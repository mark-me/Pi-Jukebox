"""
**pi-jukebox.py**: Main file
"""

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


class Screens(object):
    """ Manages screens

            - Player screen
            - Library screen
        Handles screen switching, clicking and swyping and mpd status updating
    """

    def __init__(self):
        self.screen_list = []  # List containing all screen objects (home-screen, library-browser etc.)
        self.screen_list_current = 0  # Points to current screen in screen_list, initially select player/home screen
        self.screen_list.append(ScreenPlayer(screen))  # Create player (home) screen
        self.screen_list.append(ScreenLibrary(screen))  # Create library browsing screen
        self.mouse_down_pos = pygame.mouse.get_pos()  # Initialize mouse position

    def show(self):
        """ Show the current screen """
        self.screen_list[self.screen_list_current].show()

    def add_screen(self, screen):
        """ Adds screen to list """
        self.screen_list.append(screen)

    def mpd_updates(self):
        """ Updates a current screen if it shows mpd relevant content. """
        if isinstance(self.screen_list[self.screen_list_current], ScreenPlayer):
            self.screen_list[self.screen_list_current].update()

    def swipe_type_get(self):
        """ Determines the kind of gesture. """
        x, y = pygame.mouse.get_rel()  # Register mouse movement since last call
        if abs(x) <= MIN_SWIPE:
            if abs(y) <= MIN_SWIPE:
                if abs(x) < MAX_CLICK and abs(y) < MAX_CLICK:
                    return SWIPE_CLICK  # Not a swipe but a tap (click)
                else:
                    return -1  # No idea what the user did
            elif y > MIN_SWIPE:  # Down swipe
                return SWIPE_DOWN
            elif y < -MIN_SWIPE:  # Up swipe
                return SWIPE_UP

        elif abs(y) <= MIN_SWIPE:
            if x > MIN_SWIPE:  # Left swipe
                return SWIPE_LEFT
            elif x < -MIN_SWIPE:  # Right swipe
                return SWIPE_RIGHT
        return SWIPE_CLICK  # Tap

    def process_mouse_event(self, event_type):
        """ Processes mouse events. """
        if event_type == pygame.MOUSEBUTTONDOWN:  # Gesture start
            mouse_down_time = pygame.time.get_ticks()  # Start timer to detect long mouse clicks
            self.mouse_down_pos = pygame.mouse.get_pos()  # Get click position (= start position for swipe)
            pygame.mouse.get_rel()  # Start tracking mouse movement
        elif event_type == pygame.MOUSEBUTTONUP:  # Gesture end
            swipe_type = self.swipe_type_get()  # Determines the kind of gesture used
            # Start mouse related event functions
            if swipe_type == SWIPE_CLICK:  # Fire click function
                ret_value = self.screen_list[self.screen_list_current].on_click(self.mouse_down_pos[0],
                                                                                self.mouse_down_pos[
                    1])  # Relay tap/click to active screen
                # If the screen requests a screen switch
                if ret_value >= 0 and ret_value < len(self.screen_list):
                    self.screen_list_current = ret_value
                    self.show()
            # Switch screens with horizontal swiping
            if swipe_type == SWIPE_LEFT and self.screen_list_current - 1 >= 0:
                self.screen_list_current -= 1
                self.show()
            if swipe_type == SWIPE_RIGHT and self.screen_list_current + 1 < len(self.screen_list):
                self.screen_list_current += 1
                self.show()
            # Relay vertical swiping to active screen controls
            if swipe_type == SWIPE_UP or swipe_type == SWIPE_DOWN:
                self.screen_list[self.screen_list_current].on_swipe(self.mouse_down_pos[0], self.mouse_down_pos[1],
                                                                    swipe_type)


def main():
    """ The function where it all starts...."""
    pygame.display.set_caption("Pi Jukebox")
    # Check whether mpd is running and get it's status
    if not mpd_controller.is_mpd_running():
        print("mpd is not running... Start the mpd daemon service with 'sudo service mpd start'.")
        sys.exit()

    screens = Screens()  # Screens
    mpd_controller.status_get()  # Get mpd status
    screens.show()  # Display the screen

    while 1:

        # Check whether mpd's status changed
        if mpd_controller.status_get():
            screens.mpd_updates()  # If so update relevant screens

        for event in pygame.event.get():

            screens.process_mouse_event(event.type)

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()

    time.sleep(0.2)
    pygame.display.update()


if __name__ == '__main__':
    main()
