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
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'image' : 10,
    'random' : 0,
    'port' : '/dev/ttyUSB0',
    'sensor' : 0,
    'counter' : 0
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
        'x' : 240,
        'y' : -70
    },
    13: {
        'x' : 258,
        'y' : -43
    },
    14: {
        'x' : 199,
        'y' : -39
    },
    15: {
        'x' : 262,
        'y' : -30
    },
    19: {
        'x' : 210,
        'y' : -36
    },
    20: {
        'x' : 268,
        'y' : 9
    },
    25: {
        'x' : 228,
        'y' : -82
    },
    26: {
        'x' : 236,
        'y' : -60
    },
    28: {
        'x' : 197,
        'y' : -45
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

    print 'image: ', misc['image']

    if overlay != None:
        overlay.terminate()
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','-x','0','-y','0','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])

    print 'camera preview'

    print 'x no: ', pos[misc['images'][misc['image']]]['x']
    print 'x of: ', pos[misc['images'][misc['image']]]['x'] - 80

    print 'y no: ', pos[misc['images'][misc['image']]]['y']
    print 'y of: ', pos[misc['images'][misc['image']]]['y'] + 10

    camera.preview_window = (pos[misc['images'][misc['image']]]['x'] - 80,pos[misc['images'][misc['image']]]['y'] + 10,(pos[misc['images'][misc['image']]]['x'] + misc['width'] - 80),(pos[misc['images'][misc['image']]]['y'] + misc['height'] + 10))
    camera.start_preview()

    time.sleep(5)
    
finally:
    overlay.terminate()
    camera.close()
