#! /usr/bin/env bash

set -o errexit

source install/setup.bash

ros2 launch neo_mpo_700-2 bringup.launch.py \
    imu_enable:=False \
    d435_enale:=False \
    disable_scanners:=True \
    arm_type:=ur10e \
    use_ur_dc:=True \
    gripper_type:=vg10 \
    initial_controller_arm:=scaled_joint_trajectory_controller \
    robot_ip:="192.168.100.102" \
    reverse_ip:="192.168.100.10" \
    direct_ur_connection:=False
