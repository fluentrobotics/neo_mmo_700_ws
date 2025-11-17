.PHONY: all clean

# ANSI escape codes
YELLOW  := \033[1;33m
RED     := \033[1;31m
GREEN   := \033[1;32m
RESET   := \033[0m

all:
	AMENT_PREFIX_PATH= CMAKE_PREFIX_PATH= COLCON_PREFIX_PATH= . /opt/ros/jazzy/setup.sh && \
	MAKEFLAGS= colcon build --symlink-install --packages-skip cartesian_controller_simulation cartesian_controller_tests

	@echo "\n$(YELLOW)⚠ Remember to source install/setup.zsh$(RESET)\n"

clean:
	rm -rf build/ install/ log/
