# Neobotix MMO-700 ROS 2 Workspace

## Cloning

You need a GitHub SSH key as some submodules are declared as SSH urls.

Use `git clone --recursive`.

If you somehow skipped over the previous line but came back here, you can run `git submodule update --init --recursive`.

## Building

Run `make` from the workspace root.

### Robot-Specific First-Time Setup

Builds on the robot depend on [neo-relayboard.service](src/neo_mpo_700-2/configs/relayboard_v2/neo-relayboard.service) being installed to `/etc/systemd/system/`.
This service [launches](src/neo_mpo_700-2/configs/relayboard_v2/relayboard_v2.launch.py) the [RelayBoard](src/neo_relayboard_v2-2) at boot so that battery information is available even if the robot drivers are not running.
Run the following on the robot from the workspace root.
Do not run this on workstations.

```shell
sudo ln -sfn \
  "$(realpath src/neo_mpo_700-2/configs/relayboard_v2/neo-relayboard.service)" \
  /etc/systemd/system/neo-relayboard.service
```

Then, rerun `make` from the workspace root.
After that, run

```shell
sudo systemctl daemon-reload
sudo systemctl enable --now neo-relayboard.service
```

The service will run automatically on subsequent boots. You can check the status formally by running

```shell
systemctl status neo-relayboard.service
journalctl -u neo-relayboard.service -f
```

or informally by running

```shell
ros2 topic echo --once /battery_state
```

The service transitively depends on a dotfile config `$HOME/dotfiles/ros2env.sh` which sets the `ROS_DOMAIN_ID`.
