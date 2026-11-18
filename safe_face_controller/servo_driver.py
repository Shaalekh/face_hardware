from __future__ import annotations

from typing import Dict, Optional

try:
    from adafruit_servokit import ServoKit
except ImportError:  # pragma: no cover - used in tests and non-hardware environments
    ServoKit = None


class ServoDriver:
    """Small hardware abstraction around the servo controller."""

    def __init__(self, channels: int = 16, *, use_mock: bool = False):
        self.channels = channels
        self.use_mock = use_mock
        self._angles: Dict[int, float] = {}

        if not self.use_mock:
            if ServoKit is None:
                raise RuntimeError(
                    "ServoKit hardware support is unavailable. Install "
                    "adafruit-circuitpython-servokit and run on a Raspberry Pi "
                    "with I2C enabled."
                )
            self.kit = ServoKit(channels=self.channels)

    def set_angle(self, channel: int, angle: float) -> None:
        if self.use_mock:
            self._angles[channel] = angle
            return

        self.kit.servo[channel].angle = angle
        self._angles[channel] = angle

    def set_all_safe(self, safe_angles: Dict[int, float]) -> None:
        for channel, angle in safe_angles.items():
            self.set_angle(channel, angle)

    @property
    def angles(self) -> Dict[int, float]:
        return dict(self._angles)
