#! /usr/bin/env bash

set -o errexit

workspace_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

source "$workspace_root/install/setup.bash"

ros2 launch "$workspace_root/launch/laptop.launch.yaml" \
    ur_calibration_file:="$workspace_root/config/ur_calibration_20255201255.yaml"
