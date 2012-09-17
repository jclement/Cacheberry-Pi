import os
import sys
import time
from lcdproc.server import Server
from threading import Thread
import pyspatialite.dbapi2 as spatialite

class GeocacheLoader(Thread):
  def __init__(self, database_filename, source, pause_func, unpause_func):
    Thread.__init__(self)
    self.daemon = True
    self.__database_filename = database_filename
    self.__source = source
    self.__pause_func = pause_func
    self.__unpause_func = unpause_func
    self.__lcd = Server()
    self.__lcd.start_session()
    self.__screen = self.__lcd.add_screen("loader")
    self.__screen.set_priority("hidden")
    self.__title_widget = self.__screen.add_string_widget("title","",y=1)
    self.__progress_widget = self.__screen.add_hbar_widget("status",y=2,length=0)

  def run(self):
    db = spatialite.connect(self.__database_filename)
    while 1:
      # wait until memory stick is inserted
      while not os.path.exists(self.__source):
        time.sleep(5)

      self.__pause_func()

      cur = db.cursor()

      self.__progress_widget.set_length(0)
      self.__screen.set_priority("foreground")

      # read entire file into memory so we can do nice progress bar
      self.__title_widget.set_text("Reading") 
      f = open(self.__source,"r")
      header = f.readline()
      lines = f.readlines()
      f.close()

      self.__title_widget.set_text("Clearing")
      cur.execute("delete from gc");

      self.__title_widget.set_text("Loading")
      position = 0
      for line in lines:
        position = position + 1
        if position % 20 == 0:
          self.__progress_widget.set_length((float(position)/len(lines)) * (5*16))
        Name,Latitude,Longitude,Description,URL,Type,Container,Diff,Terr = line.split('\t')
        cur.execute("insert into gc (code, description, type, container, diff, terr, location) values (?,?,?,?,?,?,MakePoint(?, ?, 4326))", 
            (Name, Description.replace("'", ""), Type, Container, float(Diff), float(Terr), float(Latitude), float(Longitude)));

      db.commit()
      cur.close()

      self.__screen.set_priority("hidden")

      self.__unpause_func()

      # wait until memory stick is removed
      while os.path.exists(self.__source):
        time.sleep(5)
