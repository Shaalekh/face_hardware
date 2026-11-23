import time

from safe_face_controller import SafeFaceController
from safe_face_controller.servo_driver import ServoDriver
import safe_face_controller.servo_driver as servo_driver_module
from safe_face_controller.joint_mover import configured_channels
from safe_face_controller.config import DEFAULT_NEUTRAL_ANGLES


class MockDriver(ServoDriver):
    def __init__(self):
        super().__init__(use_mock=True)


def test_safe_target_angles_are_clamped():
    controller = SafeFaceController(
        limits={0: (30, 110), 1: (45, 135)},
        driver=MockDriver(),
    )

    controller.set_target_angles({0: 200, 1: 10})

    assert controller.target_angles[0] == 110
    assert controller.target_angles[1] == 45


def test_watchdog_returns_to_neutral():
    driver = MockDriver()
    controller = SafeFaceController(driver=driver)
    controller.set_target_angles({0: 110, 1: 120})

    controller._last_update = time.monotonic() - 1.0
    controller._update_once()

    assert controller.current_angles[0] < 110
    assert controller.current_angles[1] < 120


def test_controller_starts_and_stops_cleanly():
    controller = SafeFaceController(driver=MockDriver())
    controller.start()
    time.sleep(0.05)
    controller.set_target_angles({0: 100, 1: 60})
    time.sleep(0.05)
    controller.stop()

    assert controller._thread is not None
    assert not controller._thread.is_alive()


def test_joint_mover_uses_all_configured_channels():
    assert configured_channels() == list(range(16))


def test_joint_mover_controller_keeps_target_after_watchdog_window():
    controller = SafeFaceController(
        driver=MockDriver(),
        watchdog_timeout=float("inf"),
    )
    controller.set_target_angles({0: 115, 1: 120})

    controller._last_update = time.monotonic() - 1.0
    controller._update_once()

    assert controller.target_angles[0] == 110
    assert controller.target_angles[1] == 120


def test_controller_uses_hardware_driver_when_available(monkeypatch):
    class FakeServo:
        angle = None

    class FakeServoKit:
        def __init__(self, channels):
            self.servo = [FakeServo() for _ in range(channels)]

    monkeypatch.setattr(servo_driver_module, "ServoKit", FakeServoKit)

    controller = SafeFaceController()

    assert not controller.driver.use_mock
    assert controller.driver.kit.servo[0].angle == DEFAULT_NEUTRAL_ANGLES[0]
