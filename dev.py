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
import serial, time
import requests
import subprocess
import Queue, threading
import ultrasonic
import printer
import picamera
import random
import math

import urllib2
import httplib

from PIL import Image
from time import sleep
from time import strftime
from serial import Serial
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
    'width' : 367,
    'height' : 490,
    'images' : [2,7,8,13,14,15,19,20,25,26,28],
    'image' : -1,
    'random' : 0,
    'port' : '/dev/ttyUSB0'
}

pos = [
    {
        'x' : 244,
        'y' : 11
    },
    {
        'x' : 261,
        'y' : -19
    },
    {
        'x' : 245,
        'y' : 121
    },
    {
        'x' : 262,
        'y' : -47
    },
    {
        'x' : 186,
        'y' : 69
    },
    {
        'x' : 280,
        'y' : -63
    },
    {
        'x' : 195,
        'y' : -67
    },
    {
        'x' : 280,
        'y' : 5
    },
    {
        'x' : 227,
        'y' : -134
    },
    {
        'x' : 245,
        'y' : -101
    },
    {
        'x' : 181,
        'y' : -81
    }
]

camera = picamera.PiCamera()
camera.resolution = (misc['width'], misc['height'])
camera.preview_fullscreen = False
camera.hflip = True

if len(sys.argv) == 2:
    serialport = sys.argv[1]
else:
    serialport = printer.ThermalPrinter.SERIALPORT

if not os.path.exists(serialport):
    sys.exit("ERROR: Serial port not found at: %s" % serialport)

overlay = None
merci = None

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
    global misc
    global ready
    global overlay
    global merci
    
    # CREATE A RANDOM NUMBER
    while (misc['image'] == misc['random']):
        misc['random'] = random.randrange(0,len(misc['images'])-1,1)
      
    print 'image: ', misc['image']
    print 'add one'
    # misc['image'] = misc['random']
    misc['image'] += 1
    print 'image: ', misc['image']
	
    if merci != None:
        merci.terminate()
		
	sleep(2)
    
    if overlay != None:
        overlay.terminate()
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])
    
    camera.preview_window = (pos[misc['image']]['x'] - 80,pos[misc['image']]['y'] + 10,(pos[misc['image']]['x'] + misc['width'] - 80),(pos[misc['image']]['y'] + misc['height'] + 10))
    camera.start_preview()
    
    ready['setup'] = True

def counter():
    counter = subprocess.Popen(['/home/pi/raspidmx/spriteview/./spriteview','-b','0','-c','5','-l','5','-m','1000000','-i','0','/home/pi/Photobooth/counter/counter.png'])
    sleep(5)
    
    tSnapshot = threading.Thread(name='snapshot', target=snapshot, args=(misc['image'],))
    tSnapshot.daemon = True
    tSnapshot.start()

def snapshot(image):
    global merci
    global camera
    print 'image: ', image
    print 'real image: ', str(misc['images'][image])
    
    camera.stop_preview()
    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    camera.capture(misc['snapshots'] + filename + misc['ext'], format='png')
    
    print 'resize'
    
    # MERGING IMAGES
    resize_canvas(misc['snapshots'] + filename + misc['ext'],misc['snapshots'] + filename + misc['ext'],pos[image]['x'],pos[image]['y'])
    background = Image.open(misc['snapshots'] + filename + misc['ext'])
    foreground = Image.open(misc['cards'] + str(misc['images'][image]) + '.png')

    print 'merge'
    
    Image.alpha_composite(background, foreground).save(misc['compositions'] + filename + misc['ext'])
    
    print 'upload'
    
    tUpload = threading.Thread(name='upload', target=upload, args=(filename,image,))
    tUpload.daemon = True
    tUpload.start()
    
    merci = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','4','/home/pi/Photobooth/merci/merci.png'])
    sleep(10)

    print 'setup'
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()

def upload(filename,image):
	url = api['protocol'] + api['url'] + '/upload'
	files = {'file': open(misc['compositions'] + filename + misc['ext'], 'rb')}
	data = {'image': image}
    
	try:
		r = requests.post(url, headers=api['header'], files=files, data=data)
		response = r.json()

		# CHECK FOR HASH
		if 'status' in response:
			hashid = response['status']
            
			# PRINT 
			tPlot = threading.Thread(name='plot', target=plot, args=(hashid,image,))
			tPlot.daemon = True
			tPlot.start()
            
		del response
		
	except requests.exceptions.RequestException as e:
	    print e
        
def plot(hashid,image):
    print api['protocol'] + api['url'] + '/' + hashid
    p = printer.ThermalPrinter(serialport=serialport)
    
    p.linefeed()
    
    p.upsidedown_on()
    p.print_text(api['protocol'] + api['url'] + '/' + hashid + "\n")
    p.upsidedown_off()

    from PIL import Image, ImageDraw
    i = Image.open(misc['raster'] + str(misc['images'][image]) + '.png')
    data = list(i.getdata())
    w, h = i.size
    p.print_bitmap(data, w, h, False)
    
    p.linefeed()
    p.linefeed()
    
def resize_canvas(old_image_path, new_image_path,
                  x1=0, y1=0,
                  canvas_width=800, canvas_height=1280):

    im = Image.open(old_image_path)
    old_width, old_height = im.size

    # Center the image
    # x1 = int(math.floor((canvas_width - old_width) / 2))
    # y1 = int(math.floor((canvas_height - old_height) / 2))

    mode = im.mode
    if len(mode) == 1:  # L, 1
        new_background = (255)
    if len(mode) == 3:  # RGB
        new_background = (255, 255, 255)
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (255, 255, 255, 255)

    newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
    newImage.paste(im, (x1, y1, x1 + old_width, y1 + old_height))
    newImage.save(new_image_path)
 
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
    
    print 'READY'
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
    
    while True:

        tCounter = threading.Thread(name='counter', target=counter)
        tCounter.daemon = True
        tCounter.start()
        
        sleep(15)

except KeyboardInterrupt:
	cleanupAndExit()
except Exception:
	cleanupAndExit()
	traceback.print_exc(file=sys.stdout)
sys.exit(0)