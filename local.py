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
import requests
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
	'action' : False,
	'snapshot' : False
}

misc = {
	'snapshots' : '/home/pi/Photobooth/snapshots/',
    'compositions' : '/home/pi/Photobooth/compositions/',
    'cards' : '/home/pi/Photobooth/cards/',
    'raster' : '/home/pi/Photobooth/raster/',
    'ext' : '.png',
    'width' : 400,
    'height' : 534,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0'
}

pos = [
    {
        'x' : 157,
        'y' : 143
    },
    {
        'x' : 157,
        'y' : 143
    }
]

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

def snapshot():
    
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    image = 'asdf'
    
    tUpload = threading.Thread(name='upload', target=upload, args=(filename,image,))
    tUpload.daemon = True
    tUpload.start()

def upload(filename,image):

    print filename
    print image
 
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
    
    while True:
        print 'READY'
        
        tSnapshot = threading.Thread(name='snapshot', target=snapshot)
        tSnapshot.daemon = True
        tSnapshot.start()
        
        sleep(30)
        
except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
sys.exit(0)