#!/bin/bash

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

check_prerequisites() {
	echo -n "Checking prerequisites... "
	if [ ! `command -v python 2>/dev/null` ] ; then
		echo -e "FAILED!\n\nYou need to install python first. Aborting." 1>&2
		exit 2
	fi
	if [ ! `command -v i2cset 2>/dev/null` ] ; then
		echo -e "FAILED!\n\nYou need to install i2c-tools first. Aborting." 1>&2
		exit 2
	fi
	if [ ! -d /usr/lib/systemd/system/ ] ; then
		echo -e "FAILED!\n\nThis system doesn't seem to have systemd. Aborting." 1>&2
		exit 2
	fi
	echo -e "OK!\n"
}

install() {
	read -p "Are you sure you want to install picoolfan-manager [y|N]? " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]] ; then
		if [ -e /opt/picoolfan-manager/picoolfand.py ] ; then
			read -p "Do you want to overwrite current version [y|N]? " -n 1 -r
			echo
			if [[ $REPLY =~ ^[Yy]$ ]] ; then
				systemctl stop picoolfand.service
				systemctl stop picoolfan-init.service
				systemctl disable picoolfand.service
				systemctl disable picoolfan-init.service
			else
				echo "Installation interrupted by user."
				exit 1
			fi
		fi
		mkdir -p /opt/picoolfan-manager
		cp ./src/picoolfand.py /opt/picoolfan-manager/
		cp ./src/pilog.py /opt/picoolfan-manager/
		cp ./src/piconfig.py /opt/picoolfan-manager/
		cp ./src/picoolfan-init.sh /opt/picoolfan-manager/
		cp ./src/picoolfand.service /usr/lib/systemd/system/
		cp ./src/picoolfan-init.service /usr/lib/systemd/system/
		chmod +x /opt/picoolfan-manager/picoolfand.py
		chmod +x /opt/picoolfan-manager/picoolfan-init.sh
		systemctl daemon-reload
		echo "----------------------------------------------------------"
		echo " start daemon with   'systemctl start picoolfand.service' "
		echo " enable at boot with 'systemctl enable picoolfand.service'"
		echo "----------------------------------------------------------"
		echo "Done."
		exit 0
	else
		echo "Installation interrupted by user."
		exit 1
	fi
	
}

uninstall() {
	if [ ! -d /opt/picoolfan-manager/ ] ; then
		echo "picoolfan-manager is not installed!"
		exit 2
	fi
	read -p "Are you sure you want to uninstall picoolfan-manager [y|N]? " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]] ; then
		systemctl stop picoolfand.service
		systemctl stop picoolfan-init.service
		systemctl disable picoolfand.service
		systemctl disable picoolfan-init.service
		rm -f /opt/picoolfan-manager/picoolfand.py*
		rm -f /opt/picoolfan-manager/pilog.py*
		rm -f /opt/picoolfan-manager/piconfig.py*
		rm -f /opt/picoolfan-manager/picoolfan-init.sh
		rm -rf /opt/picoolfan-manager/__pycache__/
		rmdir /opt/picoolfan-manager/ 2> /dev/null
		rm -f /usr/lib/systemd/system/picoolfand.service
		rm -f /usr/lib/systemd/system/picoolfan-init.service
		rm -f /etc/default/picoolfan-manager
		echo "Done."
		exit 0
	else
		echo "Uninstallation interrupted by user."
		exit 1
	fi
}

case "$1" in
	install)
		is_root
		check_prerequisites
		install
		;;
	uninstall)
		is_root
		uninstall
		;;
	*)
		echo "Usage: $0 {install|uninstall}"
		exit 1
		;;
esac

exit 0
