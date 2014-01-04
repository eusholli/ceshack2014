#!/usr/bin/python

from unity import Unity
import time
import sys
import json
import re
import uuid

class ControlFanExample:
  request_id = None
  def __init__(self):
    '''connects to unity network'''
    try:
      self.unity = Unity()
    except:
      print('could not connect to broker')
      raise

  def control_fan(self, device_id, on=False):
    full_device_name = device_id + '.ceshack.unity.tfoundry.com'
    topic = full_device_name + '/action/request'

    self.request_id = str(uuid.uuid1())

    action_request = {}
    action_request['component'] = 'fan'
    action_request['device_name'] = full_device_name
    if on == True:
      action_request['action'] = 'on'
    else:
      action_request['action'] = 'off'
    action_request['request_id'] = self.request_id
    action_request['timestamp'] = time.time()

    self.unity.publish(topic, json.dumps(action_request))
  

  def on(self, device_id):
    self.control_fan(device_id, True)

  def off(self, device_id):
    self.control_fan(device_id, False)


if __name__ == "__main__":
  fan = ControlFanExample()
  fan.on('ceshack-pi01')
  time.sleep(2)
  fan.off('ceshack-pi01')
