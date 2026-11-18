import time

from safe_face_controller import SafeFaceController


def main() -> None:
    controller = SafeFaceController()
    controller.start()

    try:
        while True:
            controller.set_target_angles({0: 85, 1: 125})
            time.sleep(0.5)
            controller.set_target_angles({0: 115, 1: 95})
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping SafeFaceController...")
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
