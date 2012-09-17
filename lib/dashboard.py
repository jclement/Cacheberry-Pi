#!/usr/bin/env python

import os
import time
import unicodedata
from lcdproc.server import Server

class Dashboard:
  def __init__(self):
    self.__lcd = Server()
    self.__lcd.start_session()
    self.__screen = self.__lcd.add_screen("dashboard")
    self.__screen.set_heartbeat("off")
    self.__screen.set_priority("info")

    self.__clock_widget = self.__screen.add_string_widget("time","")
    self.__speed_widget = self.__screen.add_string_widget("speed","",y=2, x=1)
    self.__bearing_widget = self.__screen.add_string_widget("bearing","",y=2, x=14)

  def update(self, clock, speed, bearing):
    if clock:
      self.__clock_widget.set_text(time.strftime('%H:%M:%S  %d-%b', clock))
    self.__bearing_widget.set_text(bearing)
    self.__speed_widget.set_text('%0.0f km/h' % (speed * 3.6))

