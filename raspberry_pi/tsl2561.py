#!/usr/bin/python

import sys
import smbus
import time
from Adafruit_I2C import Adafruit_I2C

### Written for Python 3
### Big thanks to bryand, who wrote the code that I borrowed heavily from/was inspired by
### More thanks pandring who kind of kickstarted my work on the TSL2561 sensor
### A great big huge thanks to driverblock and the Adafruit team (Congrats on your many succeses
### Ladyada).  Without you folks I would just be a guy sitting somewhere thinking about cool stuff
### Now I'm a guy building cool stuff.
### If any of this code proves useful, drop me a line at medicforlife.blogspot.com 


class Luxmeter:
    i2c = None

    def __init__(self, address=0x39, debug=0, pause=0.41):
        self.i2c = Adafruit_I2C(address)
        self.address = address
        self.pause = pause
        self.debug = debug

        self.i2c.write8(0x80, 0x03)     # enable the device
        self.i2c.write8(0x81, 0x11)     # set gain = 16X and timing = 101 mSec
        time.sleep(self.pause)          # pause for a warm-up

    def readfull(self, reg=0x8C):
        """Reads visible + IR diode from the I2C device"""
        try:
            fullval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(fullval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readIR(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        try:
            IRval = self.i2c.readU16(reg)
            newIR = self.i2c.reverseByteOrder(IRval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            return newIR
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readfullauto(self, reg=0x8c):
        """Reads visible + IR diode from the I2C device with auto ranging"""
        try:
            fullval = self.i2c.readU16(reg)
            newval = self.i2c.reverseByteOrder(fullval)
            if newval >= 37177:
                self.i2c.write8(0x81, 0x01)
                time.sleep(self.pause)
                fullval = self.i2c.readU16(reg)
                newval = self.i2c.reverseByteOrder(fullval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, fullval & 0xFFFF, reg))
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

    def readIRauto(self, reg=0x8e):
        """Reads IR diode from the I2C device with auto ranging"""
        try:
            IRval = self.i2c.readU16(reg)
            newIR = self.i2c.reverseByteOrder(IRval)
            if newIR >= 37177:
                self.i2c.write8(0x81, 0x01)     #   remove 16x gain
                time.sleep(self.pause)
                IRval = self.i2c.readU16(reg)
                newIR = self.i2c.reverseByteOrder(IRval)
            if (self.debug):
                print("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X" % (self.address, IRval & 0xFFFF, reg))
            return newIR
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.address)
            return -1

def luxread(address = 0x39, debug = False, autorange = True):
    """Grabs a lux reading either with autoranging or without"""
    LuxSensor = Luxmeter(0x39, False)
    if autorange == True:
        ambient = LuxSensor.readfullauto()
        IR = LuxSensor.readIRauto()
    else:
        ambient = LuxSensor.readfull()
        IR = LuxSensor.readIR()
        
    ratio = (float) (IR / ambient)

    if ((ratio >= 0) & (ratio <= 0.52)):
        lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
    elif (ratio <= 0.65):
        lux = (0.0229 * ambient) - (0.0291 * IR)
    elif (ratio <= 0.80):
        lux = (0.0157 * ambient) - (0.018 + IR)
    elif (ratio <= 1.3):
        lux = (0.00338 * ambient) - (0.0026 * IR)
    elif (ratio > 1.3):
        lux = 0
    
    return lux


print(luxread())
