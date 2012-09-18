import os
import fcntl
import glob
import sys
import time
from lcdproc.server import Server
from threading import Thread
import shutil

class TracklogExporter(Thread):
  def __init__(self, tracklog_source_dir, tracklog_export_dir):
    Thread.__init__(self)
    self.daemon = True
    self.__tracklog_source_dir = tracklog_source_dir
    self.__tracklog_export_dir = tracklog_export_dir
    self.__lcd = Server()
    self.__lcd.start_session()
    self.__screen = self.__lcd.add_screen("exporter")
    self.__screen.set_priority("hidden")
    self.__title_widget = self.__screen.add_string_widget("title","",y=1)
    self.__progress_widget = self.__screen.add_hbar_widget("status",y=2,length=0)

  def __test_lock(self, file):
        f = open(file, 'r')
        try:
          print file, fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
          ret = True
        except:
          ret = False
        f.close()
        return ret

  def run(self):
    while 1:
      # wait until memory stick is inserted
      while not os.path.exists(self.__tracklog_export_dir):
        time.sleep(5)

      self.__progress_widget.set_length(0)
      self.__screen.set_priority("foreground")
      self.__title_widget.set_text("Moving Logs") 

      files = glob.glob(os.path.join(self.__tracklog_source_dir, "*.csv"))
      position = 0
      for file in files:
        if self.__test_lock(file):
          print position, file
          shutil.move(file, self.__tracklog_export_dir)
        self.__progress_widget.set_length((float(position)/len(files)) * (5*16))
        position = position + 1

      self.__screen.set_priority("hidden")

      # wait until memory stick is removed
      while os.path.exists(self.__tracklog_export_dir):
        time.sleep(5)

if __name__=='__main__':
  f = open('source/a.csv','w')
  fcntl.flock(f, fcntl.LOCK_EX)
  f.write('test')
  e = TracklogExporter("source","target")
  e.run()
