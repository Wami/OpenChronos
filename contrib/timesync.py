#!/usr/bin/python
#synctime - synchronize your chronos watch to your computer
#
#
# Copyright (c) 2010 Sean Brewer 
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
#
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
#You can contact me at seabre986@gmail.com or on reddit (seabre) if you want.
#
#****TONS**** of mistakes in the last version. Sorry about that everybody.

import serial
import datetime
import array
from time import sleep
def splitIntoNPieces(s,n):
    return [s[i:i+n] for i in range(0, len(s), n)]

def makeByteString(arr):
    return array.array('B', arr).tostring()

def startAccessPoint():
    return makeByteString([0xFF, 0x07, 0x03])
    

def stopAccessPoint():
    return makeByteString([0xFF, 0x09, 0x03])


"""
kinda messy

Here's how this works.
A packet for the watch sync looks like this:
FF 31 16 03 94 34 01 07 DA 01 17 06 1E 00 00 00 00 00 00 00 00 00
You have the first four bytes which we're just going to ignore.
The 5th byte represents the hour you want to sync to.
The 6th byte represents the minute you want to sync to.
The 7th byte represents the second you want to sync to.
The 9th byte represents the year you want to sync to.
The 10th byte represents the month you want to sync to.
The 11th byte represents the day you want to sync to.
THe 14th and 15th bytes represent the temperature in celcius.
The 16th and 17th bytes represent the altitude in meters.

It also stores some of these values in some unusual (to me) ways.

For hour, the value 0x80 needs to be added to the 24hr representation of the desired
hour to sync to.

For year the value 0x700 needs to be subtracted from the desired year to sync to.

For temperature, the temperature (in celcius) needs to be multiplied by 0x0A.

Caveat emptor: There is no error checking implemented to check for valid ranges.
"""
def syncTimeDateTempAlt(hour,minute,second,month,day,year,tempCelcius,altMeters):
    adjHour = hour + 0x80 #assumes 24h based time entry
    adjYear = year - 0x700
    adjTempCelcius = tempCelcius * 0x0A
    alarmHour = 20
    alarmMin = 30

    cmd = [0xFF, 0x31, 0x16, 0x03,adjHour,minute,second,0x07,adjYear,month,day,alarmHour,alarmMin]

    hexCelcius = hex(adjTempCelcius)[2:].zfill(4)
    hexMeters = hex(altMeters)[2:].zfill(4)

    for i in splitIntoNPieces(hexCelcius,2):
        cmd.append(int(i,16))
    for i in splitIntoNPieces(hexMeters,2):
        cmd.append(int(i,16))
    
    for i in xrange(0,5):
        cmd.append(0)
   
    return makeByteString(cmd)


#Open COM port 6 (check your system info to see which port
#yours is actually on.)
#argments are 5 (COM6), 115200 (bit rate), and timeout is set so
#the serial read function won't loop forever.
ser = serial.Serial('/dev/ttyACM0',115200,timeout=None)

#Start access point
ser.write(startAccessPoint())

#raw_input("Please turn your watch to sync mode and turn on the transceiver (though if the transciever is already on you may have to turn it off then on again), then press enter...")

while 1:
	time = datetime.datetime.now()
	ser.write(syncTimeDateTempAlt(time.hour,time.minute,time.second,time.month,time.day,time.year,20,0))
	sleep(10)
	ser.flushOutput()

#Need to pause to make sure the watch actually gets the sync packet
print "OK. Your watch should have been sync'd. Pausing for two seconds.."

sleep(2)

#The start access point command needs to come before the stop access point command
#in order for the access point to turn off.
ser.write(startAccessPoint())
ser.write(stopAccessPoint())
    
ser.close()
    
