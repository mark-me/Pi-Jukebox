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
from screen_directory import *
from screen_radio import *
from screen_settings import *


class PiJukeboxScreen(Screen):
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon('btn_player', self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.screen, ICO_PLAYLIST_ACTIVE, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.screen, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.screen, ICO_DIRECTORY, 3, 125))
        self.add_component(ButtonIcon('btn_radio', self.screen, ICO_RADIO, 3, 165))
        self.add_component(ButtonIcon('btn_settings', self.screen, ICO_SETTINGS, 3, 205))

    def on_click(self, x, y):
        """
        :param x: The horizontal click position.
        :param y: The vertical click position.

        :return: Possibly returns a screen index number to switch to.
        """
        tag_name = super(ScreenPlaylist, self).on_click(x, y)
        if tag_name == 'btn_player':
            return 0
        elif tag_name == 'btn_playlist':
            return 1
        elif tag_name == 'btn_library':
            return 2
        elif tag_name == 'btn_directory':
            return 3
        elif tag_name == 'btn_radio':
            return 4
        elif tag_name == 'btn_settings':
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()



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
        self.screen_list.append(ScreenDirectory(SCREEN))  # Create directory browsing screen
        self.screen_list.append(ScreenRadio(SCREEN))  # Create radio station managing screen

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
    mpd.music_directory_set(config_file.setting_get('MPD Settings', 'music directory'))
    if not config_file.section_exists('Radio stations'):
        config_file.setting_set('Radio stations', "Radio Swiss Jazz", "http://stream.srg-ssr.ch/m/rsj/mp3_128")


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
