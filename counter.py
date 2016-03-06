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
    
    c5 = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","5","/home/pi/Photobooth/test/5.png"])
    
    time.sleep(1)
    c5.terminate()
    
    c4 = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","5","/home/pi/Photobooth/test/4.png"])
    
    time.sleep(1)
    c4.terminate()

    c3 = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","5","/home/pi/Photobooth/test/3.png"])
    
    time.sleep(1)
    c3.terminate()
    
    c2 = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","5","/home/pi/Photobooth/test/2.png"])
    
    time.sleep(1)
    c2.terminate()
    
    c1 = subprocess.Popen(["/home/pi/raspidmx/pngview/./pngview","-b","0","-l","5","/home/pi/Photobooth/test/1.png"])
    
    time.sleep(1)
    c1.terminate()
    
    time.sleep(5)
    
    camera.stop_preview()
    p.terminate()
    
finally:
    camera.close()