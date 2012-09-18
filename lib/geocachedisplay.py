#!/usr/bin/env python

import os
import unicodedata
from lcdproc.server import Server

class GeocacheDisplay:
  def __init__(self):
    self.__lcd = Server()
    self.__lcd.start_session()
    self.__screen = self.__lcd.add_screen("cache")
    self.__screen.set_heartbeat("off")
    self.__screen.set_duration(10)
    self.__screen.set_priority("hidden")

    self.__title_widget = self.__screen.add_scroller_widget("title",1,1,12,1,"h",1,"")
    self.__code_widget = self.__screen.add_string_widget("code","",y=2)
    self.__distance_to_cache_widget = self.__screen.add_string_widget("dist","",y=2, x=9)
    self.__bearing_to_cache_widget = self.__screen.add_string_widget("btc","",y=2, x=14)
    self.__bearing_widget = self.__screen.add_string_widget("bearing","",y=1, x=14)

  def update(self, cache_name, code, bearing, bearing_to_cache, distance_to_cache):
    self.__title_widget.set_text(cache_name.encode('ascii'))
    self.__code_widget.set_text(code.encode('ascii'))
    if (distance_to_cache > 1000):
      self.__distance_to_cache_widget.set_text('%0.0fkm' % (distance_to_cache / 1000.0))
    else:
      self.__distance_to_cache_widget.set_text('%0.0fm' % distance_to_cache)
    self.__bearing_widget.set_text(bearing)
    self.__bearing_to_cache_widget.set_text(bearing_to_cache)

  def hide(self):
    self.__screen.set_priority("hidden")

  def show(self, foreground):
    if foreground:
      self.__screen.set_priority("foreground")
    else:
      self.__screen.set_priority("info")

