#
#
#
#
#
# IMPORTS
#
#
#
#
#

import sys, traceback, os
import time

import subprocess
import Queue, threading
import random
import math

import urllib2
import httplib

from time import sleep
from time import strftime
from datetime import datetime

#
#
#
#
#
#   DECLARATIONS
#
#
#
#
#

api = {
	'protocol' : 'http://',
	'url' : 'mhq-verspielt.de',
	'header' : {'user-agent': 'raspberry-pi/photobooth'}
}

ready = {
	'setup' : False,
	'snapshot' : False
}

misc = {
	'snapshots' : '/home/pi/Photobooth/snapshots/',
    'compositions' : '/home/pi/Photobooth/compositions/',
    'cards' : '/home/pi/Photobooth/cards/',
    'raster' : '/home/pi/Photobooth/raster/',
    'ext' : '.png',
    'width' : 367,
    'height' : 490,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
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

#
#
#
#
#
#   DEFINITIONS
#
#
#
#
#

def cleanupAndExit():
	print 'EXIT'

def setup():
    global ready
    global misc
    
    # CREATE A RANDOM NUMBER
    while (misc['image'] == misc['random']):
        misc['random'] = random.randrange(0,len(misc['images'])-1,1)
        
    misc['image'] = misc['random']
    print 'image: ', misc['image']
    print 'image: ', misc['images'][misc['image']]
    
    print 'preview x0: ', pos[misc['images'][misc['image']]]['x']
    print 'preview y0: ', pos[misc['images'][misc['image']]]['y']
    
    print 'preview x1: ', pos[misc['images'][misc['image']]]['x'] + misc['width']
    print 'preview y1: ', pos[misc['images'][misc['image']]]['y'] + misc['height']
	
    ready['setup'] = True

def snapshot(image):
    
    global misc
    
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    image = 'asdf'
    
    tUpload = threading.Thread(name='upload', target=upload, args=(filename,image,))
    tUpload.daemon = True
    tUpload.start()

def upload(filename,image):

    print filename
    print image
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
 
#
#
#
#
#
#   MAIN LOOP
#
#
#
#
#       

try:
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
    
    while True:
        print ' '
        print ' '
        print ' '
        print ' '
        print 'ready: ', ready['setup']
        
        if ready['setup'] == True:

            ready['setup'] = False
            tSnapshot = threading.Thread(name='snapshot', target=snapshot, args=(misc['images'][misc['image']],))
            tSnapshot.daemon = True
            tSnapshot.start()
        
        sleep(5)
        
except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
sys.exit(0)