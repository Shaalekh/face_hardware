from __future__ import annotations
import os
import argparse
import sys
from typing import Iterable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .config import DEFAULT_LIMITS, DEFAULT_NEUTRAL_ANGLES
from .controller import SafeFaceController
from .servo_driver import ServoDriver

os.environ["BLINKA_SKIP_DEPENDENCY_CHECK"] = "1"

def configured_channels() -> list[int]:
    channels = set(DEFAULT_LIMITS)
    channels.update(DEFAULT_NEUTRAL_ANGLES)
    return sorted(channels)


class JointMoverWindow(QWidget):
    def __init__(self, controller: SafeFaceController) -> None:
        super().__init__()
        self.controller = controller
        self.sliders: dict[int, QSlider] = {}
        self.spinboxes: dict[int, QSpinBox] = {}

        self.setWindowTitle("Servo Joint Mover")
        self.resize(640, 480)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        joint_widget = QWidget()
        joint_layout = QGridLayout(joint_widget)
        joint_layout.setColumnStretch(1, 1)

        channels = configured_channels()
        if not channels:
            joint_layout.addWidget(QLabel("No joints configured in config.py"), 0, 0)

        for row, channel in enumerate(channels):
            min_limit, max_limit = DEFAULT_LIMITS.get(channel, (0.0, 180.0))
            neutral = float(DEFAULT_NEUTRAL_ANGLES.get(channel, 90.0))
            neutral = max(0.0, min(180.0, neutral))

            name = QLabel(f"Joint {channel}")
            name.setMinimumWidth(90)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 180)
            slider.setValue(round(neutral))

            spinbox = QSpinBox()
            spinbox.setRange(0, 180)
            spinbox.setValue(round(neutral))
            spinbox.setSuffix(" deg")

            limits = QLabel(f"{int(min_limit)}-{int(max_limit)} deg")
            limits.setMinimumWidth(90)

            joint_layout.addWidget(name, row, 0)
            joint_layout.addWidget(slider, row, 1)
            joint_layout.addWidget(spinbox, row, 2)
            joint_layout.addWidget(limits, row, 3)

            slider.valueChanged.connect(
                lambda value, ch=channel: self._set_angle(ch, value)
            )
            spinbox.valueChanged.connect(
                lambda value, ch=channel: self._set_angle(ch, value)
            )
            self.sliders[channel] = slider
            self.spinboxes[channel] = spinbox

        joint_layout.setRowStretch(len(channels), 1)
        scroll.setWidget(joint_widget)
        root_layout.addWidget(scroll)

        reset_button = QPushButton("Reset to Neutral")
        reset_button.clicked.connect(self.reset_all)
        root_layout.addWidget(reset_button)

        initial_angles = {
            channel: float(DEFAULT_NEUTRAL_ANGLES.get(channel, 90.0))
            for channel in channels
        }
        self.controller.set_target_angles(initial_angles)

    def _set_angle(self, channel: int, angle: int) -> None:
        actual = int(round(self.controller.set_target_angle(channel, float(angle))))
        slider = self.sliders[channel]
        spinbox = self.spinboxes[channel]

        slider.blockSignals(True)
        spinbox.blockSignals(True)
        slider.setValue(actual)
        spinbox.setValue(actual)
        slider.blockSignals(False)
        spinbox.blockSignals(False)

    def reset_all(self) -> None:
        neutral_angles = {
            channel: float(DEFAULT_NEUTRAL_ANGLES.get(channel, 90.0))
            for channel in configured_channels()
        }
        clamped = self.controller.set_target_angles(neutral_angles)
        for channel, angle in clamped.items():
            actual = int(round(angle))
            slider = self.sliders[channel]
            spinbox = self.spinboxes[channel]
            slider.blockSignals(True)
            spinbox.blockSignals(True)
            slider.setValue(actual)
            spinbox.setValue(actual)
            slider.blockSignals(False)
            spinbox.blockSignals(False)

    def closeEvent(self, event) -> None:
        self.controller.stop()
        super().closeEvent(event)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PyQt servo joint mover")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="use a software servo driver instead of Raspberry Pi hardware",
    )
    return parser


def main(args: Iterable[str] | None = None) -> int:
    parsed = build_arg_parser().parse_args(list(args) if args is not None else None)

    app = QApplication(sys.argv)
    if parsed.mock:
        driver: ServoDriver = ServoDriver(use_mock=True)
    else:
        driver = ServoDriver()

    controller = SafeFaceController(
        driver=driver,
        watchdog_timeout=float("inf"),
    )
    controller.start()

    window = JointMoverWindow(controller)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
