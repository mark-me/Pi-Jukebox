"""
**pi-jukebox.py**: Main file
"""
__author__ = 'Mark Zwart'
import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import interface_widgets
from settings import *
from mpd_client import *
from screen_player import *
from screen_library import *
from screen_settings import *


class PiJukeboxScreens(Screens):
    """ Manages Pi Jukebox's main screens.
            - Player screen
            - Library screen
        Handles screen switching, clicking and swiping and displaying mpd status
        updates on screen(s)
    """
    def __init__(self):
        Screens.__init__(self)
        self.screen_list.append(ScreenPlaying(SCREEN))  # Screen with now playing and cover art
        self.screen_list.append(ScreenPlaylist(SCREEN))  # Create player with playlist screen
        self.screen_list.append(ScreenLibrary(SCREEN))  # Create library browsing screen

    def mpd_updates(self):
        """ Updates a current screen if it shows mpd relevant content. """
        if isinstance(self.screen_list[self.current_index], ScreenPlaylist) or \
                isinstance(self.screen_list[self.current_index], ScreenPlaying):
            self.screen_list[self.current_index].update()


def main():
    """ The function where it all starts...."""
    pygame.display.set_caption("Pi Jukebox")
    # Check whether mpd is running and get it's status
    # if not mpd.is_mpd_running():
    #    print("mpd is not running... Start the mpd daemon service with 'sudo service mpd start'.")
    #    sys.exit()

    if not mpd.connect():
        print("Couldn't connect to the local mpd server on port 6600!")
        sys.exit()
    mpd.status_get()  # Get mpd status
    screens = PiJukeboxScreens()  # Screens
    screens.show()  # Display the screen

    while 1:

        # Check whether mpd's status changed
        pygame.time.wait(PYGAME_EVENT_DELAY)
        if mpd.status_get():
            screens.mpd_updates()  # If so update relevant screens

        for event in pygame.event.get():  # Do for all events in pygame's event queue

            screens.process_mouse_event(event)  # Handle mouse related events

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                mpd.disconnect()
                sys.exit()

    time.sleep(0.2)
    pygame.display.update()


if __name__ == '__main__':
    main()
