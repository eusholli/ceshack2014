#!/usr/bin/python

import dns.resolver
import socket
import time
import logging
import sys
import riak

DATASTORE_SRV_QUERY = '_datastore._tcp.xx'

logger = logging.getLogger('unity_datastore')
fhdlr = logging.FileHandler('unity_datastore.log')
chdlr = logging.StreamHandler()
chdlr.setLevel(logging.DEBUG)
fhdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fhdlr.setFormatter(formatter)
logger.addHandler(fhdlr)
logger.addHandler(chdlr)
logger.setLevel(logging.INFO)

class UnityDatastore:
  def __init__(self):
    self.fqdn = socket.getfqdn()
    self.hostname = socket.gethostname()
  
  def find_datastore(self):
    lowest_priority = 0
    ds_host = None
    ds_port = None
    datastore_srv_record = self.fqdn.replace(self.hostname, DATASTORE_SRV_QUERY);
    try:
      answers = dns.resolver.query(datastore_srv_record, 'SRV')
      for answer in answers:
	# TODO implement weight
	if answer.priority <= lowest_priority:
	  ds_host = answer.target.to_text()
          ds_port = answer.port
	  break
	else :
	  lowest_priority = answer.priority
    except dns.resolver.NXDOMAIN:
      # TODO remove this when we get APN for 3GPP
      # use public
      logger.warn('could not find domain, using public domain instead')
      ds_host = 'db.ceshack2014.att.io'
      ds_port = 8098
    except:
      logger.exception("error querying datastore")
    
    return ds_host, ds_port
  
  def get_connected(self):
    return self.connected_ds

  def connect_to_datastore(self, ds_host, ds_port):
    logger.info("connecting to datastore %s:%d" %(ds_host, ds_port))
    self.connected_ds = {}
    self.connected_ds['host'] = ds_host
    self.connected_ds['port'] = ds_port

    client = riak.RiakClient(nodes=[{'host':ds_host,'http_port':ds_port}])
    return client

  def upload_file(self, bucket_name, filename, key):
    logger.info('uploading %s to %s, key %s' % (filename, bucket_name, key))
    bucket = self.get_bucket(bucket_name)
    entry = bucket.new_from_file(key, filename)
    entry.store()
    return

  def get_bucket(self, bucket_name):
    bucket = self.client.bucket(bucket_name)
    return bucket
    
  def connect(self):
    ds_host, ds_port = self.find_datastore()
    if ds_host == None or ds_port == None:
      raise Exception("Cannot find a datastore")

    self.client = self.connect_to_datastore(ds_host, ds_port)
    if self.client == None:
      raise Exception("Could not connect to datastore %s:%d" % (ds_host, ds_port))

