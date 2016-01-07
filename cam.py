import time
import picamera
import os

camera = picamera.PiCamera()
try:
    camera.start_preview()
    os.system("~/raspidmx/pngview/./pngview -b 0 -l 3 ~/Photobooth/cards/26.png")
    
    time.sleep(30)
    camera.stop_preview()
finally:
    camera.close()
    os.system("killall pngview")