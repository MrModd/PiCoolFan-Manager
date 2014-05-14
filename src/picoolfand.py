#!/usr/bin/python

##########################################################################
# PiCoolFan Manager by MrModd
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

import subprocess #For Popen
import time #For sleep
import os, sys, getopt, signal
from systemd import journal

################### CONFIGURE NEXT LINES #################################

# Modify next line to set temperature thresholds:
#   -Turn fan off if temperature < thresholds[0]
#   -Fan at 25% if temperature < thresholds[1]
#   -Fan at 50% if temperature < thresholds[2]
#   -Fan at 75% if temperature < thresholds[3]
#   -If temperature >= thresholds[3] then fan at 100%
thresholds = [40, 48, 56, 60]
#             ^   ^   ^   ^
#             0   1   2   3

# Set interval of updates
delay = 10 #Seconds

################# DON'T MODIFY ANYTHING NEXT THIS LINE ####################

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
	file = open("/sys/class/thermal/thermal_zone0/temp", "r")
	temp = file.read()
	file.close()
	return float(temp)/1000

def daemonize():
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
		sys.stderr.write(str(err) + "\n")
		sys.exit(1)

def handler(signum, frame):
	getResult(["i2cset", "-y", bus, device, address, speeds[0], "b"])
	sys.exit(0)



daemon=False
try:
	opts, args = getopt.getopt(sys.argv[1:], "d", ["daemon"])
except getopt.GetoptError as err:
	sys.stderr.write(str(err) + "\n")
	sys.stderr.write("Usage: " + sys.argv[0] + " [-d --daemon]\n")
	sys.exit(1)
for opt, arg in opts:
	if opt in ('-d', '--daemon'):
		journal.send("Detaching.\n")
		daemonize()
		daemon=True

signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGQUIT, handler)
signal.signal(signal.SIGABRT, handler)
signal.signal(signal.SIGINT, handler)

currentSpeed = 0 #Set starting fan speed to OFF
oldTemp = 10 #Arbitrary starting temperature
getResult(["i2cset", "-y", bus, device, address, speeds[0], "b"])
if (daemon==False):
	print("Fan initialized (initial speed set to OFF).")
else:
	journal.send("Fan initialized (initial speed set to OFF).")

while 1:
	time.sleep(delay)
	newTemp = getTemp()
	if (newTemp - oldTemp > margin or oldTemp - newTemp > margin):
		i = 0
		while (i < 5):
			if (i < 4 and newTemp < thresholds[i]):
				if (i != currentSpeed):
					getResult(["i2cset", "-y", bus, device, address, speeds[i], "b"])
					oldTemp = newTemp
					currentSpeed = i
					if (daemon==False):
						print("Temperature %3.2f°C, new speed %s." % (newTemp, speedLabel[i]))
					else:
						journal.send("Temperature %3.2f°C, new speed %s." % (newTemp, speedLabel[i]))

				break
			elif (i == 4):
				if (i != currentSpeed):
					getResult(["i2cset", "-y", bus, device, address, speeds[i], "b"])
					oldTemp = newTemp
					currentSpeed = i
					if (daemon==False):
						print("Temperature %3.2f°C, new speed %s." % (newTemp, speedLabel[i]))
					else:
						journal.send("Temperature %3.2f°C, new speed %s." % (newTemp, speedLabel[i]))
			i = i+1
