#-------------------------------------------------------------------------------
# Name:        pi-jukebox
# Purpose:     Providing a graphical interface from the command line
#                to manage MPD
#
# Author:      Mark Zwart
#
# Created:     20-04-2015
# Copyright:   (c) Mark Zwart 2015
# Licence:     GNU
#-------------------------------------------------------------------------------

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import interface_widgets
from settings import *
from mpc_control import *
from screen_player import *
from screen_library import *
from screen_settings import *

screen_list = []            # List containing all screen objects (home-screen, library-browser etc.)
screen_list_current = -1    # Points to current screen in screen_list

# Determines the kind of gesture
def get_swipe_type():
    x, y = pygame.mouse.get_rel()  # Register mouse movement since last call

    if abs(x) <= MIN_SWIPE:
        if abs(y) <= MIN_SWIPE:
            if abs(x) < MAX_CLICK and abs(y) < MAX_CLICK:
                return SWIPE_CLICK      # Not a swipe but a tap (click)
            else:
                return -1      # No idea what the user did
        elif y > MIN_SWIPE:    # Down swipe
            return SWIPE_DOWN
        elif y < -MIN_SWIPE:   # Up swipe
            return SWIPE_UP

    elif abs(y) <= MIN_SWIPE:
        if x > MIN_SWIPE:      # Left swipe
            return SWIPE_LEFT
        elif x < -MIN_SWIPE:   # Right swipe
            return SWIPE_RIGHT
    return SWIPE_CLICK  	    # Tap


# Exit the application
def exit():
    sys.exit()

# Show the current screen
def screen_show():
    global screen_list, screen_list_current
    screen_list[screen_list_current].show()


# The function where it all starts....
def main():
    global screen_list, screen_list_current
    # Check whether mpd is running and get it's status
    if not mpc_controller.is_mpd_running():
        print("mpd is not running... Start the mpd daemon service with 'sudo service mpd start'.")
        exit()
    screen_list.append(ScreenPlayer(screen))    # Create player (home) screen
    screen_list.append(ScreenLibrary(screen))   # Create library browsing screen
    screen_list.append(ScreenSettings(screen))  # Create setting screen

    mpc_controller.get_status()

    screen_list_current = 0  # Initially select player/home screen
    screen_show()            # Display the screen

    mouse_down_pos = pygame.mouse.get_pos()  # Initialize mouse position

    while 1:

        if mpc_controller.get_status() and isinstance(screen_list[screen_list_current], ScreenPlayer):
            screen_list[screen_list_current].update()

        for event in pygame.event.get():

            # Detect mouse action
            if event.type == pygame.MOUSEBUTTONDOWN:        # Gesture start
                mouse_down_time = pygame.time.get_ticks()   # Start timer to detect long mouse clicks
                mouse_down_pos = pygame.mouse.get_pos()     # Get click position (= start position for swipe)
                pygame.mouse.get_rel()                      # Start tracking mouse movement
            if event.type == pygame.MOUSEBUTTONUP:  # Gesture end
                swipe_type = get_swipe_type()       # Determines the kind of gesture used

                # Start mouse related event functions
                if swipe_type == SWIPE_CLICK:      # Fire click function
                    ret_value = screen_list[screen_list_current].on_click(mouse_down_pos[0], mouse_down_pos[1])    # Relays tap/click to active screen
                    if ret_value >= 0 and ret_value <= 2:
                        screen_list_current = ret_value
                        screen_show()
                # Switch screens with horizontal swiping
                if swipe_type == SWIPE_LEFT and screen_list_current - 1 >= 0:
                    screen_list_current -= 1
                    screen_show()
                if swipe_type == SWIPE_RIGHT and screen_list_current + 1 < len(screen_list):
                    screen_list_current += 1
                    screen_show()
                # Relay vertical swiping to active screen controls
                if swipe_type == SWIPE_UP or swipe_type == SWIPE_DOWN:
                    screen_list[screen_list_current].on_swipe(mouse_down_pos[0], mouse_down_pos[1], swipe_type)

            # Possibility to end program with 'Esc' key
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit()

    time.sleep(0.2)
    pygame.display.update()


if __name__ == '__main__':
    pygame.display.set_caption("Pi Jukebox")
    main()
