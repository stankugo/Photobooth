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
import os
import signal
import serial, time
import requests
import subprocess
import Queue, threading
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
    'url' : 'mhq-verspielt.de',
    'header' : {'user-agent': 'raspberry-pi/photobooth'}
}

ready = {
    'setup' : False,
    'timestamp' : 0,
    'upload' : True,
    'print' : True,
    'capture' : 0
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

live = {
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
reboot = None

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
    print 'SHUTDOWN'
    camera.close()
    sensor.stop()
    
    if overlay != None:
        # overlay.terminate()
        os.kill(overlay.pid, signal.SIGTERM)
        time.sleep(2)
        if overlay.poll() is None:
            time.sleep(3)
            os.kill(overlay.pid, signal.SIGKILL)

    if merci != None:
        # merci.terminate()
        os.kill(merci.pid, signal.SIGTERM)
        time.sleep(2)
        if merci.poll() is None:
            time.sleep(3)
            os.kill(merci.pid, signal.SIGKILL)

    print 'EXIT'
    
def setup():
    global ready
    global overlay
    global merci
    global misc
    global pos
    global live
    
    # CREATE A RANDOM NUMBER
    while (misc['image'] == misc['random']):
        misc['random'] = random.randrange(0,len(misc['images'])-1,1)
        
    misc['image'] = misc['random']
    print 'image: ', misc['image']

    if overlay != None:
        # overlay.terminate()
        os.kill(overlay.pid, signal.SIGTERM)
        print 'overlay: kill'
        time.sleep(2)
        if overlay.poll() is None:
            time.sleep(3)
            os.kill(overlay.pid, signal.SIGKILL)
            print 'overlay: forcekill'
            
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','-x','0','-y','0','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])
    
    print 'overlay: done'
    sleep(2)
    
    camera.stop_preview()
    print 'camera stop preview (setup): done'
    sleep(2)
    
    camera.preview_window = (live[misc['images'][misc['image']]]['x'] - 80,live[misc['images'][misc['image']]]['y'] + 10,(live[misc['images'][misc['image']]]['x'] + misc['width'] - 80),(live[misc['images'][misc['image']]]['y'] + misc['height'] + 10))
    camera.start_preview()

    print 'camera start preview (setup): done'
    sleep(2)

    if merci != None:
        # merci.terminate()
        os.kill(merci.pid, signal.SIGTERM)
        print 'merci: kill'
        time.sleep(2)
        if merci.poll() is None:
            time.sleep(3)
            os.kill(merci.pid, signal.SIGKILL)
            print 'merci: forcekill'
        
    print 'merci: done'
    
    ready['setup'] = True
    ready['timestamp'] = int(time.time())
    
    print 'ready setup: ', ready['setup']
    print 'timestamp setup: ', ready['timestamp']

def counter():
    global misc
    
    print 'counter: start'
    counter = subprocess.Popen(['/home/pi/raspidmx/spriteview/./spriteview','-b','0','-c','5','-l','5','-m','1000000','-i','0','/home/pi/Photobooth/counter/counter.png'])
    
    countup = 0
    misc['counter'] = 0
    
    while countup < 5:
        if misc['sensor'] <= 2000 or misc['sensor'] > 3000:
            misc['counter'] += 1
        countup += 1
        sleep(1)
    
    print 'counter: done'
    print 'counter: ', misc['counter']
    
    if misc['counter'] > 3:
        print 'still occupied'
        tSnapshot = threading.Thread(name='snapshot', target=snapshot, args=(misc['image'],))
        tSnapshot.daemon = True
        tSnapshot.start()
    
    else:
        print 'abort'
        tSetup = threading.Thread(name='setup', target=setup)
        tSetup.daemon = True
        tSetup.start()

def snapshot(image):
    global ready
    global misc
    global merci
    global camera
    print 'image: ', image
    print 'real image: ', str(misc['images'][image])

    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    
    print 'filename: ', filename
    
    ready['capture'] = int(time.time())
    print 'camera: capture start'
    camera.capture(misc['snapshots'] + filename + misc['ext'], format='png')
    print 'camera: capture done'
    ready['capture'] = 0
    
    ready['upload'] = False
    ready['print'] = False
    
    print 'ready (upload): ', ready['upload']
    print 'ready (print): ', ready['print']
    
    print 'resize'
    
    # MERGING IMAGES
    resize_canvas(misc['snapshots'] + filename + misc['ext'],misc['snapshots'] + filename + misc['ext'],pos[misc['images'][image]]['x'],pos[misc['images'][image]]['y'])
    background = Image.open(misc['snapshots'] + filename + misc['ext'])
    foreground = Image.open(misc['cards'] + str(misc['images'][image]) + '.png')

    print 'merge'
    
    Image.alpha_composite(background, foreground).save(misc['compositions'] + filename + misc['ext'])
    
    print 'prepare'
    
    tPrepare = threading.Thread(name='prepare', target=prepare, args=(filename,misc['images'][image],))
    tPrepare.daemon = True
    tPrepare.start()
    
    merci = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','4','/home/pi/Photobooth/merci/merci.png'])
    sleep(10)

    print 'setup'
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()

def prepare(filename,image):
    
    url = api['protocol'] + api['url'] + '/prepare'
    
    try:
        r = requests.get(url, headers=api['header'])
        response = r.json()
        
        # CHECK FOR HASH
        if 'status' in response:
            id = response['id']
            hashid = response['hashid']
            
            # UPLOAD
            tUpload = threading.Thread(name='upload', target=upload, args=(id,hashid,filename,image,))
            tUpload.daemon = True
            tUpload.start()
            
            # PRINT 
            tPlot = threading.Thread(name='plot', target=plot, args=(hashid,image,))
            tPlot.daemon = True
            tPlot.start()
            
        del response
        
    except requests.exceptions.RequestException as e:
        print e

def upload(id,hashid,filename,image):
    
    print 'upload'
        
    url = api['protocol'] + api['url'] + '/upload'
    files = {'file': open(misc['compositions'] + filename + misc['ext'], 'rb')}
    data = {'id': id, 'hashid': hashid, 'image': image}
    
    try:
        r = requests.post(url, headers=api['header'], files=files, data=data)
        print r.text
        response = r.json()
        del response
    
    except requests.exceptions.RequestException as e:
        print e
        
def plot(hashid,image):
    print api['protocol'] + api['url'] + '/' + hashid
    p = printer.ThermalPrinter(serialport=serialport)
    
    p.linefeed()
    
    p.upsidedown()
    p.print_text(api['protocol'] + api['url'] + '/' + hashid + "\n")
    p.upsidedown(False)

    from PIL import Image, ImageDraw
    i = Image.open(misc['raster'] + str(image) + '.png')
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
    
def watchdog():
    global merci
    global ready
    
    while True:
        
        sleep(15)
        
        print ''
        print ''
        print '----------'
        print ''
        print 'current time: %s' % time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
        print 'last action:  %s' % int(time.time()) - ready['timestamp']
        print 'ultrasonic: %s' % misc['sensor']
        print 'ready (setup): %s' % ready['setup']
        print 'ready (print): %s' % ready['print']
        print 'ready (upload): %s' % ready['upload']
        print 'ready (capture): %s' % ready['capture']
        print ''
        print '----------'
        
        
        print ready['timestamp']
        print int(time.time())
        
        # if capture process takes more than a minute ---> reboot
        if ( int(time.time()) - ready['capture'] ) > ( 60 ) and ready['upload'] == True and ready['capture'] == True:
            reboot = subprocess.Popen('sudo shutdown -r -f now', stdout=PIPE, stderr=PIPE, shell=True)
        
        # if installation has been idle for 15 minutes ---> setup
        elif ( int(time.time()) - ready['timestamp'] ) > ( 60 * 15 ):
            
            print ''
            print ''
            print '=========='
            print ''
            print 're-setup'
            print ''
            print '=========='
            
            ready['setup'] = False
            
            merci = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','4','/home/pi/Photobooth/merci/hello.png'])
            sleep(2)
            
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
    
    print 'READY'
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
    
    tWatchdog = threading.Thread(name='watchdog', target=watchdog)
    tWatchdog.daemon = True
    tWatchdog.start()
    
    sensor = MySensor(misc['port'])
    sensor.start()
    
    while True:
        
        if misc['sensor'] != 0 and (misc['sensor'] <= 2000 or misc['sensor'] > 3000) and ready['setup'] == True:
            
            ready['setup'] = False
            
            tCounter = threading.Thread(name='counter', target=counter)
            tCounter.daemon = True
            tCounter.start()
        
        sleep(1)

except KeyboardInterrupt:
    cleanupAndExit()
except Exception:
    cleanupAndExit()
    traceback.print_exc(file=sys.stdout)
sys.exit(0)