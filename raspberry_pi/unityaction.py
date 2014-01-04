#!/usr/bin/python

import RPi.GPIO as GPIO
from unity import Unity
from unitydatastore import UnityDatastore
from unitysota import UnitySota
import time
import sys
import json
import logging
import socket
import uuid
import subprocess
import re
import datetime


NAME = 'action'

ACTION_REQUEST = 'action/request'
ACTION_RESPONSE = 'action/response'
SOTA_PREFIX = 'SOTA'
SOTA_REQUEST = None
SOTA_RESOONSE = None

logger = logging.getLogger('unity_action')
fhdlr = logging.FileHandler('unity_action.log')
chdlr = logging.StreamHandler()
chdlr.setLevel(logging.DEBUG)
fhdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fhdlr.setFormatter(formatter)
logger.addHandler(fhdlr)
logger.addHandler(chdlr)
logger.setLevel(logging.INFO)

FAN_PIN=17

class UnityAction:
  def __init__(self):

    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, False)

    self.fqdn = socket.getfqdn()
    self.hostname = socket.gethostname()
    global ACTION_REQUEST
    global ACTION_RESPONSE
    global SOTA_REQUEST
    global SOTA_RESPONSE
    global NAME

    ACTION_REQUEST = self.fqdn+'/action/request'
    ACTION_RESPONSE = self.fqdn+'/action/response'
    SOTA_REQUEST = SOTA_PREFIX+'/'+self.fqdn+'/request'
    SOTA_RESPONSE = SOTA_PREFIX+'/'+self.fqdn+'/response'
    NAME=self.fqdn+'_'+NAME


  def connect(self):
    self.unity = Unity(NAME)
    self.unity_ds = UnityDatastore()
    try:
      self.unity.connect(Unity.SENSOR, False, self.on_message)
      self.unity_ds.connect()
    except:
      sys.stderr.write('could not connect to broker')
      sys.exit(1)

  def start(self):
    topics = [ACTION_REQUEST, SOTA_REQUEST]
    self.unity.subscribe(topics)

  def on_message(self, mosq, obj, msg):
    logger.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    payload_json = json.loads(msg.payload)

    if 'SOTA/' in msg.topic and '/request' in msg.topic:
      logger.info('upgrade request' + msg.payload)
      unitysota = UnitySota(self.sota_status_callback)
      unitysota.execute(msg.payload)
    else:
      action = payload_json['action']
      component = payload_json['component']
      if component == 'camera' and action == 'take_picture':
        url = self.take_picture()
        action_response = {}
        if url != None:
          action_response['status'] = 'success'
          action_response['url'] = url
        else:
          action_response['status'] = 'error'
  
        action_response['requested_action'] = 'take_picture'
        action_response['device'] = self.fqdn
        action_response['request_id'] = payload_json['request_id']
        action_response['timestamp'] = payload_json['timestamp']
        self.unity.publish(ACTION_RESPONSE, json.dumps(action_response))
      elif component == 'fan' and action == 'on':
        self.control_fan('on')
      elif component == 'fan' and action == 'off':
        self.control_fan('off')
    
  def control_fan(self, action):
    if action == "on":
      GPIO.output(FAN_PIN, True)
    elif action == "off":
      GPIO.output(FAN_PIN, False)

  def take_picture(self):
    url = None
    filename = '/tmp/image_'+str(uuid.uuid1())+'.jpeg'
    key = filename.split('/')[2]
    command = ['/opt/vc/bin/raspistill', '-w','640','-h', '480', '-t', '1', '-o', filename]
    if command != None:
      cmd = subprocess.Popen(command)
      bucket_name = self.fqdn
      ret = cmd.wait()
      logger.info("executed %s, exit code %d" % (command, ret))
      if ret == 0:
        self.unity_ds.upload_file(bucket_name, filename, key)
        connected_datastore = self.unity_ds.get_connected()
        url = "http://"+connected_datastore['host']+":"+str(connected_datastore['port'])+"/buckets/"+self.fqdn+"/keys/"+key
        logger.info("url %s" % (url))
    return url
  

  def sota_status_callback(self, message):
    logger.info('sota_status_callback message %s' % message)
    self.unity.publish(SOTA_RESPONSE, str(message))

  def execute_command(self, command):
    pass

if __name__ == "__main__":
  unity_action = UnityAction()
  unity_action.connect()
  unity_action.start()
