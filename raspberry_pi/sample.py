#!/usr/bin/python

from Adafruit_LSM303 import Adafruit_LSM303
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
import os

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

ser = None

if os.path.exists('/dev/ttyACM0'):
  ser = serial.Serial('/dev/ttyACM0', 9600)

def get_lsm(lsm):

  #print '[(Accelerometer X, Y, Z), (Magnetometer X, Y, Z, orientation)]'
  values = lsm.read()
  dict = {}
  dict['sensor_type'] = 'lsm303'
  dict['accelerometer'] = {}
  dict['accelerometer']['x'] = values[0][0]
  dict['accelerometer']['y'] = values[0][1]
  dict['accelerometer']['z'] = values[0][2]

  dict['magnetometer'] = {}
  dict['magnetometer']['x'] = values[1][0]
  dict['magnetometer']['y'] = values[1][1]
  dict['magnetometer']['z'] = values[1][2]

  return dict

def read_arduino():
  arduino_values = None
  if ser != None:
    arduino_values = {}
    line=ser.readline()

    match = re.findall("CO=([0-9]+)", line)
    if match:
      arduino_values['CO']=match[0]

    match = re.findall("Alcohol=([0-9]+)", line)
    if match:
      arduino_values['Alcohol']=match[0]

  return arduino_values

def read_dht():
  # Run the DHT program to get the humidity and temperature readings!
  temp = None
  humidity = None

  dhtoutput = dhtreader.read(dht_type, dht_pin)
  if dhtoutput != None:
    temp = dhtoutput[0]
    humidity = dhtoutput[1]

  return temp, humidity

def read_lsm303():
  lsm = Adafruit_LSM303()
  lsm.read()
def read_tsl2561():
  lux = luxread()
  return lux

try:
  ## connect to network specifing device type and broadcast presence flag
  unity.connect(device_type, broadcast_presence)
except:
  print('could not connect to broker')
  sys.exit(1)

dht_counter = 0
tsl_counter = 0
lsm_counter = 0
arduino_counter = 0
lsm = Adafruit_LSM303()
while(True):

  dict = {}
  timestamp = strftime("%Y-%m-%d %H:%M:%S %Z", gmtime())

  temp, humidity = read_dht()
  if temp != None or humidity != None:
    dict['sensor_type'] = 'dht22'
    dict['counter'] = dht_counter
    dict['timestamp'] = timestamp
    dht_counter = dht_counter + 1
    if temp != None:
      dict['temperature'] = "%.2f" % temp
    if humidity != None:
      dict['humidity'] = "%.2f" % humidity
    json_str = json.dumps(dict)
    unity.publish(topic, json_str)

  dict = {}
  lux = read_tsl2561()
  if lux != None:
    dict['sensor_type'] = 'tsl2561'
    dict['counter'] = tsl_counter
    dict['timestamp'] = timestamp
    tsl_counter = tsl_counter + 1
    dict['lux'] = "%.2f" % lux
    json_str = json.dumps(dict)
    unity.publish(topic, json_str)

  lsm_values = get_lsm(lsm)
  if lsm_values != None:
    lsm_values['timestamp'] = timestamp
    lsm_values['sensor_type'] = 'lsm303'
    lsm_values['counter'] = lsm_counter
    json_str = json.dumps(lsm_values)
    lsm_counter = lsm_counter + 1
    unity.publish(topic, json_str)

  
  arduino_values = read_arduino()
  if arduino_values != None: 
    dict = {}
    dict['timestamp'] = timestamp
    dict['sensor_type'] = 'gas'
    dict['counter'] = arduino_counter
    arduino_counter = arduino_counter + 1
    dict.update(arduino_values)
    json_str = json.dumps(dict)
    unity.publish(topic, json_str)

  time.sleep(1)
