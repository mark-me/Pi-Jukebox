"""
=======================================================
**screen_radio.py**: MPD radio management
=======================================================

"""
__author__ = 'Mark Zwart'

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from gui_widgets import *
from mpd_client import *
from settings import *
from screen_keyboard import *
from screen_settings import *
from config_file import *


class RadioBrowser(ItemList):
    """ The component that displays internet radio stations

        :param screen_rect: The screen rect where the directory browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, 'list_stations', screen_rect, 55, 42, 210, 194)
        self.outline_visible = False
        self.item_outline_visible = True
        self.font_color = FIFTIES_YELLOW
        self.set_item_alignment(HOR_LEFT, VERT_MID)
        self.radio_stations = []

    def item_selected_get(self):
        return self.radio_stations[self.item_selected_index]

    def show_stations(self):
        """ Displays all songs or based on the first letter or partial string match.

            :param search: Search string, default = None
            :param only_start: Boolean indicating whether the search string only matches the first letters, default = True
        """
        self.list = []
        self.radio_stations = config_file.radio_stations_get()
        updated = False
        for item in self.radio_stations:
            self.list.append(item[0])
            updated = True
        if updated:
            self.page_showing_index = 0
            self.draw()


class ScreenRadio(Screen):
    """ The screen where the user can browse and add radio stattion and add those to playlists.

        :param screen_rect: The display's rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        self.first_time_showing = True
        # Screen navigation buttons
        self.add_component(ButtonIcon('btn_player', self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.screen, ICO_PLAYLIST, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.screen, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.screen, ICO_DIRECTORY, 3, 125))
        self.add_component(ButtonIcon('btn_radio', self.screen, ICO_RADIO_ACTIVE, 3, 165))
        self.add_component(ButtonIcon('btn_settings', self.screen, ICO_SETTINGS, 3, 205))
        # Radio station buttons
        self.add_component(ButtonIcon('btn_station_add', self.screen, ICO_STATION_ADD, 55, 5))
        # Lists
        self.add_component(RadioBrowser(self.screen))

    def show(self):
        self.components['list_stations'].show_stations()
        super(ScreenRadio, self).show()

    def station_action(self):
        """ Displays screen for follow-up actions when an item was selected from the library. """
        selected = self.components['list_stations'].item_selected_get()
        select_screen = ScreenSelected(self.screen, selected[0], selected[1])
        select_screen.show()
        self.show()

    def on_click(self, x, y):
        """
        :param x: The horizontal click position.
        :param y: The vertical click position.

        :return: Possibly returns a screen index number to switch to.
        """
        tag_name = super(ScreenRadio, self).on_click(x, y)
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
        elif tag_name == 'btn_station_add':
            screen_add = ScreenStation(self.screen)
            screen_add.show()
            self.show()
        elif tag_name == 'btn_settings':
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == 'list_stations':
            self.station_action()


class ScreenSelected(ScreenModal):
    """ Screen for selecting playback actions with a selected radio station.

        :param screen_rect: The directory's rect where the library browser is drawn on.
        :param station_name: The name of the selected radio station.
        :param station_URL: The URL of the selected radio station.
    """

    def __init__(self, screen_rect, station_name, station_URL):
        ScreenModal.__init__(self, screen_rect, station_name)
        self.station_name = station_name
        self.station_URL = station_URL
        self.title_color = FIFTIES_YELLOW
        self.initialize()
        self.return_type = ""

    def initialize(self):
        """ Set-up screen controls. """
        button_left = self.window_x + 10
        button_width = (self.window_width - 2 * button_left) / 2 - 5
        button_top = 30
        label = "Edit"
        self.add_component(ButtonText('btn_edit', self.screen, button_left, button_top, button_width, 32, label))
        label = "Remove"
        self.add_component(
            ButtonText('btn_remove', self.screen, button_left + button_width + 10, button_top, button_width, 32, label))
        button_width = self.window_width - 2 * button_left
        button_top += 42
        label = "Add to playlist"
        self.add_component(ButtonText('btn_add', self.screen, button_left, button_top, button_width, 32, label))
        self.components['btn_add'].button_color = FIFTIES_TEAL
        button_top += 42
        label = "Add to playlist and play"
        self.add_component(ButtonText('btn_add_play', self.screen, button_left, button_top, button_width, 32, label))
        self.components['btn_add_play'].button_color = FIFTIES_TEAL
        button_top += 42
        label = "Replace playlist and play"
        self.add_component(ButtonText('btn_replace', self.screen, button_left, button_top, button_width, 32, label))
        self.components['btn_replace'].button_color = FIFTIES_TEAL
        button_top += 42
        label = "Cancel"
        self.add_component(ButtonText('btn_cancel', self.screen, button_left, button_top, button_width, 32, label))

    def action(self, tag_name):
        """ Action that should be performed on a click. """
        play = False
        clear_playlist = False
        if tag_name == 'btn_edit':
            screen_edit = ScreenStation(self.screen, self.station_name)
            screen_edit.show()
            self.close()
        elif tag_name == 'btn_remove':
            screen_yes_no = ScreenYesNo(self.screen, "Remove " + self.station_name,
                                        "Are you sure you want to remove " + self.station_name + "?")
            if screen_yes_no.show() == 'yes':
                config_file.setting_remove('Radio stations', self.station_name)
            self.close()
        elif tag_name == 'btn_add_play':
            play = True
        elif tag_name == 'btn_replace':
            play = True
            clear_playlist = True
        if tag_name == 'btn_add' or tag_name == 'btn_add_play' or tag_name == 'btn_replace':
            mpd.playlist_add_file(self.station_URL, play, clear_playlist)
        self.close()


class ScreenStation(ScreenModal):
    """ Screen for selecting playback actions with a selected radio station.

        :param screen_rect: The directory's rect where the library browser is drawn on.
        :param station_name: The name of the selected radio station.
        :param station_URL: The URL of the selected radio station.
    """

    def __init__(self, screen_rect, station_name=""):
        ScreenModal.__init__(self, screen_rect, station_name)
        self.title_color = FIFTIES_YELLOW
        self.window_x = 20
        self.window_y = 60
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.station_name = station_name
        btn_name_label = ""
        btn_URL_label = ""
        if station_name == "":
            ScreenModal.__init__(self, screen_rect, "Add a radio station")
            self.station_URL = ""
            btn_name_label = "Set station name"
            btn_URL_label = "Set station URL"
        else:
            ScreenModal.__init__(self, screen_rect, "Edit radio station")
            self.station_URL = config_file.setting_get('Radio stations', self.station_name)
            btn_name_label = "Change name " + self.station_name
            btn_URL_label = "Change station URL"
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        button_top = 30
        self.add_component(
            ButtonText('btn_name', self.screen, button_left, button_top, button_width, 32, btn_name_label))
        button_top += 42
        self.add_component(ButtonText('btn_URL', self.screen, button_left, button_top, button_width, 32, btn_URL_label))
        button_top += 42
        self.add_component(
            ButtonText('btn_cancel', self.screen, self.window_x + 5, self.window_y + self.window_height - 37, 55, 32,
                       "Cancel"))
        self.add_component(ButtonText('btn_ok', self.screen, self.window_x + self.window_width - 60,
                                      self.window_y + self.window_height - 37, 55, 32, "Ok"))

    def update(self):
        """ Set-up screen controls. """
        if self.station_name == "":
            self.components['btn_name'].draw("Set station name")
        else:
            self.components['btn_name'].draw("Change name " + self.station_name)
        if self.station_URL == "":
            self.components['btn_URL'].draw("Set station URL")
        else:
            self.components['btn_URL'].draw("Change station URL")
        self.show()

    def action(self, tag_name):
        """ Action that should be performed on a click. """
        if tag_name == 'btn_name':
            keyboard = Keyboard(self.screen, "Set station name")
            keyboard.title_color = FIFTIES_YELLOW
            keyboard.text = self.station_name
            self.station_name = keyboard.show()
            self.update()
            self.show()
        elif tag_name == 'btn_URL':
            keyboard = Keyboard(self.screen, "Set station URL")
            keyboard.title_color = FIFTIES_YELLOW
            keyboard.text = self.station_URL
            self.station_URL = keyboard.show()
            self.update()
            self.show()
        elif tag_name == 'btn_cancel':
            self.close()
        elif tag_name == 'btn_ok':
            if self.station_name != "" and self.station_URL != "":
                config_file.setting_set('Radio stations', self.station_name, self.station_URL)
            self.close()
