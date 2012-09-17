#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

LED_ON = GPIO.HIGH
LED_OFF = GPIO.LOW

class LedHandler:
  def __init__(self, led_pins):  # GPIO Pin addresses
    GPIO.setmode(GPIO.BOARD)
    self.__led_pins = []
    for pin in led_pins:
      self.__led_pins.append([pin, LED_OFF])
      pin_index = len(self.__led_pins)-1
      self.__set_pin_to_output(pin_index)
      self.set(pin_index, LED_ON)
      time.sleep(0.1)
      self.set(pin_index, LED_OFF)

  def __set_pin_to_output(self, pin):
    GPIO.setup(self.__led_pins[pin][0], GPIO.OUT)
    pass

  def set(self, pin, state):
    if pin < 0 or pin >= len(self.__led_pins):
      raise "Unknown LED pin"
    if state <> LED_ON and state <> LED_OFF:
      raise "Unknown LED state"
    self.__led_pins[pin][1] = state
    GPIO.output(self.__led_pins[pin][0], state)

  def toggle(self, pin):
    if pin < 0 or pin >= len(self.__led_pins):
      raise "Unknown LED pin"
    if (self.__led_pins[pin][1] == LED_ON):
      self.set(pin, LED_OFF)
    else:
      self.set(pin, LED_ON)


 
  
