# Cloud Photos SlideShow  <img style="float: right;" width=250px src="_bin/readme1.jpg">
Simple slideshow to displays new photos from cloud accounts
Currently supports flickr cloud

## Requirement
- A simple computer attached to a screen (Can be even a RaspberryPi)

## Installation
- Clone this repo
- Copy all files to: /home/pi/flickr (For example)
- Run this commands:

    sudo pip3 install  pyglet flickrapi
- Add the script "slideshow.sh" to startup, by editting this file (On RaspberryPi):
   ~/.config/lxsession/LXDE-pi
  And addinf this line to it:
   @/home/pi/flickr/slideshow.sh

For more configurations, please see file: config/_Raspberry_Config_For_Slideshows.txt
