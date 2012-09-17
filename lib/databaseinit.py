#!/usr/bin/env python

import pyspatialite.dbapi2 as spatialite

def create(dbfile):
    print "Initializing", dbfile
    conn = spatialite.connect(dbfile)
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
