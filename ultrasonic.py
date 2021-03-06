#!/usr/bin/python3
# Filename: ultrasonic.py

# Reads serial data from Maxbotix ultrasonic rangefinders
# Gracefully handles most common serial data glitches
# Use as an importable module with "import ultrasonic"
# Returns an integer value representing distance to target in millimeters

from time import time
from serial import Serial

serialDevice = "/dev/ttyUSB0" # default for RaspberryPi
maxwait = 1 # seconds to try for a good reading before quitting

def measure(portName):
    ser = Serial(portName, 57600, 8, 'N', 1, timeout=1)
    timeStart = time()
    rv = ''

    while time() < timeStart + maxwait:
       ch = ser.read()
       rv += ch
       if ch=='\r':
           dt = rv.replace('\r','').lstrip('R')
           rv = ''
           try:
               mm = int(dt)
           except ValueError:
               # value is not a number
               continue
           ser.close()
           return(mm)

    ser.close()
    # raise RuntimeError("Expected serial data not received")

if __name__ == '__main__':
    measurement = measure(serialDevice)
    print("distance =",measurement)