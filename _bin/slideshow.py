#!/usr/bin/env python
#
#  Copyright (c) 2013, 2015, Corey Goldberg
#
#  Dev: https://github.com/cgoldberg/py-slideshow
#  License: GPLv3

# Slideshow player - plays all photos found in directory.
# When flickr_downloader returns non zero code - reloads the slideshow so new photos will be included.
# rewriten by: H.D.D.
# TODO:
# - Delete oldest file only when 'Frame' folder > x MB
# - Send error log by email if errors acour


CHECK_FOR_NEW_PHOTOS_EVERY_X_SECOND = 5 # 10800 = 3 Hours
BASE_FOLDER  = '/Users/hanochdaum/development/pyslideshow'
DOWNLOAD_FOLDER = BASE_FOLDER + '/Frame'
#DIRTY_FILE = BASE_FOLDER + '/_bin/DIRTY_FILE' # Will be deleted after new photos are downloaded
IN_DEBUG_MODE = False


import argparse
import random
import sys
import os
import pyglet
#from pyglet.window import mouse
import logging
import time
from pathlib import Path
#from past.builtins import execfile
# import flickr_download_v3
#from flickr_download_v3 import main_download_flickr

#sys.path.append(os.path.abspath("flickr_download_v3.py"))

NO_OF_FILES_IN_FRAME_FOLDER = len(os.listdir(DOWNLOAD_FOLDER))  # For use in debug mode - when new photos found in Frame folder - reloads slideshow
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
global MOUSE_CLICKS
MOUSE_CLICKS = 0
exit_pressed = 0

def update_pan_zoom_speeds():
    global _pan_speed_x
    global _pan_speed_y
    global _zoom_speed
    _pan_speed_x = random.randint(-8, 8)
    _pan_speed_y = random.randint(-8, 8)
    _zoom_speed = random.uniform(-0.02, 0.02)
    return _pan_speed_x, _pan_speed_y, _zoom_speed


def update_pan(dt):
    sprite.x += dt * _pan_speed_x
    sprite.y += dt * _pan_speed_y


def update_zoom(dt):
    sprite.scale += dt * _zoom_speed


def update_image(dt):
    img = pyglet.image.load(random.choice(image_paths))
    sprite.image = img
    sprite.scale = get_scale(window, img)
    sprite.x = 0
    sprite.y = 0
    update_pan_zoom_speeds()
    window.clear()


def get_image_paths(input_dir='.'):
    paths = []
    for root, dirs, files in os.walk(input_dir, topdown=True):
        for file in sorted(files):
            if file.endswith(('jpg', 'png', 'gif')):
                path = os.path.abspath(os.path.join(root, file))
                paths.append(path)
    return paths


def get_scale(window, image):
    if image.width > image.height:
        scale = float(window.width) / image.width
    else:
        scale = float(window.height) / image.height
    return scale

def setup_logger(name, log_file, level=logging.INFO):
	"""Function setup as many loggers as you want"""

	handler = logging.FileHandler(log_file)		
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)
	logger.setLevel(level)
	logger.addHandler(handler)

	return logger

# Pyglet init:
window = pyglet.window.Window(fullscreen=True)
if not IN_DEBUG_MODE:
    window.set_mouse_visible(False)
#label = pyglet.text.Label('נסיכות ונסיכים',
                          # font_name='Times New Roman',
                          # font_size=36,
                          # x=window.width//5, y=25, #window.height-
                          # anchor_x='center', anchor_y='center')
                    
@window.event
def on_draw():
    sprite.draw()
    # label.draw()
@window.event
def on_mouse_press(x, y, button, modifiers): # (x, y, button, modifiers);
    global MOUSE_CLICKS
    MOUSE_CLICKS = MOUSE_CLICKS + 1
    if IN_DEBUG_MODE: logger.info('mouse pressed ' + str(MOUSE_CLICKS) + ' times')
    if MOUSE_CLICKS > 1:
        sys.exit()
        
def reset_mouse_clicks(dt):
    global MOUSE_CLICKS
    MOUSE_CLICKS = 0
    
def check_for_new_photos(dt):
    try:
        #flick_check = BASE_FOLDER + '/_bin/flickr_download_v3'
        #if IN_DEBUG_MODE: logger.info('Current working folder: ' + os.getcwd())
        if IN_DEBUG_MODE: logger.info("#@@#  Checking for new photos - flickr #@@#")
        flickr_exit_code = flickr_download_v3.download_all_new_photos()
        if IN_DEBUG_MODE: # lets you change add photos files in Frame folder and slideshow reloads
            global NO_OF_FILES_IN_FRAME_FOLDER
            NEW_NO = len(os.listdir(DOWNLOAD_FOLDER))
            if NO_OF_FILES_IN_FRAME_FOLDER == NEW_NO:
                logger.info('NO_OF_FILES_IN_FRAME_FOLDER not changed (' + str(NO_OF_FILES_IN_FRAME_FOLDER) + ')')
            else:
                logger.info('NO_OF_FILES_IN_FRAME_FOLDER changed! New Number: ' + str(NEW_NO) )
                NO_OF_FILES_IN_FRAME_FOLDER = NEW_NO
                reload_photos_files()
            logger.info('flickr_exit_code:' + str(flickr_exit_code) + "\n")
        if flickr_exit_code:
            logger.info('New photo found from: Flickr!')
            reload_photos_files()
    except:
        print("########   Unexpected error in check_for_new_photos:", sys.exc_info(), '  ############')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lineno = exc_tb.tb_lineno
        import linecache
        linecache.checkcache(fname)
        line = linecache.getline(fname, lineno, exc_tb.tb_frame.f_globals)
        logger_errors.error('Unexpected error in check_for_new_photos: ' + str(sys.exc_info()[1]) + ' | Error Type: ' + exc_type.__name__ + ' | file: ' + fname + ' | line No. ' + str(lineno) + '|' + line.strip())

    
    ## TODO: 
    ## pass arguments: download_folder, log_file, OR: share vars from this script to downloader script
    ## Check from more providers: Google_Drive..


    
    
    # DIRTY_FILE_O = Path(DIRTY_FILE)
    # logger.info('Checking for dirty file: ' + DIRTY_FILE)
    # if DIRTY_FILE_O.exists():
        # logger.info('### Found new file/s, Restarting slideshow... ###')
        # time.sleep(2)
        # os.remove(DIRTY_FILE)
        # reload_photos_files()
       # pyglet.app.exit()
        
 
def reload_photos_files():
    try:
        if IN_DEBUG_MODE: logger.info('### Reloading photos files... ###')
        global image_paths
        image_paths = get_image_paths(DOWNLOAD_FOLDER)
        global img
        img  = pyglet.image.load(random.choice(image_paths))
        global sprite
        sprite = pyglet.sprite.Sprite(img)
        sprite.scale = get_scale(window, img)
    except:
        print("########   Unexpected error in reloading photos files:", sys.exc_info(), '  ############')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger_errors.error('Unexpected error in reloading photos files: ' + str(sys.exc_info()[1]) + ' | Error Type: ' + exc_type.__name__ + ' | file: ' + fname + ' | line No. ' + str(exc_tb.tb_lineno))

###  Logging:
global logger
logger = setup_logger('normal_logger', BASE_FOLDER + '/logs/log_normal.log')
global logger_errors
logger_errors	= setup_logger('errors_logger', BASE_FOLDER + '/logs/log_errors.log')	# Error events
logger.info('### Starting Photos Slideshow... ###')
	
if __name__ == '__main__':
    _pan_speed_x, _pan_speed_y, _zoom_speed = update_pan_zoom_speeds()

    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='directory of images',
                        nargs='?', default=os.getcwd())
    args = parser.parse_args()

    if not IN_DEBUG_MODE: pyglet.clock.schedule_interval(update_image, 6.0) # Production: change to 6.0. Debug: 1.0
    if IN_DEBUG_MODE: pyglet.clock.schedule_interval(update_image, 2.0) # Production: change to 6.0. Debug: 1.0
    pyglet.clock.schedule_interval(update_pan, 1/60.0)
    pyglet.clock.schedule_interval(update_zoom, 1/60.0)
    pyglet.clock.schedule_interval(check_for_new_photos, CHECK_FOR_NEW_PHOTOS_EVERY_X_SECOND)
    pyglet.clock.schedule_interval(reset_mouse_clicks, 3)

    if IN_DEBUG_MODE: logger.info('### Main loop starting... ###')
    while not exit_pressed:
        try:
            #app = 
            logger.info('### Starting app... ###')
            reload_photos_files()
            pyglet.app.run()
            if IN_DEBUG_MODE: logger.info('Finished app...') 
            if 'app' not in locals():
                logger.info('No instance of app - exiting...')
                #break
                sys.exit()
        except IOError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('Could not find photo for slideshow: ', ' ', sys.exc_info()[0].__name__, str(e), fname, 'In line No. ', exc_tb.tb_lineno)
            logger_errors.error('Could not find photo for slideshow: ' + str(sys.exc_info()[0].__name__) + ': ' +str(e) + '. file: ' + fname + '. line No. ' + str(exc_tb.tb_lineno))
            reload_photos_files()
            #pyglet.app.exit()
            #pyglet.app.run()
        except SystemExit:
            if 'app' not in locals():
                print('########   System Exited by function  ############')
                logger.info('System Exited by function...') 
            else:
                print('########   System Exited by user  ############')
                logger.info('System Exited by user...') 
            break
        except:
            print("########   Unexpected error:", sys.exc_info(), '  ############')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lineno = exc_tb.tb_lineno
            import linecache
            linecache.checkcache(fname)
            line = linecache.getline(fname, lineno, exc_tb.tb_frame.f_globals)
            logger_errors.error('Unexpected error: ' + str(sys.exc_info()[1]) + ' | Error Type: ' + exc_type.__name__ + ' | file: ' + fname + ' | line No. ' + str(lineno) + '|' + line.strip())
            if IN_DEBUG_MODE: break
            reload_photos_files()
            #pyglet.app.exit()
            #pyglet.app.run()    sys.exc_info()[0]
