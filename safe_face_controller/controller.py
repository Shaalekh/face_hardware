from __future__ import annotations

import threading
import time
from typing import Dict, Mapping, Optional

from .config import DEFAULT_LIMITS, DEFAULT_NEUTRAL_ANGLES
from .servo_driver import ServoDriver


class SafeFaceController:
    """Continuous, non-blocking servo controller with safe angle limits."""

    def __init__(
        self,
        limits: Optional[Mapping[int, tuple[float, float]]] = None,
        neutral_angles: Optional[Mapping[int, float]] = None,
        *,
        step_size: float = 2.0,
        update_interval: float = 0.02,
        watchdog_timeout: float = 0.5,
        driver: Optional[ServoDriver] = None,
    ) -> None:
        self.limits = dict(DEFAULT_LIMITS if limits is None else limits)
        self.neutral_angles = dict(DEFAULT_NEUTRAL_ANGLES if neutral_angles is None else neutral_angles)
        self.step_size = float(step_size)
        self.update_interval = float(update_interval)
        self.watchdog_timeout = float(watchdog_timeout)

        self.driver = driver or ServoDriver(use_mock=driver is None)

        self.current_angles = {channel: float(angle) for channel, angle in self.neutral_angles.items()}
        self.target_angles = {channel: float(angle) for channel, angle in self.current_angles.items()}

        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._last_update = time.monotonic()

        for channel, angle in self.current_angles.items():
            self.driver.set_angle(channel, angle)

    def start(self) -> "SafeFaceController":
        if self._thread and self._thread.is_alive():
            return self

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="SafeFaceControllerLoop", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

        self.set_target_angles(self.neutral_angles)
        self.driver.set_all_safe(self.current_angles)

    def set_target_angles(self, target_angles: Mapping[int, float]) -> Dict[int, float]:
        clamped = {}
        for channel, target in target_angles.items():
            clamped[channel] = self._clamp_angle(channel, float(target))

        with self._lock:
            self.target_angles.update(clamped)
            self._last_update = time.monotonic()

        return dict(clamped)

    def set_target_angle(self, channel: int, target: float) -> float:
        return self.set_target_angles({channel: target})[channel]

    def _clamp_angle(self, channel: int, angle: float) -> float:
        min_limit, max_limit = self.limits.get(channel, (0.0, 180.0))
        return max(min_limit, min(max_limit, float(angle)))

    def _get_channels(self) -> set[int]:
        channels = set(self.limits)
        channels.update(self.current_angles)
        channels.update(self.target_angles)
        channels.update(self.neutral_angles)
        return channels

    def _update_once(self) -> None:
        with self._lock:
            target_copy = dict(self.target_angles)
            current_copy = dict(self.current_angles)
            last_update = self._last_update

        now = time.monotonic()
        if now - last_update > self.watchdog_timeout:
            target_copy = {ch: self.neutral_angles.get(ch, current_copy.get(ch, 90.0)) for ch in self._get_channels()}

        final_angles: Dict[int, float] = {}
        for channel in sorted(self._get_channels()):
            current = float(current_copy.get(channel, self.neutral_angles.get(channel, 90.0)))
            target = float(target_copy.get(channel, current))
            target = self._clamp_angle(channel, target)

            if abs(target - current) <= self.step_size:
                new_angle = target
            else:
                direction = 1 if target > current else -1
                new_angle = current + (self.step_size * direction)

            final_angles[channel] = new_angle
            self.driver.set_angle(channel, new_angle)

        with self._lock:
            self.current_angles.update(final_angles)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self._update_once()
            self._stop_event.wait(self.update_interval)


__all__ = ["SafeFaceController"]
