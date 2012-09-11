Cacheberry-Pi
=============

Cacheberry Pi is a geocaching assistant built upon the Raspberry Pi platform.

It's intended to be a permanent fixture in the car and alert you of nearby caches (when stopped) or along your route (when driving).  The intent is not to replace your handheld GPSr but to complement it. 

See an overview [Video on YouTube](http://youtu.be/bwD6K2EeeV8)
# Features #
* Smart Search: depending on speed and direction of travel
* Ability to maintain a database of 20k+ geocaches
* Easy syncing of cache lists with GSAK via thumb drive
* Automatic tracklog recording and syncing with thumb drive

# Hardware #
* [RaspberryPi B](http://canada.newark.com/raspberry-pi/raspbrry-pcba/raspberry-pi-model-b-board-only/dp/83T1943)
* [Arduino IIC / I2C Serial 2.6" LCD 1602 Module Display](http://dx.com/p/arduino-iic-i2c-twi-spi-serial-lcd-1602-module-electronic-building-block-136922?item=4)
* [Holux M-215 GPRr](http://dx.com/p/genuine-holux-usb-gps-receiver-black-106778?item=8) - Likely almost any other NMEA GPS will suffice
* 8GB SD Card
* 12V USB Charger + MicroUSB cable

# Software Requirements #
* Python 2.7
* [GPsd](http://www.catb.org/gpsd/) - Available through APT
* [PySpatialite](http://code.google.com/p/pyspatialite/) - Available through APT
* [LCDProc] (http://www.lcdproc.org/) - Available through APT (required custom display driver)                                                      
* [RPi.GPIO] (http://pypi.python.org/pypi/RPi.GPIO) 
* [AutoFS] (http://www.autofs.org/) - Available through APT
