#!/bin/bash
cd /home/pi/flickr/
while true; do
sudo kill -9 $(ps aux | grep '[p]ython' | awk '{print $2}')
python3 ./_bin/py-slideshow/slideshow.py & ./Frame
sleep 4
done
