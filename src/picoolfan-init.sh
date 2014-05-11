#!/bin/bash

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

#if [ "$(id -u)" != "0" ] ; then
#	echo "You must be root to execute this script" 1>&2
#	exit 1
#fi

modprobe i2c-bcm2708
modprobe i2c-dev
modprobe rtc-ds1307

echo "ds1307 0x68" > /sys/class/i2c-adapter/i2c-1/new_device

i2cset -y 1 0x6c 0 1
i2cset -y 1 0x6c 1 3
