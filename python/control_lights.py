#!/usr/bin/python

from unity import Unity
import time
import sys
import json
import re
import uuid

class ControlLightsExample:
  request_id = None
  def __init__(self):
    '''connects to unity network'''
    try:
      # pass the callback function for messages received from subscribed topics
      self.unity = Unity()
    except:
      print('could not connect to broker')

  def control_lights(self, bulb_id, on=False, bri=255, sat=255, hue=10000, effects='none'):
    device_name = 'hueproxy.ceshack.unity.tfoundry.com'
    topic = device_name + '/action/request'

    self.request_id = str(uuid.uuid1())

    action_request = {}
    action_request['bulb_id'] = bulb_id
    action_request['on'] = on
    action_request['bri'] = bri
    action_request['sat'] = sat
    action_request['hue'] = hue
    action_request['effect'] = effects
    action_request['request_id'] = self.request_id
    action_request['timestamp'] = time.time()

    self.unity.publish(topic, json.dumps(action_request))

  def on(self, bulb_id, bri=255, sat=255, hue=10000, effect='none'):
    self.control_lights(bulb_id, True, bri, sat, hue, effect)

  def off(self, bulb_id):
    self.control_lights(bulb_id, False)

if __name__ == "__main__":
  lights = ControlLightsExample()

  #turn on lamp 1 with brightness = 255, saturation = 255, hue = 10000 and effect = 'none' Note: none is a string here and not python None type
  lights.on(1, 255, 255, 10000, 'none')

  #turn off lamp 1
  lights.off(1)

