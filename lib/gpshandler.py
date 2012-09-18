#!/usr/bin/env python

import os
from threading import Thread, Lock
import gps
import copy

MAX_ERROR_X = 30
MAX_ERROR_Y = 30
MAX_ERROR_S = 30

class GpsHandler(Thread):
  def __init__(self, track_folder):
    Thread.__init__(self)
    self.daemon = True
    self.__lock = Lock()
    self.__gps = gps.gps(mode=gps.WATCH_ENABLE)
    self.__state = {'p':None, 's':0, 'b':0, 't':None}
    self.__has_lock = False
    self.__track_folder = track_folder
    self.__track_file = None
    if not os.path.exists(track_folder):
      os.mkdir(track_folder)

  def state(self):
    self.__lock.acquire()
    state_copy = copy.copy(self.__state)
    self.__lock.release()
    return state_copy

  def __update_tracklog(self):
    g = self.state()
    if not self.__track_file:
      if g['t']:
        self.__track_file = open(os.path.join(self.__track_folder, g[t]+'.csv'), 'w')
        self.__track_file.write('date,time,lat,lon,speed')
    if self.__track_file and self.__has_lock:
      clock = time.strptime(g['t'], '%Y-%m-%dT%H:%M:%S.000Z')
      self.__track_file.write('%s,%s,%s,%s,%s\n' % (
        time.strftime('%Y/%m/%d', clock),
        time.strftime('%H:%M:%S', clock),
        g['p'][0],
        g['p'][1],
        g['s']
        ))
      self.__track_file.flush()

  def run(self):
    while 1:
      gpsinfo = self.__gps.next()
      if gpsinfo["class"] == 'TPV':
        self.__lock.acquire()
        if 'track' in gpsinfo.keys() and self.__has_lock:
          self.__state['b'] = gpsinfo.track
        if 'lat' in gpsinfo.keys() and 'lon' in gpsinfo.keys() and self.__has_lock:
          self.__state['p'] = (gpsinfo.lat, gpsinfo.lon)
        if 'speed' in gpsinfo.keys() and self.__has_lock:
          if gpsinfo.eps < MAX_ERROR_S:
            self.__state['s'] = gpsinfo.speed
        if 'time' in gpsinfo.keys():
          self.__state['t'] = gpsinfo['time']
        if 'epx' in gpsinfo.keys() and 'epy' in gpsinfo.keys() and 'eps' in gpsinfo.keys():
          if gpsinfo.epx < MAX_ERROR_X and gpsinfo.epy < MAX_ERROR_Y and gpsinfo.eps < MAX_ERROR_S:
            self.__has_lock = True
        self.__lock.release()
        self.__update_tracklog()




