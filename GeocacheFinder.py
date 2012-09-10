#!/usr/bin/env python
import os
import sys
import math
import gislib
from pyspatialite import dbapi2 as db
from lcdproc.server import Server
import unicodedata
import time
import gps
import RPi.GPIO as GPIO

def isAngleWithin(a1, a2, threshold):
  a_min = min(a1, a2)
  a_max = max(a1, a2)
  if (a_max-a_min) > threshold:
    return ((a_min+360) - a_max) <= threshold
  return (a_max - a_min) <= threshold

def calculateBearing(start, target):
  lat1, lon1 = map(math.radians, start)
  lat2, lon2 = map(math.radians, target)
  dLon = lon2-lon1
  y = math.sin(dLon) * math.cos(lat2)
  x = math.cos(lat1)*math.sin(lat2) - \
      math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
  return (math.degrees(math.atan2(y, x))+180) % 360

def humanizeBearing(bearing):
  # symbols = ['N','NE','E','SE','S','SW','W','NW']
  symbols = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
  step = 360.0 / len(symbols) 
  for i in range(len(symbols)):
    if isAngleWithin(i*step, bearing, step/2):
      return symbols[i]

class CacheDatabase:
  def __init__(self, dbfile, searchRadius, closeRadius):
    self.__conn = db.connect(dbfile)
    self.__searchRadius = searchRadius
    self.__closeRadius = closeRadius
  
  def findNearest(self, lat, lon, bearing, speed):
    while 1:
      print "searching", bearing, speed, self.__searchRadius
      result = self.findNearest_helper(lat, lon, bearing, speed) 
      if result:
        self.__searchRadius = result['distance'] * 1.5
        return result
      else:
        self.__searchRadius *= 2
        print "doubling radius", self.__searchRadius

  def findNearest_helper(self, lat, lon, bearing, speed):
    cur = self.__conn.cursor()

    # SQL to define a circle around the home point with a given radius
    radius = self.__searchRadius / 111319.0
    circle = 'BuildCircleMbr(%f, %f, %f)' % (lat, lon, radius)

    # SQL to calculate distance between geocache and home point
    dist = 'greatcirclelength(geomfromtext("linestring(" || x(location) || " " || y(location) || ", %f %f)", 4326))' % (lat, lon)
    dist2 = 'geodesiclength(geomfromtext("linestring(" || x(location) || " " || y(location) || ", %f %f)", 4326))' % (lat, lon)

    # Query for caches within circle and order by distance
    rs = cur.execute('select code, description, x(location), y(location), %(dist)s from gc where MbrWithin(location, %(searchCircle)s) order by %(dist)s' % {'dist':dist2, 'searchCircle':circle})

    data = []
    for row in rs:
      coord = (row[2], row[3])
      data.append({
        'code': row[0],
        'description': row[1],
        'distance_db': int(row[4]),
        # I more reliable (I think) distance calcs from this function
        # rather than the database
        'distance': int(1000.0 * gislib.getDistance(coord, (lat, lon))),
        'human_bearing': humanizeBearing(calculateBearing(coord, (lat, lon))), 
        'bearing': calculateBearing(coord, (lat, lon)),
        'lat': row[2],
        'lon': row[3]
        })

    if len(data) == 0: return None

    # sort by distance again since we aren't using the database distance
    # this should be removed if I switch back to using the Spatialite dist.
    data.sort(key=lambda x: x['distance'])


    # If first cache is within closeRadius return that 
    if data[0]['distance'] < self.__closeRadius:
      print "cache within ", self.__closeRadius, "m"
      return data[0] 

    # search angle varies with speed.  At low speeds we look
    # for caches all around us while at higher speeds we look 
    # only right in front of us.
    if (speed < .2778 * 60): bearingError = 180
    else: bearingError = 10
    print ("speed", speed, bearingError)

    # sift through caches looking for closest one within our travel path
    for row in data:
      if isAngleWithin(bearing, row['bearing'], bearingError):
        return row

    return None

def main(db):
  print "GeocacheFinder Starting..." 
  gps_session = gps.gps(mode=gps.WATCH_ENABLE)

  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(22, GPIO.OUT)
  GPIO.output(22, GPIO.LOW)

  lcd = Server()
  lcd.start_session()

  s = lcd.add_screen("cache")
  s.set_heartbeat("off")
  s.set_duration(10)
  s.set_priority("hidden")

  sl = lcd.add_screen("latlon")
  sl.set_duration(2)
  lat_widget = sl.add_string_widget("lat","", y=1)
  lon_widget = sl.add_string_widget("lon","", y=2)

  title = s.add_scroller_widget("title",1,1,16,1,"h",1,"" )
  code = s.add_string_widget("code", "", y=2)
  dist = s.add_string_widget("dist", "", y=2, x=9)
  bearing_widget = s.add_string_widget("bearing", "", y=2, x=14)

  lat, lon = (0,0)
  bearing = 0
  speed = 0
  ledState = GPIO.LOW

  while 1:
    # process all waiting GPS updates
    while gps_session.waiting():
      gpsinfo = gps_session.next()
      if gpsinfo["class"] == 'TPV':
        if 'track' in gpsinfo.keys():
          bearing = gpsinfo.track
        if 'lat' in gpsinfo.keys():
          lat = gpsinfo.lat
        if 'lon' in gpsinfo.keys():
          lon = gpsinfo.lon
        if 'speed' in gpsinfo.keys():
          speed = gpsinfo.speed
        lat_widget.set_text("lat: %0.6f" % lat)
        lon_widget.set_text("lon: %0.6f" % lon)
        if 'time' in gpsinfo.keys():
          print gpsinfo['time'], bearing, lat, lon, speed

    # find closest cache based on lat, lon, and bearing/speed
    closest = db.findNearest(lat, lon, bearing, speed)

    if closest:
      print closest['code'], closest['distance'], closest['bearing'], closest['lat'], closest['lon']
      s.set_priority("foreground")
      title.set_text(closest['description'].encode('ascii'))
      code.set_text(closest['code'].encode('ascii'))
      if closest['distance'] > 1000:
        dist.set_text('%0.0fkm' % (closest['distance']/1000.0))
      else:
        dist.set_text('%0.0fm' % closest['distance'])
      if closest['distance'] < 300:
        if ledState == GPIO.HIGH:
          ledState = GPIO.LOW
        else:
          ledState = GPIO.HIGH
      else:
        ledState = GPIO.LOW
      GPIO.output(22, ledState)
      bearing_widget.set_text(closest['human_bearing'])
    else:
      s.set_priority("hidden")

if __name__=='__main__':
  db = CacheDatabase('db.sqlite', 5000, 100)
  main(db)

    
