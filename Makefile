.PHONY: all clean check-relayboard-service

# ANSI escape codes
YELLOW  := \033[1;33m
RED     := \033[1;31m
GREEN   := \033[1;32m
RESET   := \033[0m

# TODO: should we just remove some of these submodules from the workspace?
all: check-relayboard-service
	AMENT_PREFIX_PATH= CMAKE_PREFIX_PATH= COLCON_PREFIX_PATH= . /opt/ros/jazzy/setup.sh && \
	MAKEFLAGS= colcon build \
		--symlink-install \
		--packages-skip \
			mocap_optitrack_inv_kin \
			mocap_optitrack_w2b \
		--cmake-args \
			-DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
			-DCMAKE_BUILD_TYPE=Release \
			-DCMAKE_C_COMPILER=clang \
			-DCMAKE_CXX_COMPILER=clang++
	@echo "\n$(YELLOW)⚠ Remember to source install/setup.zsh$(RESET)\n"

clean:
	rm -rf build/ install/ log/

check-relayboard-service:
	@case "$$(hostname -s)" in mmo-700*) \
		systemctl cat neo-relayboard.service >/dev/null 2>&1 || { \
			echo "$(RED)[ERROR] neo-relayboard.service not installed. Follow the setup instructions in the README.$(RESET)"; \
			exit 1; \
		};; \
	esac
