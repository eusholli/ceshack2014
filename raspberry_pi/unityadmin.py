#!/usr/bin/python

from unity import Unity
import time
import sys
import socket
import logging
import subprocess
import re
import json

logger = logging.getLogger('unity_admin')
fhdlr = logging.FileHandler('unity_admin.log')
chdlr = logging.StreamHandler()
chdlr.setLevel(logging.DEBUG)
fhdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fhdlr.setFormatter(formatter)
logger.addHandler(fhdlr)
logger.addHandler(chdlr)
logger.setLevel(logging.INFO)


ADMIN_REQUEST='/admin/request'
ADMIN_RESPONSE='/admin/response'

class UnityAdmin:
  def __init__(self):
    global ADMIN_REQUEST
    global ADMIN_RESPONSE

    self.fqdn = socket.getfqdn()

    ADMIN_REQUEST = self.fqdn + ADMIN_REQUEST
    ADMIN_RESPONSE = self.fqdn + ADMIN_RESPONSE

  def connect(self):
    NAME='unityadmin'
    device_type=Unity.SENSOR
    broadcast_presence=False

    self.unity = Unity(NAME)
    try:
      self.unity.connect(device_type, broadcast_presence, self.on_admin_message)
      self.unity.subscribe([ADMIN_REQUEST])
    except:
      logger.exception('error connecting to broker')
      sys.exit(1)

  def on_admin_message(self, mosq, obj, msg):
    logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.payload == 'get_ip':
      output = self.execute_command('ifconfig eth0')
      dict = {}
      if output != None:
        match = re.findall(r".*inet\saddr:(.*)\sBcast.*", output)
        if match:
          ip_addr = match[0]
          logger.debug("eth0 ip_addr = %s" % (ip_addr))
          dict['eth0']=ip_addr

      output = self.execute_command('ifconfig wlan0')
      if output != None:
        match = re.findall(r".*inet\saddr:(.*)\sBcast.*", output)
        if match:
          ip_addr = match[0]
          logger.debug("eth0 ip_addr = %s" % (ip_addr))
          dict['wlan0']=ip_addr

      self.unity.publish(ADMIN_RESPONSE, json.dumps(dict))
        
    elif msg.payload == 'ping':
      self.unity.publish(ADMIN_RESPONSE, 'pong')
    elif msg.payload == 'restart':
      self.execute_command('sudo sync')
      self.execute_command('sudo shutdown -r now')
      self.unity.publish(ADMIN_RESPONSE, 'restarting ...')
    elif msg.payload == 'shutdown':
      self.execute_command('sudo sync')
      self.execute_command('sudo shutdown -h now')
      self.unity.publish(ADMIN_RESPONSE, 'shutting down...')
      

  def execute_command(self, command_str):
    output = None
    command = command_str.split(' ')
    if command != None:
      cmd = subprocess.Popen(command, stdout=subprocess.PIPE)
      ret = cmd.wait()
      if ret == 0:
        output = cmd.communicate()[0]

    return output

if __name__ == "__main__":
  unity_admin = UnityAdmin()
  unity_admin.connect()
