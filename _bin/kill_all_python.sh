#!/bin/bash
ps aux | grep '[p]ython'
read -n1 -r -p "Press any key to kill all python procces..." key
sudo kill -9 $(ps aux | grep '[p]ython' | awk '{print $2}')

