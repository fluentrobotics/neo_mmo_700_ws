#! /usr/bin/env bash

set -o errexit

source ~/neo_mmo_700_ws/install/setup.bash
sleep 2

ros2 launch neo_mpo_700-2 bringup.launch.py \
    arm_type:=ur10e \
    robot_ip:="192.168.100.102" \
    disable_scanners:=True \
    use_imu:=False \
    use_d435:=False \
    use_ur_dc:=True \
    initial_controller_arm:=scaled_joint_trajectory_controller \
    gripper_type:=vg10
