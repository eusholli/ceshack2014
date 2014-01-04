#!/usr/bin/python

from unity import Unity
import time
import sys
import json
import re

class ExampleAppliance:
  def __init__(self):
    '''connects to unity network'''
    try:
      # pass the callback function for messages received from subscribed topics
      self.unity = Unity(self.on_message)
    except:
      print('could not connect to broker')

  def on_message(self, mosq, obj, msg):
    '''call back function when message received on subscribed topics'''

    print(msg.topic + " : " + str(msg.payload))

    # all data in .*/readings topics are sent in JSON format so parse them otherwise ignore
    if re.search('.*/readings$', msg.topic):
      self.parse_payload(msg.payload)

  def parse_payload(self, payload):
    '''function parses the JSON payload and print sensor type'''
    json_obj = json.loads(payload)
    print("sensor type %s" % (json_obj['sensor_type']))

  def subscribe(self, topics):
    self.unity.subscribe(topics)

    rc = 0
    while rc == 0:
      rc = self.unity.loop()

if __name__ == "__main__":
  '''topics to subscribe, must be a list, you can add multiple topics'''
  topics = [ 'ceshack-pi00.ceshack.unity.tfoundry.com/readings' ]
  example = ExampleAppliance()
  example.subscribe(topics)
