#!/usr/bin/env python

import os
import string
import time
import lib.gislib as gislib
from lib.ledhandler import LedHandler, LED_ON, LED_OFF
from lib.gpshandler import GpsHandler
from lib.geocachefinder import GeocacheFinder
from lib.geocachedisplay import GeocacheDisplay
from lib.geocacheloader import GeocacheLoader
from lib.tracklogexporter import TracklogExporter
from lib.dashboard import Dashboard
import lib.databaseinit
from pyspatialite import dbapi2 as spatialite

## CONFIGURATION ##########################################################
GEOCACHE_SOURCE = '/var/autofs/removeable/sda1/cacheberrypi/nav.csv'
TRACKLOG_TARGET = 'tracks'
TRACKLOG_EXPORT_TARGET = '/var/autofs/removeable/sda1/cacheberrypi/tracks/'
DATABASE_FILENAME = 'geocaches.sqlite'
LED_PINS = [16,18,22] #GPIO23,24,25
LED_SEARCH_STATUS = 2
LED_CLOSE = 1
###########################################################################

def mainloop(led, gps, finder, geocache_display, dashboard):
  while 1:
    # grab current state from GPS and update finder location
    gps_state = gps.state()
    finder.update_position(gps_state['p'])
    finder.update_speed(gps_state['s'])
    finder.update_bearing(gps_state['b'])

    try:
      clock = time.strptime(gps_state['t'], '%Y-%m-%dT%H:%M:%S.000Z')
    except:
      clock = None

    dashboard.update(
        clock,
        gps_state['s'], 
        gislib.humanizeBearing(gps_state['b']))

    # grab current closest cache 
    closest = finder.closest()

    if closest:
      distance = gislib.getDistance(gps_state['p'], closest['position']) * 1000
      geocache_display.update(
          closest["description"],
          closest["code"],
          gislib.humanizeBearing(gps_state['b']) if gps_state['s'] > 2 else '',
          gislib.humanizeBearing(gislib.calculateBearing(gps_state['p'], closest['position'])),
          distance
          )

      geocache_display.show(distance < 1000)  #if within 1km show in foreground (on top)

      # blink close light if we are not moving and within 100m or if we are moving and
      # our ETA is within 45 seconds.
      if (gps_state['s'] < 10 and distance < 100) or \
        (gps_state['s'] >= 10 and (float(distance)/gps_state['s']) < 45):
        led.toggle(LED_CLOSE)
      else:
        led.set(LED_CLOSE, LED_ON)

    else:
      geocache_display.hide()

    time.sleep(.5)
  
if __name__=='__main__':

  if not os.path.exists(DATABASE_FILENAME):
    lib.databaseinit.create(DATABASE_FILENAME)

  led = LedHandler(LED_PINS)

  gps = GpsHandler(TRACKLOG_TARGET)
  gps.start()

  tracklogexport = TracklogExporter(TRACKLOG_TARGET, TRACKLOG_EXPORT_TARGET)
  tracklogexport.start()

  finder = GeocacheFinder(DATABASE_FILENAME, lambda: led.toggle(LED_SEARCH_STATUS))
  finder.start()

  geocache_display = GeocacheDisplay()

  loader = GeocacheLoader(DATABASE_FILENAME, GEOCACHE_SOURCE, 
      lambda: finder.pause(),
      lambda: finder.unpause())
  loader.start()

  dashboard = Dashboard()

  mainloop(led, gps, finder, geocache_display, dashboard)
