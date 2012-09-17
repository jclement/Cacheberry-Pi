#!/usr/bin/env python

import os
import string
import time
import lib.gislib as gislib
from lib.ledhandler import LedHandler, LED_ON, LED_OFF
from lib.gpshandler import GpsHandler
from lib.geocachefinder import GeocacheFinder
from lib.geocachedisplay import GeocacheDisplay
from pyspatialite import dbapi2 as spatialite

## CONFIGURATION ##########################################################
DATABASE_FILENAME = 'geocaches.sqlite'
LED_PINS = [22]
LED_SEARCH_STATUS = 0
###########################################################################

def mainloop(led, gps, finder, geocache_display):
  while 1:
    # grab current state from GPS and update finder location
    gps_state = gps.state()
    finder.update_position(gps_state['p'])
    finder.update_speed(gps_state['s'])
    finder.update_bearing(gps_state['b'])

    # grab current closest cache 
    closest = finder.closest()

    if closest:
      distance = gislib.getDistance(gps_state['p'], closest['position']) * 1000
      geocache_display.update(
          closest["description"],
          closest["code"],
          gislib.humanizeBearing(gps_state['b']),
          gislib.humanizeBearing(gislib.calculateBearing(gps_state['p'], closest['position'])),
          distance
          )
      geocache_display.show(distance < 1000)  #if within 1km show in foreground (on top)
    else:
      geocache_display.hide()
  
if __name__=='__main__':

  led = LedHandler(LED_PINS)

  gps = GpsHandler()
  gps.start()

  db = spatialite.connect(DATABASE_FILENAME)

  finder = GeocacheFinder(DATABASE_FILENAME, lambda: led.toggle(LED_SEARCH_STATUS))
  finder.start()

  geocache_display = GeocacheDisplay()

  mainloop(led, gps, finder, geocache_display)
