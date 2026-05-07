#! /usr/bin/env bash

set -o errexit

source install/setup.bash

ros2 launch launch/laptop.launch.yaml
