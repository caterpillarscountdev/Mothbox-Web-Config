#!/bin/sh

cd /home/pi/Desktop/Mothbox/Web
git pull
./postupdate.sh

cd /home/pi/Desktop/Mothbox
git pull

mkdir -p /home/pi/Desktop/Mothbox/logs
