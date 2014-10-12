#!/usr/bin/python

##########################################################################
# PiCoolFan Manager by MrModd
# Copyright (C) 2014  Federico 'MrModd' Cosentino (http://mrmodd.it/)
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

from subprocess import Popen, PIPE
import time #For sleep
import os, sys, getopt, signal

import pilog
import piconfig



# Default configuration path
CONFIGPATH = '/etc/default/picoolfan-manager'
# Temp sensor file
TEMPSENSOR = '/sys/class/thermal/thermal_zone0/temp'


## Exception classes
class PopenException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return str(self.value)

class FileException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return str(self.value)



## Functions ##

def getResult(command):
	p = Popen(command, stdout=PIPE, stderr=PIPE)
	if p.wait() != 0:
		raise PopenException('Error: ' + command[0] + ' returned a non zero value')
	stream = p.stdout.read()
	#stream is a bytes array!!!
	#Convert to string
	res = stream.decode('utf-8')
	return res

def getTemp():
	try:
		file = open(TEMPSENSOR, 'r')
	except OSError:
		raise FileException('Error: cannot find temp sensor')
	
	temp = file.read()
	file.close()
	return float(temp)/1000

def daemonize():
	try:
		pid = os.fork()
		if (pid > 0):
			sys.exit(0)
		os.chdir('/')
		os.setsid()
		os.umask(0)
		#sys.stdin = '/dev/null'
		#sys.stdout = '/dev/null'
		#sys.stderr = '/dev/null'
	except OSError as err:
		sys.stderr.write(str(err) + '\n')
		sys.exit(1)

def handler(signum, frame):
	# Restore initial fan speed (OFF) before exiting
	try:
		conf = piconfig.getConfig(CONFIGPATH)
	except Exception as e:
		sys.exit(1)
	
	try:
		getResult(['i2cset', '-y', conf['bus'], conf['device'], conf['address'], conf['speeds'][0], 'b'])
	except PopenException:
		sys.exit(1)
	
	sys.exit(0)

def printMessage(message, daemon):
	if not daemon:
		print(message)
	else:
		pilog.log(message)


## Entry point ##

# Read arguments
daemon=False
try:
	opts, args = getopt.getopt(sys.argv[1:], 'dc:', ['daemon', 'config'])
except getopt.GetoptError as err:
	sys.stderr.write(str(err) + '\n')
	sys.stderr.write('Usage: ' + sys.argv[0] + ' [-d --daemon] [-c --config <config file>]\n')
	sys.exit(1)
for opt, arg in opts:
	if opt in ('-d', '--daemon'):
		pilog.log('Detaching.\n')
		daemonize()
		daemon=True
	elif opt in ('-c', '--config'):
		CONFIGPATH = arg

try:
	conf = piconfig.getConfig(CONFIGPATH)
except Exception as e:
	printMessage(str(e), daemon)
	sys.exit(1)

# Handle signals
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGQUIT, handler)
signal.signal(signal.SIGABRT, handler)
signal.signal(signal.SIGINT, handler)

# Initializing fan speed to OFF
currentSpeed = 0 #Set starting fan speed to OFF
oldTemp = 10 #Arbitrary starting temperature
try:
	getResult(['i2cset', '-y', conf['bus'], conf['device'], conf['address'], conf['speeds'][0], 'b'])
except PopenException as e:
	printMessage(str(e), daemon)
	sys.exit(1)

printMessage('Fan initialized (initial speed set to ' + conf['speedLabels'][0]  + ').', daemon)

# Main loop
while 1:
	time.sleep(conf['delay'])
	newTemp = oldTemp
	try:
		newTemp = getTemp()
	except FileException as e:
		printMessage(str(e), daemon)
		sys.exit(1)
	if newTemp - oldTemp > conf['margin'] or oldTemp - newTemp > conf['margin']:
		i = 0
		while i < 5:
			if i < 4 and newTemp < conf['thresholds'][i]:
				if i != currentSpeed:
					try:
						getResult(['i2cset', '-y', conf['bus'], conf['device'], conf['address'], conf['speeds'][i], 'b'])
					except PopenException as e:
						printMessage(str(e), daemon)
						sys.exit(1)
					oldTemp = newTemp
					currentSpeed = i
					printMessage('Temperature %3.2f°C, new speed %s.' % (newTemp, conf['speedLabels'][i]), daemon)

				break
			elif i == 4:
				if i != currentSpeed:
					try:
						getResult(['i2cset', '-y', conf['bus'], conf['device'], conf['address'], conf['speeds'][i], 'b'])
					except PopenException as e:
						printMessage(str(e), daemon)
						sys.exit(1)
					oldTemp = newTemp
					currentSpeed = i
					printMessage('Temperature %3.2f°C, new speed %s.' % (newTemp, conf['speedLabels'][i]), daemon)
			i = i+1
