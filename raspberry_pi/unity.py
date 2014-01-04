#!/usr/bin/python

import dns.resolver
import socket
import time
import mosquitto
import logging
import sys

CONTROLLER_SRV_QUERY = '_m2mcontroller._tcp'

class Unity:
  SENSOR='sensor'
  APPLIANCE='appliance'
  def __init__(self, name):
    self.fqdn = socket.getfqdn()
    self.hostname = socket.gethostname()
    self.name = name
    self.setup_logger(name)

  def setup_logger(self, name):
    self.logger = logging.getLogger(name+'_unity')
    fhdlr = logging.FileHandler('/var/log/'+name+'_unity.log')
    chdlr = logging.StreamHandler()
    chdlr.setLevel(logging.DEBUG)
    fhdlr.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fhdlr.setFormatter(formatter)
    self.logger.addHandler(fhdlr)
    self.logger.addHandler(chdlr)
    self.logger.setLevel(logging.INFO)

  def find_broker(self):
    lowest_priority = 0
    mqtt_host = None
    mqtt_port = None
    controller_srv_record = self.fqdn.replace(self.hostname, CONTROLLER_SRV_QUERY);
    try:
      answers = dns.resolver.query(controller_srv_record, 'SRV')
      for answer in answers:
	# TODO implement weight
	if answer.priority <= lowest_priority:
	  mqtt_host = answer.target.to_text()
          mqtt_port = answer.port
	  break
	else :
	  lowest_priority = answer.priority
    except dns.resolver.NXDOMAIN:
      # TODO remove this when we get APN for 3GPP
      # use public
      self.logger.warn('could not find domain, using public domain instead')
      mqtt_host = 'pubsub.ceshack2014.att.io'
      mqtt_port = 1883
    except:
      self.logger.exception("error querying controller") 

    return mqtt_host, mqtt_port
    
  def connect_to_broker(self, mqtt_host, mqtt_port, connectType, publish_presence, on_message=None):
    name = self.fqdn + '_' + self.name
    self.logger.info("connecting '%s' to '%s:%d' using name '%s', topic prefix '%s/'" % (connectType, mqtt_host, mqtt_port, self.name, self.fqdn))
    mqttc = None
    self.connectType = connectType
    try:
      mqttc = mosquitto.Mosquitto(name)
      if on_message == None:
        mqttc.on_message = self.on_message
      else:
        mqttc.on_message = on_message
      mqttc.on_connect = self.on_connect
      mqttc.on_publish = self.on_publish
      mqttc.on_subscribe = self.on_subscribe
      mqttc.on_log = self.on_log

      if publish_presence:
        mqttc.will_set('devices/'+self.connectType+'/'+self.fqdn, '0', retain=True)
      mqttc.connect(mqtt_host, mqtt_port)
      if publish_presence:
        mqttc.publish('devices/'+self.connectType+'/'+self.fqdn, '1', retain=True)

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
    if not self.fqdn in topic:
      topic = self.fqdn + '/' + topic
    self.mqttc.publish(topic, msg)

  def subscribe(self, topics):
    for topic in topics: 
      self.logger.info("subscribing to %s" % (str(topic)))
      self.mqttc.subscribe(topic)

    rc = 0;
    while rc == 0:
      rc = self.mqttc.loop()

  def connect(self, typeEnum, publish_presence, on_message=None):
    connectType = str(typeEnum)
    mqtt_host, mqtt_port = self.find_broker()
    if mqtt_host == None or mqtt_port == None:
      raise Exception("Cannot find a broker")


    self.mqttc = self.connect_to_broker(mqtt_host, mqtt_port, connectType, publish_presence, on_message)
    if self.mqttc == None:
      raise Exception("Could not connect to broker %s:%d" % (mqtt_host, mqtt_port))
