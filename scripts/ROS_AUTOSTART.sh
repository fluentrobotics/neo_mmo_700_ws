#! /usr/bin/env bash

set -o errexit

workspace_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

source "$workspace_root/install/setup.bash"

ros2 launch neo_mpo_700-2 bringup.launch.py \
    imu_enable:=False \
    d435_enale:=False \
    disable_scanners:=True \
    arm_type:=ur10e \
    use_ur_dc:=True \
    ur_calibration_file:="$workspace_root/config/ur_calibration_20255201255.yaml" \
    gripper_type:=vg10 \
    initial_controller_arm:=scaled_joint_trajectory_controller \
    robot_ip:="192.168.100.102" \
    reverse_ip:="192.168.100.10" \
    direct_ur_connection:=False
