# SafeFaceController

A Raspberry Pi 5 project for safely controlling face servos with a continuously running, non-blocking control loop.

## Features

- Safe per-channel angle limits
- Smooth incremental stepping toward target poses
- Background servo update thread
- Watchdog fallback to a safe neutral pose
- Small hardware abstraction for `ServoKit`

## Installation

```bash
cd /home/shaalekh/Documents/face_hardware
python3 -m pip install -e .
```

## Run the demo

```bash
python3 main.py
```

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
