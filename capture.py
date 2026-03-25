import time
from datetime import datetime

from picamera2 import Picamera2

hour = datetime.now().hour

## if night time
if hour < 6 or hour >= 18:
    night = True
    print("night")
else:
    night = False
    print("day")


def capture():
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    try:
        cam = Picamera2()

        ## if night time
        if night:
            cam_config = cam.create_still_configuration(
                main={"size": (1920, 1080)},
                controls={
                    "AeEnable": False,
                    "ExposureTime": 2000000,
                    "AnalogueGain": 8.0,
                    "AwbEnable": True,
                    "NoiseReductionMode": 2,
                },
            )
        else:
            cam_config = cam.create_still_configuration(
                main={"size": (1920, 1080)}, buffer_count=1
            )

        cam.configure(cam_config)

        cam.start()

        time.sleep(5)

        cam.capture_file(f"./data/images/{now}.jpg")
        cam.stop()
        print(f"saved as ./data/images/{now}.jpg")
    except Exception as e:
        print(f"error: {e}")
