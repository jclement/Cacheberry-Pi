#!/usr/bin/env python

# INSTALLATION ################################################################
# Just drop into /etc/network/ifup.d
# Make sure it's marked as executable. (ie. chmod 755 ifup-lcdproc.py)
###############################################################################

import os
import sys
import time
from lcdproc.server import Server
import socket
import fcntl
import struct

def get_ip_address(ifname):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return socket.inet_ntoa(fcntl.ioctl(
    s.fileno(),
    0x8915,  # SIOCGIFADDR
    struct.pack('256s', ifname[:15])
  )[20:24])

def main(interface):
  if interface == 'lo': return
  if interface == '--all': return

  lcd = Server()
  lcd.start_session()

  s = lcd.add_screen("ip")
  s.set_priority("alert")
  s.add_title_widget("title","Net (%s)" % interface)
  s.add_string_widget("ip",get_ip_address(interface),y=2)
  time.sleep(10)

if __name__=='__main__':
  iface = 'eth0'
  if os.environ.has_key('IFACE'):
    # if we are part if ifup.d fork so we don't freeze booting
    # we need to wait for LCDd anyways>
    iface = os.environ['IFACE']
    if os.fork() != 0: sys.exit()
    time.sleep(10)
  main(iface)
