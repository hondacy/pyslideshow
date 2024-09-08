
#  A script to download all new photos from an account (SOURCE_ALBUM) and move downloaded photos to a local location
#  Suitable for a LCD with resolution: 1366x768. Dimension: 16:9
#  Version: 2 (Download 'h' size photo using getSizes method)

# Inspiried from: https://github.com/beaufour/flickr-download/blob/master/flickr_download/flick_download.py
# Prerequests:
# - install python3: sudo apt-get install python3 pip3
# - install flickrapi: sudo pip3 install flickrapi
# - check albums id at: https://www.flickr.com/services/api/explore/flickr.photosets.getList
# - change id's if needed
# - set timezone: 
#		sudo dpkg-reconfigure tzdata
#		(choose: Asia/Jerusalem)
# - set localtime: 
#		sudo cp /usr/share/zoneinfo/Israel /etc/localtime
# - set a cron job to download photos every 15 minutes:
#		crontab -e
# 	and add a line:
#		*/15 * * * * python3 /home/pi/flickr/flickr_download.py
#


#!/usr/bin/env python
import urllib
import sys, os
import argparse
import flickrapi
import pathlib
from pathlib import Path
import logging
import pdb
import requests
import shutil

import time

#SOURCE_ALBUM = '' # Inbox
DESTIN_ALBUM = '6217836' # Frame album
PLACEHOLDERID = '731289' # Not must - only for easy log understanding
PLACEHOLDERNAME = 'PlaceHolder'
BASE_FOLDER  = 'pyslideshow'
DOWNLOAD_FOLDER = BASE_FOLDER + '/Frame'
#DOWNLOAD_FOLDER = BASE_FOLDER + '\\Frame'
DIRTY_FILE = BASE_FOLDER + '/_bin/DIRTY_FILE' # Will be changed to True when new photos are detected

api_key = 'API_TOKEN'
api_secret = 'API_SECRET'
oauth_file = Path('pyslidshow/.flickr/oauth-tokens.sqlite')
#oauth_file = Path('C:\\Users\\bob\.flickr\\oauth-tokens.sqlite')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

	
def main():	
	###  Logging:
	global logger
	logger = setup_logger('normal_logger', BASE_FOLDER + '/logs/log_normal.log')
	global logger_errors
	logger_errors	= setup_logger('errors_logger', BASE_FOLDER + '/logs/log_errors.log')	# Error events

	### Downloading all new photos
	logger.info('### Starting flickr downloader... ###')
	download_all_new_photos()


### Functions:
def setup_logger(name, log_file, level=logging.INFO):
	"""Function setup as many loggers as you want"""

	handler = logging.FileHandler(log_file)		
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger

def download_all_new_photos():
	flickr = flickrapi.FlickrAPI(api_key, api_secret, store_token=True)

	if oauth_file.exists():
		print('Autho file found!',oauth_file)
	else:
		autho_exit_code = flickr.authenticate_via_browser(perms='write') # This is enough: https://github.com/rfaulkner/flickrapi/blob/master/doc/3-auth.rst

	# Download 'inbox' photoset (https://stuvel.eu/flickrapi-doc/7-util.html#walking-through-all-photos-in-a-set)
	new_photos = flickr.photos.getNotInSet(api_key=api_key)
	new_photos_list = new_photos.find('photos').findall('photo') # find all 'photo' elements inside 'photos' element tree.
	print('Downloading ', str(new_photos_list.__len__()), ' new photos')
	### If number of new photos > 0, Set dirty file to signal the slideshow to refresh
	if new_photos_list.__len__():
		f = open(DIRTY_FILE, 'w')
		f.write('NEW_PHOTOS_FOUND ')
		f.close()
	logger.info('Downloading ' + str(new_photos_list.__len__()) + ' new photos')

	for photo in new_photos_list: # download all new photos (That are not in set [=album])
		try:
			sizes = flickr.photos.getSizes(photo_id=photo.get('id'))
			photo_path = sizes.find('sizes').findall('size')[-3].get('source')
		#	#photo_path = 'https://farm' + photo.get('farm') + '.staticflickr.com/' + photo.get('server') + '/' + photo.get('id') + '_' + photo.get('secret') + '_h.jpg'
			logger.info('Downloading photo: ' + photo.get('id') + ' - ' + photo.get('title') + ' (' + photo_path + ')')
			print('Downloading photo: ', photo.get('id'), '-', photo.get('title'), '(', photo_path, ')')
			# Download:
			r = requests.get(photo_path, stream=True)
			if r.status_code == 200:
				with open(DOWNLOAD_FOLDER + '/' + photo.get('id') + '.jpg', 'wb') as f:
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)   
			download_exit_code = r.status_code
			#download_exit_code = urllib.request.urlretrieve(photo_path, DOWNLOAD_FOLDER + '/' + photo.get('id') + '.jpg' )
			#if download_exit_code[0].__len__() == 0:
			if download_exit_code != 200:
				logger_errors.error('error at downloading: ' + photo.get('id') + ' - ' + download_exit_code)
				print('error at downloading: ', photo.get('id') + ' - ' + download_exit_code)
			# Move to other Album in cloud:
			add_exit_code = flickr.photosets.addPhoto(photoset_id=DESTIN_ALBUM, photo_id=photo.get('id'))
			logger.info('Adding photo to frame album: ' + add_exit_code.get('stat'))
			print('add_exit_code: ', add_exit_code.get('stat'))
		except BaseException as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			print('Error in photo: ', photo_path, ' ', sys.exc_info()[0].__name__, str(e), fname, 'In line No. ', exc_tb.tb_lineno)
			logger_errors.error('Error in photo: ' + photo_path + '. ' + str(sys.exc_info()[0].__name__) + ': ' +str(e) + '. file: ' + fname + '. line No. ' + str(exc_tb.tb_lineno))
			continue
		sizes = None
		photo_path = None
		download_exit_code = None
		add_exit_code = None
		
main()
