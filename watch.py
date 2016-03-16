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
from maxbotix import USB_ProxSonar

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
	'url' : 'fotobox.local',
	'header' : {'user-agent': 'raspberry-pi/photobooth'}
}

ready = {
	'setup' : False,
	'timestamp' : 0
}

misc = {
	'snapshots' : '/Users/stephan/GIT/Photobooth/snapshots/',
    'compositions' : '/Users/stephan/GIT/Photobooth/compositions/',
    'cards' : '/Users/stephan/GIT/Photobooth/cards/',
    'raster' : '/Users/stephan/GIT/Photobooth/raster/',
    'ext' : '.png',
    'width' : 367,
    'height' : 490,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0',
    'sensor' : 0
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
    sensor.stop()

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
    ready['timestamp'] = int(time.time())

def snapshot(image):
    
    global misc
    
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    filename = '20160314-201800'
    
    image = 2
    
    tPrepare = threading.Thread(name='prepare', target=prepare, args=(filename,image,))
    tPrepare.daemon = True
    tPrepare.start()
    
def prepare(filename,image):
    
    url = api['protocol'] + api['url'] + '/prepare'

def upload(id,hashid,filename,image):
    
    print 'UPLOAD: ', id, ', ', hashid, ', ', image
    
    url = api['protocol'] + api['url'] + '/upload'
    files = {'file': open(misc['compositions'] + filename + misc['ext'], 'rb')}
    data = {'id': id, 'hashid': hashid, 'image': image}
        
def plot(hashid,image):
    
    print 'PLOT: ', hashid, ', ', image
    
def watchdog():
    
    while True:
        sleep(60)
        print ready['timestamp']
        print int(time.time())
        
        if ( int(time.time()) - ready['timestamp'] ) > ( 60 * 5 ):
            print 're-setup'
            tSetup = threading.Thread(name='setup', target=setup)
            tSetup.daemon = True
            tSetup.start()
            
            
class MySensor(USB_ProxSonar):

    def __init__(self, port):

        USB_ProxSonar.__init__(self, port)

    def handleUpdate(self, distanceMillimeters):

        # print('%d mm' % distanceMillimeters)
        misc['sensor'] = distanceMillimeters
 
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
    
    tWatchdog = threading.Thread(name='watchdog', target=watchdog)
    tWatchdog.daemon = True
    tWatchdog.start()
    
    sensor = MySensor(misc['port'])
    sensor.start()
    
    while True:
        
        if ready['setup'] == True:

            ready['setup'] = False
            tSnapshot = threading.Thread(name='snapshot', target=snapshot, args=(misc['images'][misc['image']],))
            tSnapshot.daemon = True
            tSnapshot.start()
        
        sleep(5)
        print ' '
        print ' '
        print ' '
        print ' '
        print 'ready: ', ready['setup']
        print 'sensor: ', misc['sensor']
        
except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
sys.exit(0)