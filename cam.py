import time
import picamera
import subprocess

camera = picamera.PiCamera()
try:
    camera.start_preview()
    subprocess.call(["~/raspidmx/pngview/./pngview", "-b 0 -l 3 ~/Photobooth/cards/26.png"])
    
    time.sleep(30)
    camera.stop_preview()
finally:
    camera.close()
    subprocess.call(["killall pngview"])