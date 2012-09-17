#!/usr/bin/env python

import os
from threading import Thread, Lock
import gps
import copy

MAX_ERROR_X = 30
MAX_ERROR_Y = 30
MAX_ERROR_S = 30

class GpsHandler(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.__lock = Lock()
    self.__gps = gps.gps(mode=gps.WATCH_ENABLE)
    self.__state = {'p':None, 's':0, 'b':0, 't':None}

  def state(self):
    self.__lock.acquire()
    state_copy = copy.copy(self.__state)
    self.__lock.release()
    return state_copy

  def run(self):
    while 1:
      gpsinfo = self.__gps.next()
      if gpsinfo["class"] == 'TPV':
        self.__lock.acquire()
        if 'track' in gpsinfo.keys():
          self.__state['b'] = gpsinfo.track
        if 'lat' in gpsinfo.keys() and 'lon' in gpsinfo.keys():
          if gpsinfo['epx'] < MAX_ERROR_X and gpsinfo['epy'] < MAX_ERROR_Y:
            self.__state['p'] = (gpsinfo.lat, gpsinfo.lon)
        if 'speed' in gpsinfo.keys():
          if gpsinfo.eps < MAX_ERROR_S:
            self.__state['s'] = gpsinfo.speed
        if 'time' in gpsinfo.keys():
          self.__state['t'] = gpsinfo['time']
        self.__lock.release()



