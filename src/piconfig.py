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

import sys

if sys.version_info.major >= 3:
	import configparser as ConfigParser
else:
	import ConfigParser
import json

####################### DEFAULT CONFIGURATION ############################

thresholds = [40, 48, 56, 60]
#             ^   ^   ^   ^
#             0   1   2   3

# Set interval of updates
delay = 10 #Seconds

bus = '1'
device = '0x6c'
address = '1'
speeds = ['0', '2', '3', '4', '1']
speedLabels = ['OFF', '25 percent', '50 percent', '75 percent', 'Full speed']
margin = 2

##########################################################################

class ConfigException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return str(self.value)

def getConfig(configPath):
	dirty = False
	Config = ConfigParser.ConfigParser()
	try:
		Config.read(configPath)
	except ConfigParser.InterpolationError:
		raise ConfigException('Invalid config file')

	configHash = {}

	# Global
	if not 'Global' in Config.sections():
		"""
		Config['Global'] = {
				'thresholds': json.dumps(thresholds),
				'delay': delay
		}
		"""
		Config.add_section('Global')
		dirty = True
	
	try:
		configHash['thresholds'] = json.loads(Config.get('Global', 'thresholds'))
	except ConfigParser.NoOptionError:
		configHash['thresholds'] = thresholds
		#Config['Global']['thresholds'] = json.dumps(thresholds)
		Config.set('Global', 'thresholds', json.dumps(thresholds))
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	try:
		configHash['delay'] = int(Config.get('Global', 'delay'))
	except ConfigParser.NoOptionError:
		configHash['delay'] = delay
		#Config['Global']['delay'] = delay
		Config.set('Global', 'delay', str(delay))
		dirty = True
	except ValueError:
		raise ConfigException('Invalid value for "delay" option')
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	# Advanced
	if not 'Advanced' in Config.sections():
		"""
		Config['Advanced'] = {
				'bus': bus,
				'device': device,
				'address': address,
				'speeds': json.dumps(speeds),
				'speedLabels': json.dumps(speedLabels),
				'margin': margin
		}
		"""
		Config.add_section('Advanced')
		dirty = True
	
	try:
		configHash['bus'] = Config.get('Advanced', 'bus')
	except ConfigParser.NoOptionError:
		configHash['bus'] = bus
		#Config['Advanced']['bus'] = bus
		Config.set('Advanced', 'bus', bus)
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))
	
	try:
		configHash['device'] = Config.get('Advanced', 'device')
	except ConfigParser.NoOptionError:
		configHash['device'] = device
		#Config['Advanced']['device'] = device
		Config.set('Advanced', 'device', device)
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	try:
		configHash['address'] = Config.get('Advanced', 'address')
	except ConfigParser.NoOptionError:
		configHash['address'] = address
		#Config['Advanced']['address'] = address
		Config.set('Advanced', 'address', address)
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	try:
		configHash['speeds'] = json.loads(Config.get('Advanced', 'speeds'))
	except ConfigParser.NoOptionError:
		configHash['speeds'] = speeds
		#Config['Advanced']['speeds'] = json.dumps(speeds)
		Config.set('Advanced', 'speeds', json.dumps(speeds))
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))
	
	try:
		configHash['speedLabels'] = json.loads(Config.get('Advanced', 'speedLabels'))
	except ConfigParser.NoOptionError:
		configHash['speedLabels'] = speedLabels
		#Config['Advanced']['speedLabels'] = json.dumps(speedLabels)
		Config.set('Advanced', 'speedLabels', json.dumps(speedLabels))
		dirty = True
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	try:
		configHash['margin'] = int(Config.get('Advanced', 'margin'))
	except ConfigParser.NoOptionError:
		configHash['margin'] = margin
		#Config['Advanced']['margin'] = margin
		Config.set('Advanced', 'margin', str(margin))
		dirty = True
	except ValueError:
		raise ConfigException('Invalid value for "margin" option')
	except ConfigParser.InterpolationError as e:
		raise ConfigException('Error in config file. Message was:\n    ' + str(e))

	if dirty:
		with open(configPath, 'w+') as configfile:
			Config.write(configfile)
	
	return configHash
