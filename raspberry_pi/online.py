#!/usr/bin/python

## This is a test client to make a raspberry pi "unity present" without any sensors

from unity import Unity
import subprocess
import re
import time
import sys
import json
from time import sleep, gmtime, strftime
from tsl2561 import luxread
import serial
import dhtreader

dht_type = 22
dht_pin = 4

dhtreader.init()

## The topic this device will be publishing to. Unity library will prepend the FQDN of the device. So topic for example below will be <fqdn>/readings
topic = 'readings'

## Use to identify client in MQTT broker
NAME='tsl2561'

## The type of devices. Either sensor or appliance
device_type=Unity.SENSOR

## If you want this device to broadcast its presence in Unity network
broadcast_presence=True

## instantiate unity client
unity = Unity(NAME)

while(True):
  try:
    ## connect to network specifing device type and broadcast presence flag
    unity.connect(device_type, broadcast_presence)
  except:
    print('could not connect to broker')
    sys.exit(1)

  time.sleep(15)
