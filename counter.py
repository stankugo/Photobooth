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
    p = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","3","/home/pi/Photobooth/cards/26.png"])
    
    time.sleep(5)
    
    c = subprocess.Popen(["/home/pi/raspidmx/spriteview/./spriteview","-b","0","-c","5","-l","5","-m","1000000","-i","0","/home/pi/Photobooth/counter/counter.png"])
    
    time.sleep(10)
    
    camera.stop_preview()
    p.terminate()
    
finally:
    camera.close()