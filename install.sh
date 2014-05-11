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

is_root() {
	if [ "$(id -u)" != "0" ] ; then
			echo "You must be root to execute this script" 1>&2
		exit 1
	fi
}

install() {
	if [ ! -d /usr/lib/systemd/system/ ] ; then
		echo "This system doesn't have systemd. Aborting" 1>&2
		exit 1
	fi
	mkdir -p /opt/picoolfan-manager
	cp ./src/picoolfand.py /opt/picoolfan-manager/
	cp ./src/picoolfan-init.sh /opt/picoolfan-manager/
	cp ./src/picoolfand.service /usr/lib/systemd/system/
	cp ./src/picoolfan-init.service /usr/lib/systemd/system/
	chmod +x /opt/picoolfan-manager/picoolfand.py
	chmod +x /opt/picoolfan-manager/picoolfan-init.sh
	systemctl daemon-reload
	echo "----------------------------------------------------------"
	echo " start daemon with   'systemctl start picoolfand.service'"
	echo " enable at boot with 'systemctl enable picoolfand.service'"
	echo "----------------------------------------------------------"
}

uninstall() {
	if [ ! -d /opt/picoolfan-manager/ ] ; then
		echo "'picoolfan-manager' is not installed"
		exit 1
	fi
	systemctl stop picoolfand.service
	systemctl stop picoolfan-init.service
	systemctl disable picoolfand.service
	systemctl disable picoolfan-init.service
	rm -f /opt/picoolfan-manager/picoolfand.py
	rm -f /opt/picoolfan-manager/picoolfan-init.sh
	rmdir /opt/picoolfan-manager/ 2> /dev/null
	rm -f /usr/lib/systemd/system/picoolfand.service
	rm -f /usr/lib/systemd/system/picoolfan-init.service
}

case "$1" in
	install)
		is_root
		install
		echo "Done"
		;;
	uninstall)
		is_root
		uninstall
		echo "Done"
		;;
	*)
		echo "Usage: $0 {install|uninstall}"
		exit 1
		;;
esac

exit 0
