#! /usr/bin/env python3

"""
This is an internal tool generated with Codex assistance and was not originally
intended to be modified by hand.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple, Type

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from ur_dashboard_msgs.msg import RobotMode, SafetyMode
from ur_dashboard_msgs.srv import (
    GetLoadedProgram,
    GetProgramState,
    GetRobotMode,
    GetSafetyMode,
    IsProgramRunning,
    Load,
)

ROBOT_MODE_NAME_BY_VALUE = {
    value: name
    for name, value in vars(RobotMode).items()
    if name.isupper() and isinstance(value, int)
}
SAFETY_MODE_NAME_BY_VALUE = {
    value: name
    for name, value in vars(SafetyMode).items()
    if name.isupper() and isinstance(value, int)
}


class URDashboardStartup:
    def __init__(
        self,
        node: Node,
        target_program: str,
        service_timeout_s: float,
        wait_for_service_timeout_s: float,
    ) -> None:
        self._node = node
        self._target_program = target_program
        self._service_timeout_s = service_timeout_s
        self._wait_for_service_timeout_s = wait_for_service_timeout_s
        self._clients: Dict[Tuple[str, Type[Any]], Any] = {}

    def run(self) -> None:
        self._node.get_logger().info(
            f"Starting UR dashboard launch sequence for program '{self._target_program}'"
        )

        safety_mode_resp = self._call_with_success(
            "/dashboard_client/get_safety_mode",
            GetSafetyMode,
            GetSafetyMode.Request(),
        )
        safety_mode = safety_mode_resp.safety_mode.mode
        if safety_mode != SafetyMode.NORMAL:
            safety_mode_name = SAFETY_MODE_NAME_BY_VALUE.get(
                safety_mode, f"UNKNOWN({safety_mode})"
            )
            raise RuntimeError(
                f"Safety mode is {safety_mode_name}; expected NORMAL. Aborting startup."
            )

        running_resp = self._call_with_success(
            "/dashboard_client/program_running",
            IsProgramRunning,
            IsProgramRunning.Request(),
        )
        if running_resp.program_running:
            self._node.get_logger().info("Program already running.")
            return

        robot_mode_resp = self._call_with_success(
            "/dashboard_client/get_robot_mode",
            GetRobotMode,
            GetRobotMode.Request(),
        )
        robot_mode = robot_mode_resp.robot_mode.mode
        robot_mode_name = ROBOT_MODE_NAME_BY_VALUE.get(
            robot_mode, f"UNKNOWN({robot_mode})"
        )
        if robot_mode == RobotMode.POWER_OFF:
            self._call_trigger("/dashboard_client/power_on")
        elif robot_mode in (RobotMode.POWER_ON, RobotMode.IDLE, RobotMode.RUNNING):
            self._node.get_logger().info(
                f"Robot mode is {robot_mode_name}; skipping /dashboard_client/power_on"
            )
        else:
            raise RuntimeError(
                "Unsupported robot mode for startup: "
                f"{robot_mode_name}. Expected POWER_OFF, POWER_ON, IDLE, or RUNNING."
            )

        program_state_resp = self._call_with_success(
            "/dashboard_client/program_state",
            GetProgramState,
            GetProgramState.Request(),
        )
        loaded_program = program_state_resp.program_name.strip()

        if not loaded_program:
            loaded_program_resp = self._call_with_success(
                "/dashboard_client/get_loaded_program",
                GetLoadedProgram,
                GetLoadedProgram.Request(),
            )
            loaded_program = loaded_program_resp.program_name.strip()

        target_basename = Path(self._target_program).name
        loaded_basename = Path(loaded_program).name if loaded_program else ""
        if loaded_basename == target_basename:
            self._node.get_logger().info(
                f"Program already loaded ('{loaded_program}'); skipping /dashboard_client/load_program"
            )
        else:
            load_req = Load.Request()
            load_req.filename = self._target_program
            self._call_with_success("/dashboard_client/load_program", Load, load_req)

        self._call_trigger("/dashboard_client/brake_release")
        self._call_trigger("/dashboard_client/play")

        self._node.get_logger().info("UR dashboard launch sequence completed")

    def _call_trigger(self, service_name: str) -> Trigger.Response:
        response = self._call_service(service_name, Trigger, Trigger.Request())
        if not response.success:
            message = response.message or "(no message)"
            raise RuntimeError(f"{service_name} returned success=false: {message}")
        return response

    def _call_with_success(
        self, service_name: str, srv_type: Type[Any], request: Any
    ) -> Any:
        response = self._call_service(service_name, srv_type, request)
        success = getattr(response, "success", None)
        if success is not True:
            answer = getattr(response, "answer", "") or "(no answer)"
            raise RuntimeError(f"{service_name} returned success=false: {answer}")
        return response

    def _call_service(
        self, service_name: str, srv_type: Type[Any], request: Any
    ) -> Any:
        client = self._get_client(service_name, srv_type)

        if not client.wait_for_service(timeout_sec=self._wait_for_service_timeout_s):
            raise RuntimeError(
                f"Service {service_name} not available within {self._wait_for_service_timeout_s:.1f}s"
            )

        self._node.get_logger().info(f"Calling {service_name}")
        future = client.call_async(request)
        rclpy.spin_until_future_complete(
            self._node, future, timeout_sec=self._service_timeout_s
        )

        if not future.done():
            raise RuntimeError(
                f"Timed out after {self._service_timeout_s:.1f}s while calling {service_name}"
            )

        exc = future.exception()
        if exc is not None:
            raise RuntimeError(f"Service call failed for {service_name}: {exc}")

        response = future.result()
        if response is None:
            raise RuntimeError(f"Service call for {service_name} returned no response")

        return response

    def _get_client(self, service_name: str, srv_type: Type[Any]) -> Any:
        key = (service_name, srv_type)
        client = self._clients.get(key)
        if client is None:
            client = self._node.create_client(srv_type, service_name)
            self._clients[key] = client
        return client


def parse_args(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="UR dashboard startup sequence with status checks and robust error handling.",
    )
    parser.add_argument(
        "--target-program",
        default=os.getenv("UR_TARGET_PROGRAM", "neobotix.urp"),
        help="Program path/name to ensure loaded before play (default: %(default)s)",
    )
    parser.add_argument(
        "--service-timeout",
        type=float,
        default=float(os.getenv("UR_SERVICE_TIMEOUT_SECONDS", "10")),
        help="Per-call response timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--wait-for-service-timeout",
        type=float,
        default=float(os.getenv("UR_WAIT_FOR_SERVICE_SECONDS", "5")),
        help="Per-call service availability wait timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--node-name",
        default="ur_dashboard_startup",
        help="ROS node name (default: %(default)s)",
    )
    return parser.parse_known_args(argv)


def main(argv: list[str]) -> int:
    args, ros_args = parse_args(argv)
    rclpy.init(args=ros_args)
    node = rclpy.create_node(args.node_name)
    try:
        startup = URDashboardStartup(
            node=node,
            target_program=args.target_program,
            service_timeout_s=args.service_timeout,
            wait_for_service_timeout_s=args.wait_for_service_timeout,
        )
        startup.run()
        return 0
    except RuntimeError as exc:
        node.get_logger().error(str(exc))
        return 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
