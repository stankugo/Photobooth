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
from datetime import timedelta
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
    'setuptime' : 0,
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
    'images' : [2,7,8,14,15,19,20,25,26,28],
    'image' : 0,
    'random' : 0,
    'port' : '/dev/ttyUSB0',
    'sensor' : 0,
    'counter' : 0
}

pos = {
    2: {
        'x' : 241,
        'y' : 23
    },
    7: {
        'x' : 261,
        'y' : -1
    },
    8: {
        'x' : 246,
        'y' : -106
    },
    13: {
        'x' : 268,
        'y' : -43
    },
    14: {
        'x' : 179,
        'y' : -59
    },
    15: {
        'x' : 280,
        'y' : -54
    },
    19: {
        'x' : 193,
        'y' : -53
    },
    20: {
        'x' : 281,
        'y' : 20
    },
    25: {
        'x' : 223,
        'y' : -122
    },
    26: {
        'x' : 246,
        'y' : -90
    },
    28: {
        'x' : 179,
        'y' : -71
    }
}

live = {
    2: {
        'x' : 241,
        'y' : 23
    },
    7: {
        'x' : 261,
        'y' : -1
    },
    8: {
        'x' : 240,
        'y' : -60
    },
    13: {
        'x' : 258,
        'y' : -33
    },
    14: {
        'x' : 199,
        'y' : -29
    },
    15: {
        'x' : 262,
        'y' : -20
    },
    19: {
        'x' : 210,
        'y' : -26
    },
    20: {
        'x' : 268,
        'y' : 19
    },
    25: {
        'x' : 228,
        'y' : -72
    },
    26: {
        'x' : 236,
        'y' : -50
    },
    28: {
        'x' : 197,
        'y' : -35
    }
}

if len(sys.argv) == 2:
    serialport = sys.argv[1]
else:
    serialport = printer.ThermalPrinter.SERIALPORT

if not os.path.exists(serialport):
    sys.exit("ERROR: Serial port not found at: %s" % serialport)

camera = None
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
    global ready
    global overlay
    global merci
    global misc
    global pos
    global live
    global camera
    
    print 'SHUTDOWN'
    camera.close()
    sensor.stop()
    
    if overlay != None and overlay.poll() is None:
        # overlay.terminate()
        os.kill(overlay.pid, signal.SIGTERM)
        time.sleep(2)
        if overlay.poll() is None:
            time.sleep(3)
            os.kill(overlay.pid, signal.SIGKILL)

    if merci != None and merci.poll() is None:
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
    global camera
    
    # MEASURE SETUP TIME
    ready['setuptime'] = int(time.time())
    
    # CREATE A RANDOM NUMBER
    while (misc['image'] == misc['random']):
        misc['random'] = random.randrange(0,len(misc['images'])-1,1)
        
    misc['image'] = misc['random']
    print 'image: ', misc['image']

    if overlay != None and overlay.poll() is None:
        # overlay.terminate()
        os.kill(overlay.pid, signal.SIGTERM)
        print 'overlay: kill'
        time.sleep(2)
        while overlay.poll() is None:
            time.sleep(3)
            os.kill(overlay.pid, signal.SIGKILL)
            print 'overlay: forcekill'
            
    overlay = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','3','-x','0','-y','0','/home/pi/Photobooth/cards/' + str(misc['images'][misc['image']]) + '.png'])
    
    print 'overlay: done'
    sleep(2)
    
    if camera != None:
        print 'camera close (setup)'
        camera.close()
        print 'camera close (setup): done'
        sleep(5)
    
    
    print 'camera init (setup)'
    camera = picamera.PiCamera()
    camera.resolution = (misc['width'], misc['height'])
    camera.preview_fullscreen = False
    camera.hflip = True
    camera.preview_window = (live[misc['images'][misc['image']]]['x'] - 80,live[misc['images'][misc['image']]]['y'] + 10,(live[misc['images'][misc['image']]]['x'] + misc['width'] - 80),(live[misc['images'][misc['image']]]['y'] + misc['height'] + 10))
    print 'camera init (setup): done'
    
    print 'camera start preview (setup)'
    camera.start_preview()
    print 'camera start preview (setup): done'
    sleep(2)

    if merci != None and merci.poll() is None:
        # merci.terminate()
        os.kill(merci.pid, signal.SIGTERM)
        print 'merci: kill'
        time.sleep(2)
        while merci.poll() is None:
            time.sleep(3)
            os.kill(merci.pid, signal.SIGKILL)
            print 'merci: forcekill'
        
    print 'merci: done'
    
    ready['setuptime'] = 0
    ready['setup'] = True
    ready['timestamp'] = int(time.time())
    
    print 'ready setup: ', ready['setup']
    print 'timestamp setup: ', ready['timestamp']

def counter():
    global misc
    
    tStatus = threading.Thread(name='status', target=status, args=('counter',))
    tStatus.daemon = True
    tStatus.start()
    
    print 'counter: start'
    counter = subprocess.Popen(['/home/pi/raspidmx/spriteview/./spriteview','-b','0','-c','5','-l','5','-m','1000000','-i','0','/home/pi/Photobooth/counter/counter.png'])
    
    countup = 0
    misc['counter'] = 0
    
    while countup < 5:
        if misc['sensor'] <= 2000 or misc['sensor'] > 4000:
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
        tStatus = threading.Thread(name='status', target=status, args=('abort',))
        tStatus.daemon = True
        tStatus.start()
        
        tSetup = threading.Thread(name='setup', target=setup)
        tSetup.daemon = True
        tSetup.start()

def snapshot(image):
    global ready
    global overlay
    global merci
    global misc
    global pos
    global live
    global camera
    
    print 'image: ', image
    print 'real image: ', str(misc['images'][image])

    filename = time.strftime('%Y%m%d') + '-' + time.strftime('%H%M%S')
    
    print 'filename: ' + filename
    
    message = 'snapshot: ' + filename
    tStatus = threading.Thread(name='status', target=status, args=(message,))
    tStatus.daemon = True
    tStatus.start()
    
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
    
    tStatus = threading.Thread(name='status', target=status, args=('upload',))
    tStatus.daemon = True
    tStatus.start()
        
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
    
def status(status):
    
    print 'status update'
    
    if status == 'init':
        # wait some more time for network stuff
        sleep(15)
        
    url = api['protocol'] + api['url'] + '/status'
    data = {'status': status}
    
    try:
        r = requests.post(url, headers=api['header'], data=data)
        print r.text
        response = r.json()
        del response
    
    except requests.exceptions.RequestException as e:
        print e
    
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
        print 'last action:  %s' % (int(time.time()) - int(ready['timestamp']))
        print 'ultrasonic: %s' % misc['sensor']
        print 'ready (setup): %s' % ready['setup']
        print 'ready (print): %s' % ready['print']
        print 'ready (upload): %s' % ready['upload']
        print 'ready (capture): %s' % ready['capture']
        print 'timestamp: %s' % int(time.time())
        print ''
        print '----------'
        
        timetime = int(time.time())
        capdiff = timetime - ready['capture']
        setupdiff = timetime - ready['setuptime']
        
        print 'capdiff: ', capdiff
        print 'setupdiff: ', setupdiff
        print 'timetime: ', timetime
       
        # if capture process takes more than a minute ---> reboot
        # if setup process takes more than 30 seconds ---> reboot
        if ( capdiff < timetime and capdiff > 60 ) or ( setupdiff < timetime and setupdiff > 30 ):
            print 'shutdown -r now'
            
            tStatus = threading.Thread(name='status', target=status, args=('reboot',))
            tStatus.daemon = True
            tStatus.start()
            
            sleep(5)
            
            reboot = subprocess.Popen('sudo shutdown -r now', shell=True)
        
        # if installation has been idle for 30 minutes ---> setup
        elif ready['setup'] == True and ( int(time.time()) - ready['timestamp'] ) > ( 60 * 30 ):
            
            print ''
            print ''
            print '=========='
            print ''
            print 're-setup'
            print ''
            print '=========='
            
            # ready['setup'] = False
            
            # tStatus = threading.Thread(name='status', target=status, args=('re-setup',))
            # tStatus.daemon = True
            # tStatus.start()
            
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime_string = str(timedelta(seconds = int(uptime_seconds)))
            
            message = 'uptime: ' + uptime_string
            tStatus = threading.Thread(name='status', target=status, args=(message,))
            tStatus.daemon = True
            tStatus.start()
            
            ready['timestamp'] = int(time.time())
            
            '''
            if merci != None and merci.poll() is None:
                # merci.terminate()
                os.kill(merci.pid, signal.SIGTERM)
                print 'merci (hello): kill'
                time.sleep(2)
                while merci.poll() is None:
                    time.sleep(3)
                    os.kill(merci.pid, signal.SIGKILL)
                    print 'merci (hello): forcekill'
            
            merci = subprocess.Popen(['/home/pi/raspidmx/pngview/./pngview','-b','0','-l','4','/home/pi/Photobooth/merci/hello.png'])
            print 'merci (hello): done'
            sleep(2)
            
            tSetup = threading.Thread(name='setup', target=setup)
            tSetup.daemon = True
            tSetup.start()
            '''

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
    
    tStatus = threading.Thread(name='status', target=status, args=('init',))
    tStatus.daemon = True
    tStatus.start()
    
    tSetup = threading.Thread(name='setup', target=setup)
    tSetup.daemon = True
    tSetup.start()
    
    tWatchdog = threading.Thread(name='watchdog', target=watchdog)
    tWatchdog.daemon = True
    tWatchdog.start()
    
    sensor = MySensor(misc['port'])
    sensor.start()
    
    while True:
        
        if misc['sensor'] != 0 and (misc['sensor'] <= 2000 or misc['sensor'] > 4000) and ready['setup'] == True:
            
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