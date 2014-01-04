#!/usr/bin/python

from unity import Unity
import time
import sys
import json
import re

class PresenceExample:
  def __init__(self):
    '''connects to unity network'''
    try:
      # pass the callback function for messages received from subscribed topics
      self.unity = Unity(self.on_message)
    except:
      print('could not connect to broker')
      sys.exit(1)

  def on_message(self, mosq, obj, msg):
    '''call back function when message received on subscribed topics'''

#    print(msg.topic + " : " + str(msg.payload))

    if msg.payload == '0':
      print ('Offline : '+msg.topic)
    elif msg.payload == '1':
      print ('Online  : '+msg.topic)

  def subscribe(self, topics):
    self.unity.subscribe(topics)

    rc = 0
    while rc == 0:
      rc = self.unity.loop()

if __name__ == "__main__":
  presence = PresenceExample()
  '''listen to device presence topic'''
  topics = [ 'devices/sensor/#' ]
  presence.subscribe(topics)
