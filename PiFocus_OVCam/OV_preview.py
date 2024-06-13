import time
from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

size = (400, 640)
flim = 500
exp = 60
gain = 1.0
preview_config = picam2.create_preview_configuration(raw={'format': 'R10', 'size': size}, controls = {"FrameDurationLimits": (flim, flim), "ExposureTime": exp, "AnalogueGain": gain})
picam2.configure(preview_config)

picam2.start()
time.sleep(20)
picam2.stop()
