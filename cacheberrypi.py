#!/usr/bin/env python

import os
import string
import time
from lib.ledhandler import LedHandler, LED_ON, LED_OFF
from lib.gpshandler import GpsHandler

## CONFIGURATION ##########################################################
DATABASE_FILENAME = 'geocaches.sqlite'
LED_PINS = [22]
###########################################################################

def mainloop(led, gps):
  while 1:
    print gps.state()
    time.sleep(1)
  
if __name__=='__main__':

  led = LedHandler(LED_PINS)

  gps = GpsHandler()
  gps.start()

  mainloop(led, gps)
