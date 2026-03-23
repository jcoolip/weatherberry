from picamera2 import Picamera2
import time
from datetime import datetime

def capture():
	try:
		now = datetime.now()
		cam = Picamera2()

		cam_config = cam.create_still_configuration(main={"size": (1920,1080)}, buffer_count=1)
		cam.configure(cam_config)

		cam.start()

		time.sleep(2)

		cam.capture_file(f"./data/images/{now}.jpg")
		cam.stop()
		print(f"saved as ./data/images/{now}.jpg")
	except Exception as e:
		print(f"error: {e}")
