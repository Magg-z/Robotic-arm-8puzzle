#!/usr/bin/python3

import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM czestotliwosc 50HZ,the okres 20ms
    self.setPWM(channel, 0, int(pulse))

if __name__=='__main__':
    
  # #1490 srodek
  # # 0 - 1490
  # # 2 - 800
  # # 4 - 600
  # # 6 - 2500
   pwm = PCA9685(0x40, debug=False)
   pwm.setPWMFreq(50)
  
   a= [1490, 800, 600, 2500]
   b= [1250, 1800, 740, 2620]
   c= [1250, 2000, 800, 2620]
   d= [1500, 2000, 800, 2620]
   e= [1500, 1800, 800, 2620]
  
   pwm.setServoPulse(0,a[0])
   time.sleep(0.02)
   pwm.setServoPulse(2,a[1])
   time.sleep(0.02)
   pwm.setServoPulse(4,a[2])
   time.sleep(0.02)
   pwm.setServoPulse(6,a[3])
  
  # time.sleep(0.5)
  
  # pwm.setServoPulse(0,b[0])
  # time.sleep(0.02)
  # pwm.setServoPulse(2,b[1])
  # time.sleep(0.02)
  # pwm.setServoPulse(4,b[2])
  # time.sleep(0.02)
  # pwm.setServoPulse(6,b[3])
  
  
  # time.sleep(0.5)
  
  # pwm.setServoPulse(0,c[0])
  # time.sleep(0.02)
  # pwm.setServoPulse(2,c[1])
  # time.sleep(0.02)
  # pwm.setServoPulse(4,c[2])
  # time.sleep(0.02)
  # pwm.setServoPulse(6,c[3])
  
  # time.sleep(0.5)
  
  # pwm.setServoPulse(0,d[0])
  # time.sleep(0.02)
  # pwm.setServoPulse(2,d[1])
  # time.sleep(0.02)
  # pwm.setServoPulse(4,d[2])
  # time.sleep(0.02)
  # pwm.setServoPulse(6,d[3])
  
  # time.sleep(0.5)
  # pwm.setServoPulse(0,e[0])
  # time.sleep(0.02)
  # pwm.setServoPulse(2,e[1])
  # time.sleep(0.02)
  # pwm.setServoPulse(4,e[2])
  # time.sleep(0.02)
  # pwm.setServoPulse(6,e[3])
  
#   pwm.setServoPulse(0,1250)
#   time.sleep(0.02)
#   pwm.setServoPulse(2,1800)
#   time.sleep(0.02)
#   pwm.setServoPulse(4,740)
#   time.sleep(0.02)
#   pwm.setServoPulse(6,2650)
  
#   time.sleep(2)
#   pwm.setServoPulse(2,2000)
#   time.sleep(2)
#   pwm.setServoPulse(0,1450)