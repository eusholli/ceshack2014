#!/usr/bin/python

from unity import Unity
import time
import uuid
import sys
import json
import re

class ControlCameraExample:
  continue_listening = True
  request_id = None

  def __init__(self):
    '''connects to unity network'''
    try:
      self.unity = Unity(self.on_message)
    except:
      print('could not connect to broker')
      raise

  def on_message(self, mosq, obj, msg):
    '''call back function when message received on subscribed topics'''
    print(msg.topic + " : " + str(msg.payload))
    json_obj = json.loads(msg.payload)
    if json_obj['request_id'] == self.request_id:
      response_topic = json_obj['device']+'/action/response'
      self.unity.unsubscribe([response_topic])
      self.continue_listening = False

  def take_picture(self, device_id):
    full_device_name = device_id + '.ceshack.unity.tfoundry.com'
    topic = full_device_name + '/action/request'
    response_topic = full_device_name + '/action/response'
    self.request_id = str(uuid.uuid1())

    action_request = {}
    action_request['component'] = 'camera'
    action_request['device_name'] = full_device_name
    action_request['action'] = 'take_picture'
    action_request['request_id'] = self.request_id
    action_request['timestamp'] = time.time()

    print topic
    self.unity.publish(topic, json.dumps(action_request))
    self.subscribe([response_topic])

  def subscribe(self, topics):
    self.unity.subscribe(topics)
    rc = 0
    while rc == 0 and self.continue_listening:
      rc = self.unity.loop()

if __name__ == "__main__":
  camera = ControlCameraExample()
  camera.take_picture('ceshack-pi00')
