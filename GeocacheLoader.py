#!/bin/env python

# ====================================================================
DBFILE = 'db.sqlite'
SOURCE_URL = 'https://dl.dropbox.com/u/120688/gsak/nav.csv'
# ====================================================================

import os
import sys
import urllib
from pyspatialite import dbapi2 as db

class GeocacheLoader:
  def __init__(self, dbfile, url):
    self.__url = url
    if not os.path.exists(dbfile):
      self.__db = self.initializeDatabase(dbfile)
    else:
      self.__db = db.connect(dbfile)
    self.printVersions()

  def initializeDatabase(self, dbfile):
    print "Initializing", dbfile
    conn = db.connect(dbfile)
    cur = conn.cursor()
    sql = 'SELECT InitSpatialMetadata()'
    cur.execute(sql)
    sql = 'CREATE TABLE gc ('
    sql += 'code TEXT NOT NULL PRIMARY KEY'
    sql += ', description TEXT NOT NULL'
    sql += ', type TEXT NOT NULL'
    sql += ', container TEXT NOT NULL'
    sql += ', diff FLOAT NOT NULL'
    sql += ', terr FLOAT NOT NULL'
    sql += ")"
    cur.execute(sql)
    sql = "SELECT AddGeometryColumn('gc', "
    sql += "'location', 4326, 'POINT', 'XY')"
    cur.execute(sql)
    cur.execute("select createspatialindex('gc', 'location')")
    conn.commit()
    cur.close()
    return conn

  def printVersions(self):
    cur = self.__db.cursor()
    rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
    for row in rs:
      msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
      print msg

  def refresh(self):
    print "Refreshing"
    f = urllib.urlopen(self.__url)
    f.readline()
    cur = self.__db.cursor()
    count=0
    cur.execute("delete from gc")
    for line in f.readlines():
      count+=1
      Name,Latitude,Longitude,Description,URL,Type,Container,Diff,Terr = line.split('\t')
      geom = "GeomFromText('POINT(%f,%f)')" % (float(Latitude), float(Longitude))
      geom = "MakePoint(%f,%f, 4326)" % (float(Latitude), float(Longitude))
      cur.execute("insert into gc (code, description, type, container, diff, terr, location) values ('%s', '%s', '%s', '%s', '%s', '%s', %s)" % 
          (Name, Description.replace("'", ""), Type, Container, float(Diff), float(Terr), geom));
    print "Loaded",count,"caches."
    self.__db.commit()
    cur.close()


if __name__=='__main__':
  GeocacheLoader(DBFILE, SOURCE_URL).refresh()

