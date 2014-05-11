#!/usr/bin/python

##########################################################################
# PiCoolFan Manager v1.0 by MrModd
# Copyright (C) 2014  Federico "MrModd" Cosentino (http://mrmodd.it/)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import subprocess
import time
import os, sys, getopt, signal

thresholds = [40, 48, 56, 60]

#Don't modify these
bus = "1"
device = "0x6c"
address = "1"
speeds = ["0", "2", "3", "4", "1"]
speedLabel = ["OFF", "25%", "50%", "75%", "100%"]
margin = 2



def getResult(command):
	stream = subprocess.Popen(command, stdout=subprocess.PIPE).stdout.read()
	#stream is a bytes array!!!
	#Convert to string
	res = stream.decode("utf-8")
	return res

def getTemp():
	temp = getResult(["awk", "{printf \"%3.1f\", $1/1000}", "/sys/class/thermal/thermal_zone0/temp"])
	return float(temp)

def daemonize():
	print("Detaching\n")
	try:
		pid = os.fork()
		if (pid > 0):
			sys.exit(0)
		os.chdir("/")
		os.setsid()
		os.umask(0)
		#sys.stdin = '/dev/null'
		#sys.stdout = '/dev/null'
		#sys.stderr = '/dev/null'
	except OSError as err:
		sys.stderr.write(str(err))
		sys.exit(1)

def handler(signum, frame):
	print("Exiting\n")
	getResult(["i2cset", "-y", bus, device, address, speeds[0], "b"])
	sys.exit(0)



try:
	opts, args = getopt.getopt(sys.argv[1:], "d", ["daemon"])
except getopt.GetoptError as err:
	sys.stderr.write(str(err) + "\n")
	sys.stderr.write("Usage: " + sys.argv[0] + " [-d --daemon]\n")
	sys.exit(1)
for opt, arg in opts:
	if opt in ('-d', '--daemon'):
		daemonize()

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGQUIT, handler)
signal.signal(signal.SIGABRT, handler)
signal.signal(signal.SIGINT, handler)

currentSpeed = 0 #Set starting fan speed to OFF
oldTemp = 10 #Arbitrary starting temperature
getResult(["i2cset", "-y", bus, device, address, speeds[0], "b"])
print("Fan initialized")

while 1:
	time.sleep(2)
	newTemp = getTemp()
	if (newTemp - oldTemp > margin or oldTemp - newTemp > margin):
		i = 0
		while (i < 5):
			if (i < 4 and newTemp < thresholds[i]):
				if (i != currentSpeed):
					getResult(["i2cset", "-y", bus, device, address, speeds[i], "b"])
					oldTemp = newTemp
					currentSpeed = i
					print("Temperature %s°C, new speed %s" % (newTemp, speedLabel[i]))
				break
			elif (i == 4):
				if (i != currentSpeed):
					getResult(["i2cset", "-y", bus, device, address, speeds[i], "b"])
					oldTemp = newTemp
					currentSpeed = i
					print("Temperature %s°C, new speed %s" % (newTemp, speedLabel[i]))
			i = i+1
