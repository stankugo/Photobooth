import time
import picamera
import os
import subprocess

misc = {
	'snapshots' : '/home/pi/Photobooth/snapshots/',
    'compositions' : '/home/pi/Photobooth/compositions/',
    'cards' : '/home/pi/Photobooth/cards/',
    'raster' : '/home/pi/Photobooth/raster/',
    'ext' : '.png',
    'width' : 367,
    'height' : 490,
    'images' : [2,7,13,20],
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0'
}

pos = {
    2: {
        'x' : 241,
        'y' : 13
    },
    7: {
        'x' : 261,
        'y' : -11
    },
    8: {
        'x' : 246,
        'y' : -116
    },
    13: {
        'x' : 268,
        'y' : -53
    },
    14: {
        'x' : 179,
        'y' : -69
    },
    15: {
        'x' : 280,
        'y' : -64
    },
    19: {
        'x' : 193,
        'y' : -63
    },
    20: {
        'x' : 281,
        'y' : 10
    },
    25: {
        'x' : 223,
        'y' : -132
    },
    26: {
        'x' : 246,
        'y' : -100
    },
    28: {
        'x' : 179,
        'y' : -81
    }
}

print 'ready'

camera = picamera.PiCamera()
camera.resolution = (misc['width'], misc['height'])
camera.preview_fullscreen = False
camera.hflip = True

overlay = None

print 'try'

try:
    
    misc['image'] = misc['random']
    print 'image: ', misc['image']
    
    if overlay != None:
        overlay.terminate()
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])
    
    print 'camera preview'
    
    camera.preview_window = (pos[misc['images'][misc['image']]]['x'],pos[misc['images'][misc['image']]]['y'],(pos[misc['images'][misc['image']]]['x'] + misc['width']),(pos[misc['images'][misc['image']]]['y'] + misc['height']))
    camera.start_preview()

    time.sleep(10)
    
    print 'camera capture'
    
    camera.stop_preview()
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    camera.capture(misc['snapshots'] + filename + misc['ext'], format='png')
    
finally:
    camera.close()