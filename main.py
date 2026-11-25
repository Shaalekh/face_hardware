import os
import time

os.environ["BLINKA_SKIP_DEPENDENCY_CHECK"] = "1"

from safe_face_controller import SafeFaceController


def main() -> None:
    controller = SafeFaceController(watchdog_timeout=float("inf"))
    controller.start()

    try:
        while True:
            # open eyes
            controller.set_target_angles({4: 80, 5: 100, 8: 120, 9: 70})
            time.sleep(3.0)
            # close eyes
            controller.set_target_angles({4: 110, 5: 70, 8: 85, 9: 100})
            time.sleep(0.1)
            # open eyes
            controller.set_target_angles({4: 80, 5: 100, 8: 120, 9: 70})
            time.sleep(0.1)
            # close eyes
            controller.set_target_angles({4: 110, 5: 70, 8: 85, 9: 100})
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping SafeFaceController...")
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
