#!/usr/bin/python

import socket
import mosquitto
import logging
import sys
import uuid

CONTROLLER_SRV_QUERY = '_m2mcontroller._tcp'

class Unity:
  SENSOR='sensor'
  APPLIANCE='appliance'

  def __init__(self, on_message=None, broadcast_presence=False):
    self.fqdn = socket.getfqdn()
    self.hostname = socket.gethostname()
    self.name = 'unityclient'
    device_type = Unity.APPLIANCE
    self.setup_logger(self.name)
    self.connect(device_type, broadcast_presence, on_message)


  def setup_logger(self, name):
    self.logger = logging.getLogger(name)
    chdlr = logging.StreamHandler()
    self.logger.addHandler(chdlr)
    self.logger.setLevel(logging.INFO)



  def find_broker(self):
    mqtt_host = 'pubsub.ceshack2014.att.io'
    mqtt_port = 1883

    return mqtt_host, mqtt_port
    
  def connect_to_broker(self, mqtt_host, mqtt_port, connectType, publish_presence, on_message=None):
    name = self.fqdn + '_' + self.name
    self.logger.info("connecting '%s' to '%s:%d'" % (connectType, mqtt_host, mqtt_port))
    mqttc = None
    self.connectType = connectType
    mqtt_identifier = str(uuid.getnode()) # use node so no collisions
    try:
      mqttc = mosquitto.Mosquitto(mqtt_identifier)
      if on_message == None:
        mqttc.on_message = self.on_message
      else:
        mqttc.on_message = on_message
      mqttc.on_connect = self.on_connect
      mqttc.on_publish = self.on_publish
      mqttc.on_subscribe = self.on_subscribe
      mqttc.on_log = self.on_log
      mqttc.connect(mqtt_host, mqtt_port)

    except:
      self.logger.exception("error connecting to broker")
      mqttc = None

    return mqttc

  def on_connect(self, mosq, obj, rc):
    self.logger.info("connected to broker")

  def on_message(self, mosq, obj, msg):
    self.logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

  def on_publish(self, mosq, obj, mid):
    self.logger.info("mid: "+str(mid))

  def on_subscribe(self, mosq, obj, mid, granted_qos):
    self.logger.info("Subscribed: "+str(mid)+" "+str(granted_qos))

  def on_log(self, mosq, obj, level, string):
    self.logger.debug(string)

  def publish(self, topic, msg):
    self.mqttc.publish(topic, msg)

  def unsubscribe(self, topics):
    for topic in topics:
      self.logger.info("unsubscribing to %s" % (str(topic)))
      self.mqttc.unsubscribe(topic)

  def subscribe(self, topics):
    for topic in topics: 
      self.logger.info("subscribing to %s" % (str(topic)))
      self.mqttc.subscribe(topic)

#    rc = 0;
#    while rc == 0:
#      rc = self.mqttc.loop()

  def loop(self):
    return self.mqttc.loop()

  def connect(self, typeEnum, publish_presence, on_message=None):
    connectType = str(typeEnum)
    mqtt_host, mqtt_port = self.find_broker()
    if mqtt_host == None or mqtt_port == None:
      raise Exception("Cannot find a broker")


    self.mqttc = self.connect_to_broker(mqtt_host, mqtt_port, connectType, publish_presence, on_message)
    if self.mqttc == None:
      raise Exception("Could not connect to broker %s:%d" % (mqtt_host, mqtt_port))

