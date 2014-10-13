#!/bin/bash

### BEGIN INIT INFO
# Provides:          picoolfand
# Required-Start:    $syslog
# Required-Stop:     $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start picoolfand daemon.
# Description:       Start picoolfand daemon.
### END INIT INFO

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

is_root() {
	if [ "$(id -u)" != "0" ] ; then
			echo "You must be root to execute this script" 1>&2
		exit 2
	fi
}

case "$1" in
  start)
	is_root

	if [ ! $(lsmod | grep i2c_bcm2708) ] ; then
		/opt/picoolfan-manager/picoolfan-init.sh
	fi
	/opt/picoolfan-manager/picoolfand.py -d
	process=$(ps aux | grep picoolfand.py | grep -v grep | awk "{print \$2}")
	echo "Process started with PID $process"
	;;
  stop)
	is_root

	process=$(ps aux | grep picoolfand.py | grep -v grep | awk "{print \$2}")
	if [ ! $process ] ; then
		echo "Not running" >&2
		exit 1
	fi
	echo "Killing PID $process"
	kill -15 $process
	echo "Done."
	;;
  restart|force-reload)
	is_root

	process=$(ps aux | grep picoolfand.py | grep -v grep | awk "{print \$2}")
	if [ ! $process ] ; then
		echo "Not running" >&2
		exit 1
	fi
	echo "Killing PID $process"
	kill -15 $process

	if [ ! $(lsmod | grep i2c_bcm2708) ] ; then
		/opt/picoolfan-manager/picoolfan-init.sh
	fi
	/opt/picoolfan-manager/picoolfand.py -d
	process=$(ps aux | grep picoolfand.py | grep -v grep | awk "{print \$2}")
	echo "Process started with PID $process"

	echo "Done."
	;;
  *)
	echo "Usage: $0 {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac
