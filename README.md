# AT&T Developer Summit 2014 Hackathon Unity Sensor Network

Welcome to the 2014 AT&T Developer Summit Hackathon

Deployed in the room are 7 sensor kits named ceshack-pi01 to ceshack-pi07

These kits are broadcasting in realtime the following sensor data:

* Light
* Humidity
* Temperature
* Alcohol Levels
* Carbon Monoxide Levels
* Acceleration - X, Y, Z planes
* Magnetic Fields - X, Y, Z planes

On each device is also an iBeacon

See this data presented live here - http://socketio.ceshack2014.att.io:5000/meter.html#

If you select one of the devices then you can take a picture and control the attached fan

To learn how to read the data and control the devices yourselves please see here - http://socketio.ceshack2014.att.io/instructions/

The data is also streamed live into http://m2x.att.com

* ceshack-pi01 - curl -i http://api-m2x.att.com/v1/feeds/54ced6e4e0788f41168eb167b16b8d8a -H "X-M2X-KEY: 21fc5d75c9fe714e3c79d22220c4beae"

* ceshack-pi02 - curl -i http://api-m2x.att.com/v1/feeds/80e79d294233359b1a8ebc969735a82f -H "X-M2X-KEY: b9b1b404cc33f5352bfc77292764d5f9"

* ceshack-pi03 - curl -i http://api-m2x.att.com/v1/feeds/459cb7b4d388fac70b926e23d4cc51db -H "X-M2X-KEY: 1c471b31791f583eafb72f04bc60c184"

* ceshack-pi04 - curl -i http://api-m2x.att.com/v1/feeds/6a3fab1850ab258ab8b15d82ee10f3ab -H "X-M2X-KEY: fa18f4dca84dff4d3078c6fb4943e2fa"

* ceshack-pi05 - curl -i http://api-m2x.att.com/v1/feeds/4ab4d9a315ea74cca41d9ecb34acc94b -H "X-M2X-KEY: a7a85c1f687706647cb9d20406ae7578 

* ceshack-pi06 - curl -i http://api-m2x.att.com/v1/feeds/28d0ed6a2e50477bfe309d4c9dbb5925 -H "X-M2X-KEY: 948df13f64cdd58ad02b409f52628fd9"

* ceshack-pi07 - curl -i http://api-m2x.att.com/v1/feeds/a4340c8e78f62af36a36fe9a9ec47f26 -H "X-M2X-KEY: fb0524aab9728637873e1356f3e6040d"


# $10,000 Prize

To the team that **uses the data the most creatively** to create an experience that we could not see before. Use your imagination. e.g. the room is a retail space and the kits are in different departments.  Or the kits are in different peoples house's etc...

Combine with other kits, available resources - no limits!!

Welcome to the Internet of NOW! and good luck

##Watch This Space!

Coming soon...

Coming online during the show is a door sensor that will detect height of people entering and take a photo.  Also request a picture from the door sensor

A bank of 10 Philips Hue lights that you can control through the same interfaces as above

## Onsite Support

Please see the Ericsson desk.  If nobody there please send texts to one of the following:

  - Jacob Thomas - 214 738 7687
  - Thao Nguyen - 650 353 1486
  - Zia Syed - 925 917 1340
  - Geoff Hollingworth - 214 717 8973

## Credits

  - [Jacob Thomas](http://github.com/bjacobt)
  - [Geoff Hollingworth](http://github.com/eusholli)
  - [Thao Nguyen](http://github.com/boulethao)
  - [Zia Syed](http://github.com/ztsyed)

## License

(The MIT License)

Copyright (c) 2012 Geoff Hollingworth

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
