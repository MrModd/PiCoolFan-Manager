# PiCoolFan Manager by MrModd

## License

Copyright (C) 2014  Federico "MrModd" Cosentino (http://mrmodd.it/)
Version 1.2

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

## Brief description

PiCoolFan Manager is a daemon studied for the PiCoolFan shield of
RaspberryPi. It monitors internal CPU temperature and set fan speed
accordingly.
This daemon works well with ArchLinux distribution, but should be fine
also for other Linux distributions that have systemd.

There is a script in this package that loads proper modules just before
the daemon starts. Moreover it sets the virtual RTC of the PiCoolFan as
system clock. In this way one can check hardware clock with "hwclock"
command. This can be useful if there's no internet connection and
ntp synchronization cannot be done.

## Prerequisites

This script is intended for OSes that adopt systemd.

- Before using this program you must install **i2c tools**, because
it requires *i2cset* command to operate. On ArchLinux you can install
them with:

		~# pacman -S i2c-tools

- **Python** is also required. On ArchLinux install it with:

		~# pacman -S python

## How to install

Clone this git repository and execute install.sh script with root permissions:

		~# ./install.sh install

If you want to start the script on boot, enable it with systemctl as described
during installation process.
Default configuration should be good for most people, anyway you can configure
temperature thresholds and the interval between updates.
You can find configuration file under */etc/default/picoolfan-manager*.

### Optional

Raspberry doesn't have an embedded Real Time Clock. That means it loses the
current time as soon as is unplugged from the main power.
Most distributions that run on Raspberry synchronize the time with NTP protocol
every time the board is powered up. This, however, requires an Internet connection
during the boot up. If you want to set the system time with the one kept by
PiCoolFan uncomment last line of */opt/picoolfan-manager/picoolfan-init.sh*.
This can go in conflict with NTP server, so make sure you use only one method
(for example disable ntpd daemon during boot process or keep the Raspberry
disconnected from the Internet).
