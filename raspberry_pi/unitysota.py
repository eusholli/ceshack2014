#!/usr/bin/python

from unity import Unity
from unitydatastore import UnityDatastore
from subprocess import Popen
from time import strftime, gmtime
import time
import sys
import json
import logging
import socket
import uuid
import subprocess
import re
import datetime
import os
import httplib2
import urllib

logger = logging.getLogger('unity_sota')
fhdlr = logging.FileHandler('unity_sota.log')
chdlr = logging.StreamHandler()
chdlr.setLevel(logging.DEBUG)
fhdlr.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fhdlr.setFormatter(formatter)
logger.addHandler(fhdlr)
logger.addHandler(chdlr)
logger.setLevel(logging.INFO)

class UnitySota:
  def __init__(self, status_callback):
    self.fqdn = socket.getfqdn()
    self.hostname = socket.gethostname()
    self.pubsub_status_callback = status_callback

  def read_manifest(self, manifest_file):
    logger.info('reading manifest file %s' % manifest_file)
    manifest_data=open(manifest_file)
    manifest=json.load(manifest_data)

    return manifest

  def upgrade(self, dir, manifest):
    for m in manifest['pre-upgrade']:
      status = self.execute_command(m) 
      if status != 0 :
        print 'error executing command '+m
        return 1

    for m in manifest['upgrade']:
      m = m.replace('REPLACE_TMP_DIR', dir)
      status = self.execute_command(m) 
      if status != 0 :
        print 'error executing command '+m
        return 1

    for m in manifest['post-upgrade']:
      status = self.execute_command(m) 
      if status != 0 :
        print 'error executing command '+m
        return 1

    return 0


  def status_callback(self, str):
    self.pubsub_status_callback(str)
    self.status_text.append(str)

  def execute_command(self, command_string):
    logger.info('executing command '+command_string)
    self.status_callback('  executing command %s' % command_string)
    commands = command_string.split(' ')
    process = Popen(commands)
    ret = process.wait()
    self.status_callback('  command executed '+command_string+ ' with exit status = '+str(ret))
    return ret
    

  def delete_temp_directory(self, dir):
    logger.debug('delete temp directory %s' % dir)
    ret = self.execute_command('rm -rf '+dir)

    return ret

  def create_temp_directory(self, dir):
    logger.debug('create temp directory %s' % dir)
    ret = 0
    try:
      os.mkdir(dir)
    except:
      logger.exception('error creating directory %s' % dir)
      #self.delete_temp_directory(dir)
      ret = 1

    return ret

  def extract_package(self, dir, filename):
    cmd_str = "tar -C "+dir+" -xvzf "+filename
    return self.execute_command(cmd_str)
    
  
  def download_package(self, key):
    logger.info("downloading %s" % (key))
    dir = "/tmp/"+key+"_"+str(int(time.time()))
    filename = dir + "/" + key

    ret = self.create_temp_directory(dir)
     
    if ret != 0:
      logger.error('error making director %s' % dir)
      return None, None

    unity_ds = UnityDatastore()
    unity_ds.connect()
    bucket = unity_ds.get_bucket('software')
    bin_data = bucket.get(key)

    f = open(filename, 'w')
    f.write(bin_data.encoded_data)
    f.close()

    bucket = unity_ds.get_bucket('software_gtts')
    bin_data = bucket.get(key+'.gtts')

    f = open(filename+'.gtts', 'w')
    f.write(bin_data.encoded_data)
    f.close()

    return dir, filename

  def verify_package(self, key, filename):
    verify_cmd = "nodejs /home/pi/unity_new/guardtime/verify.js "+filename
    return self.execute_command(verify_cmd)
        

  def execute(self, payload_str):
    self.status_text = []
    payload = json.loads(payload_str)
    key = payload['package']
    procedure = payload['procedure']
    device_name = payload['device_name']
    ## TODO implement device name check
    username = payload['username'] 

    status_key = "sota_"+procedure+"_"+device_name+"_"+str(int(time.time()))
    status_json = {}
    status_json['key'] = status_key
    status_json['package'] = key
    status_json['device_name'] = device_name
    status_json['procedure'] = procedure
    status_json['username'] = username
    status_json['timestamp'] = strftime("%Y-%m-%d %H:%M:%S %Z", gmtime())

    self.status_callback('Downloading package '+key)
    dir, filename = self.download_package(key)
    if dir == None or filename == None:
      logger.error('error downloading package %s' % key)
      self.cleanup(dir, status_json, False)
      return 1
    self.status_callback('Download package %s SUCCESS' % key)
    
    self.status_callback('Validating software package %s' % key)
    package_valid = self.verify_package(key, filename)

    if package_valid != 0:
      logger.error('error validating software package %s' % key)
      self.cleanup(dir, status_json, False)
      return 1

    self.status_callback('Software package validation %s SUCCESS' % key)

    self.status_callback('Extracting package '+key)
    ret = self.extract_package(dir, filename)
    if ret != 0:
      logger.error('error extracting package dir %s package %s' % (dir, key))
      self.cleanup(dir, status_json, False)
      return 1
    self.status_callback('Extracting package %s SUCCESS' % key)
    
    manifest_file = dir + '/package/manifest.json'
    manifest = self.read_manifest(manifest_file)

    self.status_callback('Upgrading  ....')
    ret = self.upgrade(dir+'/package/', manifest)
    
    if ret != 0:
      logger.error('error upgrading package %s' % key)
      self.cleanup(dir, status_json, False)
      return 1

    return self.cleanup(dir, status_json, True)

  def cleanup(self, dir, status_json, success):

    self.status_callback('Cleaning up...')
    self.delete_temp_directory(dir)
    self.status_callback('Clean up SUCCESS')
    
    status_json['logs'] = self.status_text

    if success:
      self.status_callback('Upgrade SUCCESS')
    else:
      self.status_callback('Upgrade FAILED')
    self.upload_status(status_json)

    return 0


  def upload_status(self, body):
    http = httplib2.Http()
    ## TODO fix this
    url = 'http://c3.att.slyfox.tfoundry.com:8000/sign'
    headers = {'Content-type': 'application/json'}
    response, content = http.request(url, 'POST', headers=headers, body=json.dumps(body))
    print response
    print content

def run():
  manifest_file = 'manifest.json'
  unity_sota = UnitySota(cb)
  dict = {}
  dict['package'] = 'rpi_temperature_bug_package.tar.gz'
  dict['device_name'] = 'temppi.att.slyfox.tfoundry.com'
  dict['procedure'] = 'procedure'
  dict['username'] = 'jacob'
  unity_sota.execute(json.dumps(dict))

def cb(str):
  print str
  
if __name__ == "__main__":
  run()
