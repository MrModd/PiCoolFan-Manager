#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import os, sys

BUS='1'
DEVICE='0x6c'

funcFields = {} # Defined below
fieldmodes = {'0': 'b', '1': 'b', '2': 'w', '4': 'w', '6': 'b', '7': 'b',
	      '8': 'w', '10': 'w', '12': 'w', '14': 'b', '15': 'b'}

## Exception class ##
class PopenException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return str(self.value)



## Functions ##

def is_root():
	return os.geteuid() == 0

def getResult(command):
	p = Popen(command, stdout=PIPE, stderr=PIPE)
	if p.wait() != 0:
		raise PopenException('Error: ' + command[0] + ' returned a non zero value')
	stream = p.stdout.read()
	#stream is a bytes array!!!
	#Convert to string
	res = stream.decode('utf-8')
	return res

def i2cset(address, value):
	getResult(['i2cset', '-y', BUS, DEVICE, address, value, fieldmodes[address]])

def i2cget(address):
	command = ['i2cget', '-y', BUS, DEVICE, address, fieldmodes[address]]
	return getResult(command)

def showGeneralHelp():
	print('PiCoolFan manager by MrModd')
	print('Usage: ' + __file__  + ' {get|set} FIELD [PARAMETER]\n')
	print("Fields:")
	for f in funcFields.keys():
		print('\t' + f)



## Function per mode ##

def Mode(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('0').replace('\n','')
			message = 'FAN: '
			if ret == '0x00':
				message += 'OFF'
			elif ret == '0x01':
				message += 'ON'
			elif ret == '0x02':
				message += 'AUTO'
			else:
				message = ret
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1 or not values[0] in ['0', '1', '2']:
			print('Accepted values:')
			print('\t0: FAN OFF')
			print('\t1: FAN ON')
			print('\t2: FAN AUTO')
			sys.exit(1)
		try:
			i2cset('0', values[0])
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
		
def Speed(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('1').replace('\n','')
			message = 'FAN: '
			if ret == '0x00':
				message += 'OFF'
			elif ret == '0x01':
				message += '100%'
			elif ret == '0x02':
				message += '25%'
			elif ret == '0x03':
				message += '50%'
			elif ret == '0x04':
				message += '75%'
			else:
				message = ret
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1 or not values[0] in ['0', '1', '2', '3', '4']:
			print('Accepted values:')
			print('\t0: FAN OFF')
			print('\t1: FAN 100%')
			print('\t2: FAN 25%')
			print('\t3: FAN 50%')
			print('\t4: FAN 75%')
			sys.exit(1)
		try:
			i2cset('1', values[0])
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)

def Ctemp(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('2').replace('\n','')
			message = 'Temperature: '
			message += ret[2:]
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		print('Operation forbidden.')
		sys.exit(1)

def TTemp(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('4').replace('\n','')
			message = 'Threshold temperature: '
			message += ret[2:]
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1:
			print('Must be an integer value (eg. 42).')
			sys.exit(1)
		try:
			temp = int(values[0])
			message = '0x' + str(temp)
			i2cset('4', message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
		except ValueError:
			print('Must be an integer value (eg. 42).')
			sys.exit(1)

def Scale(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('6').replace('\n','')
			message = 'Temperature scale: '
			if ret == '0x00':
				message += 'Celsius'
			elif ret == '0x01':
				message += 'Fahrenheit'
			else:
				message = ret
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1 or not values[0] in ['celsius', 'fahrenheit']:
			print('Accepted values:')
			print('\tcelsius')
			print('\tfahrenheit')
			sys.exit(1)
		try:
			message = '0' if values[0] == 'celsius' else '1'
			i2cset('6', message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)

def Fstat(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('7').replace('\n','')
			message = 'FAN status: '
			if ret == '0x00':
				message += 'Not running'
			elif ret == '0x01':
				message += 'Running'
			else:
				message = ret
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		print('Operation forbidden.')
		sys.exit(1)

def Vccpi(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('8').replace('\n','')
			message = 'Current voltage: '
			volt = int(ret[2:])
			volt /= 100
			message += str(volt)
			message += 'V'
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		print('Operation forbidden.')
		sys.exit(1)

def Vccupi(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('10').replace('\n','')
			message = 'Upper limit voltage threshold: '
			volt = int(ret[2:])
			volt /= 100
			message += str(volt)
			message += 'V'
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1:
			print('Must be a positive float value (eg. 5.2).')
			sys.exit(1)
		try:
			volt = float(values[0])
			volt *= 100
			message = '0x'
			message += str(int(volt))[-3:]
			i2cset('10', message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
		except ValueError:
			print('Must be a positive float value (eg. 5.2).')
			sys.exit(1)

def Vccdpi(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('12').replace('\n','')
			message = 'Lower limit voltage threshold: '
			volt = int(ret[2:])
			volt /= 100
			message += str(volt)
			message += 'V'
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		if len(values) != 1:
			print('Must be a positive float value (eg. 4.8).')
			sys.exit(1)
		try:
			volt = float(values[0])
			volt *= 100
			message = '0x'
			message += str(int(volt))[-3:]
			i2cset('12', message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
		except ValueError:
			print('Must be a positive float value (eg. 4.8).')
			sys.exit(1)

def Version(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('14').replace('\n','')
			message = 'Hardware version: '
			message += ret[2]
			message += '\nSoftware version: '
			message += ret[3]
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		print('Operation not permitted')
		print('Please read the documentation and use i2cset command.')
		sys.exit(1)

def Rtccf(mode, values=[]):
	if mode == 'get':
		try:
			ret = i2cget('14').replace('\n','')
			message = 'RTCC Timer multipler: '
			message += ret
			print(message)
		except PopenException as e:
			sys.stderr.write(str(e) + '\n')
			sys.exit(1)
	else:
		print('Operation not permitted')
		print('Please read the documentation and use i2cset command.')
		sys.exit(1)



# Function to call when specific field was invoked
funcFields = {'mode': Mode, 'speed': Speed, 'ctemp': Ctemp, 'ttemp': TTemp,
	    'scale': Scale, 'fstat': Fstat, 'vcc_pi': Vccpi, 'vcc_upi': Vccupi,
	    'vcc_dpi': Vccdpi, 'version': Version, 'rtccf': Rtccf}



## Entry point ##

if len(sys.argv) <= 2:
	sys.stderr.write('Invalid arguments.\n')
	showGeneralHelp()
	sys.exit(1)

if not sys.argv[1] in ['get', 'set'] or not sys.argv[2] in funcFields.keys():
	sys.stderr.write('Invalid arguments.\n')
	showGeneralHelp()
	sys.exit(1)

if not is_root():
	sys.stderr.write('You must be root to use this program.\n')
	sys.exit(1)

funcFields[sys.argv[2]](sys.argv[1], sys.argv[3:])

sys.exit(0)

