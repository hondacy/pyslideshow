#!/bin/bash
DATE=`date '+%Y-%m-%d__%H_%M_%S'`
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf ./wpa_supplicant.conf_$DATE
#sudo chown pi:pi ./wpa_supplicant.conf_$DATE
