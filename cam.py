import time
import picamera
import os
import subprocess

camera = picamera.PiCamera()
try:
    camera.resolution = (1067, 800)
    camera.preview_fullscreen = False
    camera.preview_window = (0,0,1067,800)
    camera.hflip = True
    
    camera.start_preview()
    p = subprocess.Popen("/home/pi/raspidmx/pngview/./pngview -b 0 -l 3 /home/pi/Photobooth/cards/26.png")
    # os.system("/home/pi/raspidmx/pngview/./pngview -b 0 -l 3 /home/pi/Photobooth/cards/26.png")
    
    time.sleep(30)
    
    camera.stop_preview()
    p.terminate()
    
finally:
    camera.close()