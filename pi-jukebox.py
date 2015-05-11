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
from gui_screens import *
from config_file import *
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


def apply_settings():
    # Check for first time settings
    if not config_file.setting_exists('MPD Settings', 'music directory'):
        screen_message = ScreenMessage(SCREEN, 'No music directory',
                                       "If you want to display cover art, Pi-Jukebox needs to know which directory your music collection is in. The location can also be found in your mpd.conf entry 'music directory'.",
                                       'warning')
        screen_message.show()
        settings_mpd_screen = ScreenSettingsMPD(SCREEN)
        settings_mpd_screen.keyboard_setting("Set music directory", 'MPD Settings', 'music directory',
                                             '/var/lib/mpd/music/')
    mpd.host = config_file.setting_get('MPD Settings', 'host')
    mpd.port = int(config_file.setting_get('MPD Settings', 'port'))
    mpd.music_directory = config_file.setting_get('MPD Settings', 'music directory')


def main():
    """ The function where it all starts...."""
    pygame.display.set_caption("Pi Jukebox")
    apply_settings()  # Check for first time settings and applies settings

    # Check whether mpd is running and get it's status
    if not mpd.connect():
        print("Couldn't connect to the mpd server " + mpd.host + " on port " + str(
            mpd.port) + "! Check settings in file pi-jukebox.conf or check is server is running 'sudo service mpd status'.")
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
