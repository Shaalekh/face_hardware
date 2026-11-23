# SafeFaceController

A Raspberry Pi 5 project for safely controlling face servos with a continuously running, non-blocking control loop.

## Features

- Safe per-channel angle limits
- Smooth incremental stepping toward target poses
- Background servo update thread
- Watchdog fallback to a safe neutral pose
- Small hardware abstraction for `ServoKit`

## Setup

From the project directory, create a virtual environment with access to system packages for PyQt5:

```bash
cd /home/shaalekh/face_hardware
/usr/bin/python3 -m venv --system-site-packages .env
source .env/bin/activate
python -m pip install -e . pytest
```

On Debian/Raspberry Pi OS, install PyQt5 before creating the environment if it is not already available:

```bash
sudo apt-get update
sudo apt-get install -y python3-pyqt5 python3-dev libgpiod-dev
python -m pip install 'Adafruit-Blinka-Raspberry-Pi-PWM>=1.0.2' Adafruit-Blinka-Raspberry-Pi5-Neopixel
```

## Run the demo

Hardware mode requires a Raspberry Pi with I2C enabled and a compatible PCA9685 servo board:

```bash
python main.py
```

## Run the PyQt joint mover

Hardware mode:

```bash
python -m safe_face_controller.joint_mover
```

For a desktop or test run without Raspberry Pi hardware, use mock mode:

```bash
python -m safe_face_controller.joint_mover --mock
```

## Run tests

```bash
python -m pytest -q
```

Every channel listed in `DEFAULT_LIMITS` or `DEFAULT_NEUTRAL_ANGLES` appears as
a joint with a 0-180 degree slider. A channel with no neutral angle defaults to
90 degrees. Per-channel safety limits from `config.py` are still applied.

## Wiring notes

- Use a dedicated 5V power supply for the servos
- Connect grounds together between the Pi and the servo controller
- Prefer a PCA9685/I2C servo board or other supported PWM board for stable output
- Validate channel mappings before mounting the hardware

## Example usage

```python
from safe_face_controller import SafeFaceController

controller = SafeFaceController()
controller.start()

controller.set_target_angles({0: 100, 1: 50})

try:
    while True:
        controller.set_target_angles({0: 90, 1: 90})
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    controller.stop()
```
