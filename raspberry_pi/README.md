# Unity client

#### Client setup

##### Update hostname and FQDN in /etc/hosts

change 

```127.0.1.1	localhost```

to

```127.0.1.1	<hostname>	<hostname>.ceshack.unity.tfoundry.com```

##### Add hostname in /etc/hostname	

```echo "<hostname>" > /etc/hostname```

##### Reboot Pi to take effect

```
sudo sync
sudo shutdown -r now
```

##### Install required libraries

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install upstart
```
##### Restart and make sure it can boot and install rest of libraries

```
sudo sync
sudo shutdown -h now 
```
Restart Pi and 
```
sudo apt-get install python-pip
sudo pip install mosquitto
sudo pip install dnspython
sudo pip install riak
sudo pip install httplib2
sudo pip install pyserial
```
#### Configuring I2C
Follow Configuring I2C setup at this link: http://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
```
sudo sync
sudo shutdown -r now
```

#### Checkout files in this repo to /home/pi/ceshack directory

#### Install upstart files
```
sudo cp ceshack-publish.conf /etc/init
sudo cp ceshack-action.conf /etc/init
sudo cp ceshack-admin.conf /etc/init
```

#### Run sample
```
sudo ./sample.py
connecting 'sensor' to 'c3.att.slyfox.tfoundry.com.:1883' using name 'mqtt_client_name', topic prefix 'testpi.att.slyfox.tfoundry.com/'
mid: 1
mid: 2
```
The first line will list the ```host:port``` the client connects to, its ```name``` and ```topic prefix```

In the example above, the data published will be available on this topic ```testpi.att.slyfox.tfoundry.com/<name_of_topic>``` on MQTT host ```c3.att.slyfox.tfoundry.com.:1883``` the <name_of_topic> is the ```topic``` variable found in ```sample.py```

To see data all data published by device irrespective of topic subscribe to
topic prefix/#. For example ```testpi.att.slyfox.tfoundry.com/#```

If you set broadcast presence to true in sample.py you should be able to see the presence of the device by subscribing to. 

Payload of

```0``` means offline

```1``` means online


`devices/sensor` for Sensors

`devices/appliance` for Appliances
