#!/bin/bash


# Inspired From: https://github.com/cgoldberg/py-slideshow

### TODO:
###    Show IP address at startup
###    Show little transparent clock
###    Video support
###    



cd /home/pi/flickr

# Premote server for bluetooth mouse&keyboard:
exec ./_bin/Premote.sh & #this doesn't blocks the script!

/usr/bin/python3 ./_bin/slideshow.py ./Frame/  >> ./_bin/logs/log_errors.log 2>&1


