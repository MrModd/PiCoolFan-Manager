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
	echo -e "OK!\n"
}

check_distribution() {
	ret=""
	if [ -d /etc/init.d/ -a -e /etc/debian_version ] ; then
		ret="debian"
	elif [ -d /usr/lib/systemd/system/ -a -e /etc/arch-release ] ; then
		ret="arch"
	fi
	echo $ret
}

copy_common() {
	cp ./src/picoolfand.py /opt/picoolfan-manager/
	cp ./src/piconfig.py /opt/picoolfan-manager/
	cp ./src/picoolfan-manager.py /opt/picoolfan-manager/
	cp ./src/picoolfan-init.sh /opt/picoolfan-manager/
}

copy_debian() {
	copy_common
	cp ./src/debian/pilog.py.debian /opt/picoolfan-manager/pilog.py
	cp ./src/debian/picoolfand.sh /etc/init.d/
	chmod +x /etc/init.d/picoolfand.sh
}

copy_arch() {
	copy_common
	cp ./src/arch/pilog.py.arch /opt/picoolfan-manager/pilog.py
	cp ./src/arch/picoolfand.service /usr/lib/systemd/system/
	cp ./src/arch/picoolfan-init.service /usr/lib/systemd/system/
}

copy_files() {
	dist=$(check_distribution)
	if [ $dist == "debian" ] ; then
		copy_debian
	elif [ $dist == "arch" ] ; then
		copy_arch
	else
		echo "Error: cannot determine distribution version." 1>&2
		exit 2
	fi
}

rm_common() {
	rm -f /usr/bin/picoolfan
	rm -f /opt/picoolfan-manager/picoolfand.py*
	rm -f /opt/picoolfan-manager/pilog.py*
	rm -f /opt/picoolfan-manager/piconfig.py*
	rm -f /opt/picoolfan-manager/picoolfan-manager.py*
	rm -f /opt/picoolfan-manager/picoolfan-init.sh
	rm -rf /opt/picoolfan-manager/__pycache__/
	rmdir /opt/picoolfan-manager/ 2> /dev/null
	rm -f /etc/default/picoolfan-manager
}

rm_debian() {
	rm_common
	rm /etc/init.d/picoolfand.sh
}

rm_arch() {
	rm_common
	rm -f /usr/lib/systemd/system/picoolfand.service
	rm -f /usr/lib/systemd/system/picoolfan-init.service
}

rm_files() {
	dist=$(check_distribution)
	if [ $dist == "debian" ] ; then
		rm_debian
	elif [ $dist == "arch" ] ; then
		rm_arch
	else
		echo "Error: cannot determine distribution version." 1>&2
		exit 2
	fi
}

stop_services_debian() {
	service picoolfand.sh stop
	update-rc.d -f picoolfand.sh remove
}

stop_services_arch() {
	systemctl stop picoolfand.service
	systemctl stop picoolfan-init.service
	systemctl disable picoolfand.service
	systemctl disable picoolfan-init.service
}

stop_services() {
	dist=$(check_distribution)
	if [ $dist == "debian" ] ; then
		stop_services_debian
	elif [ $dist == "arch" ] ; then
		stop_services_arch
	else
		echo "Error: cannot determine distribution version." 1>&2
		exit 2
	fi
}

start_services_debian() {
	echo "----------------------------------------------------------"
	echo " start daemon with   'service picoolfand.sh start'        "
	echo " enable at boot with 'update-rc.d picoolfand.sh defaults' "
	echo "----------------------------------------------------------"
}

start_services_arch() {
	systemctl daemon-reload
	
	echo "----------------------------------------------------------"
	echo " start daemon with   'systemctl start picoolfand.service' "
	echo " enable at boot with 'systemctl enable picoolfand.service'"
	echo "----------------------------------------------------------"
}

start_services() {
	dist=$(check_distribution)
	if [ $dist == "debian" ] ; then
		start_services_debian
	elif [ $dist == "arch" ] ; then
		start_services_arch
	else
		echo "Error: cannot determine distribution version." 1>&2
		exit 2
	fi
}

install() {
	read -p "Are you sure you want to install picoolfan-manager [y|N]? " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]] ; then
		if [ -e /opt/picoolfan-manager/picoolfand.py ] ; then
			read -p "Do you want to overwrite current version [y|N]? " -n 1 -r
			echo
			if [[ $REPLY =~ ^[Yy]$ ]] ; then
				stop_services
				rm -f /usr/bin/picoolfan
			else
				echo "Installation interrupted by user."
				exit 1
			fi
		fi
		mkdir -p /opt/picoolfan-manager
		
		copy_files
		
		chmod +x /opt/picoolfan-manager/picoolfand.py
		chmod +x /opt/picoolfan-manager/picoolfan-manager.py
		chmod +x /opt/picoolfan-manager/picoolfan-init.sh
		ln -s /opt/picoolfan-manager/picoolfan-manager.py /usr/bin/picoolfan
		
		start_services
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
		stop_services

		rm -f /usr/bin/picoolfan
		
		rm_files
		
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
		echo -n "Distribution detected: "
		echo $(check_distribution)
		install
		;;
	uninstall)
		is_root
		echo -n "Distribution detected: "
		echo $(check_distribution)
		uninstall
		;;
	*)
		echo "Usage: $0 {install|uninstall}"
		exit 1
		;;
esac

exit 0
