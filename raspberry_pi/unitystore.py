#!/usr/bin/python

import logging
from unity import Unity
from unitydatastore import UnityDatastore
import threading
import json
import datetime
import sys

logger = logging.getLogger('unity-sub-store')
hdlr = logging.FileHandler('unity-sub-store.log')
chdlr = logging.StreamHandler()
chdlr.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s %(message)s')
hdlr.setFormatter(formatter)
chdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.addHandler(chdlr)
logger.setLevel(logging.DEBUG)

class UnityStore(threading.Thread):
  def __init__(self, topic):
    threading.Thread.__init__(self)
    self.topic = topic.split('/')[2]
    name = self.topic+'_store'
    self.unity = Unity(name)
    self.unitydb = UnityDatastore()
    try:
      self.unity.connect(Unity.APPLIANCE, False, self.store_message)
      self.unitydb.connect()
    except:
      logger.exception('cannot connect to unity')
      sys.exit(1)
 
    self.bucket = self.unitydb.get_bucket(self.topic)
  
  def run(self):
    self.unity.subscribe([self.topic+'/readings'])

  def store_message(self, mosq, obj, msg):
    start_time = datetime.datetime.now()
    logger.debug(msg.payload)


    content_type = 'application/json'
    key_name = None
    current_hour = None
    j = None
    try:
      j = json.loads(msg.payload)
      timestamp_str = j['timestamp']
      sensor_type = j['sensor_type']
      #format 2013-09-24 18:52:33
      dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S %Z')
      current_hour = self.get_hour(dt)
      key_name = sensor_type+'_'+dt.strftime('%Y%m%d%H0000')+'_'+str(current_hour)
    except ValueError:
      logger.warn('error parsing %s, just dumping data' % msg.payload)
      current_hour = self.get_hour(start_time)
      key_name = 'rawdata_'+start_time.strftime('%Y%m%d%H0000')+'_'+str(current_hour)
      j = {}
      j['rawdata'] = msg.payload
      j['timestamp'] = str(start_time)
    except KeyError:
      logger.warn('error parsing %s, just dumping data' % msg.payload)
      current_hour = self.get_hour(start_time)
      key_name = 'rawdata_'+start_time.strftime('%Y%m%d%H0000')+'_'+str(current_hour)
      j = {}
      j['rawdata'] = msg.payload
      j['timestamp'] = str(start_time)
    

    value = self.bucket.get(key_name)
    data = value.data
    if data == None:
      data = []
    
    data.append(j)

    entry = self.bucket.new(key_name, data, content_type)
    entry.store()

    end_time = datetime.datetime.now()
    logger.debug(msg.topic + " store message execution time : "+str((end_time - start_time).microseconds))

  def get_hour(self, dt):
    unix_time = int(dt.strftime('%s'))
    seconds_in_hour = unix_time % 3600
    return unix_time - seconds_in_hour
    
def main():
  unity = Unity('PRESENCE')
  unity.connect(Unity.APPLIANCE, True, presence_message)
  unity.subscribe(['devices/'+str(Unity.SENSOR)+'/#'])

def presence_message(mosq, obj, msg):
  if(msg.payload == "1"):
    logger.info(msg.topic + " is ONLINE")
    test = UnityStore(msg.topic)
    test.setDaemon(True)
    test.start()

if __name__ == "__main__":
  main()
