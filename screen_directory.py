"""
=======================================================
**screen_library.py**: MPD Library browsing screen
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


class LetterBrowser(ItemList):
    """ The graphical control for selecting artists/albums/songs starting with a letter.

        :param screen_rect: The screen rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, 'list_letters', screen_rect, 268, 40, 52, 195)
        self.item_outline_visible = True
        self.outline_visible = False
        self.font_color = FIFTIES_GREEN
        self.set_item_alignment(HOR_MID, VERT_MID)
        self.list = []
        # self.list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"\
        # , "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" \
        #                , "0", "1", "2", "3", "4", "5", "7", "8", "9"]


class DirectoryBrowser(ItemList):
    """ The component that displays mpd directory entries.

        :param screen_rect: The screen rect where the directory browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, 'list_directory', screen_rect, 55, 42, 210, 194)
        self.outline_visible = False
        self.item_outline_visible = True
        self.font_color = FIFTIES_YELLOW
        self.set_item_alignment(HOR_LEFT, VERT_MID)
        self.directory_current = "/"
        self.directory_content = []

    def item_selected_get(self):
        return self.directory_content[self.item_selected_index]

    def show_directory(self, path=""):
        """ Displays all songs or based on the first letter or partial string match.

            :param search: Search string, default = None
            :param only_start: Boolean indicating whether the search string only matches the first letters, default = True
        """
        self.list = []
        self.directory_current = path
        self.directory_content = mpd.directory_list(self.directory_current)
        updated = False
        for item in self.directory_content:
            index = item[1].rfind("/")
            if index == -1:
                self.list.append(item[1])
            else:
                self.list.append(item[1][index + 1:])
            updated = True
        if updated:
            self.page_showing_index = 0
            self.draw()
            self.first_letters_in_result_get()

    def show_directory_up(self):
        index = self.directory_current.rfind("/")
        if index == -1:
            self.show_directory("")
        else:
            directory_up = self.directory_current[:index]
            self.show_directory(directory_up)

    def first_letters_in_result_get(self):
        """ Get's the symbols that are first letters of the items in the result list.

            :return: List of letters
        """
        output_set = set()
        for item in self.list:
            first_letter = item[:1].upper()
            output_set.add(first_letter)
        letter_list = list(output_set)
        letter_list.sort(key=lambda item: (
            [str, int].index(type(item)), item))  # Sorting, making sure letters are put before numbers
        return letter_list


class ScreenDirectory(Screen):
    """ The screen where the user can browse in the MPD database and playlist_add items to playlists.

        :param screen_rect: The display's rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        self.first_time_showing = True
        # Screen navigation buttons
        self.add_component(ButtonIcon('btn_player', self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.screen, ICO_PLAYLIST, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.screen, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.screen, ICO_DIRECTORY_ACTIVE, 3, 125))
        self.add_component(ButtonIcon('btn_settings', self.screen, ICO_SETTINGS, 3, SCREEN_HEIGHT - 37))
        # Directory buttons
        self.add_component(ButtonIcon('btn_root', self.screen, ICO_FOLDER_ROOT, 55, 5))
        self.add_component(ButtonIcon('btn_up', self.screen, ICO_FOLDER_UP, 107, 5))
        # Lists
        self.add_component(DirectoryBrowser(self.screen))
        self.add_component(LetterBrowser(self.screen))

    def show(self):
        if self.first_time_showing:
            self.components['list_directory'].show_directory()
            self.letter_list_update()
            self.first_time_showing = False
        super(ScreenDirectory, self).show()

    def letter_list_update(self):
        self.components['list_letters'].list = self.components['list_directory'].first_letters_in_result_get()
        self.components['list_letters'].draw()

    def find_first_letter(self):
        """ Adjust current search type according to the letter clicked in the letter list. """
        letter = self.components['list_letters'].item_selected_get()
        # self.components['list_directory'].(letter)
        self.letter_list_update()

    def on_click(self, x, y):
        """ Handles click event. """
        tag_name = super(ScreenDirectory, self).on_click(x, y)
        if tag_name == 'btn_player':
            return 0
        elif tag_name == 'btn_playlist':
            return 1
        elif tag_name == 'btn_library':
            return 2
        elif tag_name == 'btn_directory':
            return 3
        elif tag_name == 'btn_settings':
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == 'list_letters':
            self.find_first_letter()
        elif tag_name == 'list_directory':
            self.playlist_action()
        elif tag_name == 'btn_root':
            self.components['list_directory'].show_directory("")
        elif tag_name == 'btn_up':
            self.components['list_directory'].show_directory_up()

    def playlist_action(self):
        """ Displays screen for follow-up actions when an item was selected from the library. """
        selected = self.components['list_directory'].item_selected_get()
        select_screen = ScreenSelected(self.screen, self.components['list_directory'].directory_current, selected[0],
                                       selected[1])
        select_screen.show()
        if isinstance(select_screen.return_object, list):
            self.components['list_directory'].show_directory(select_screen.selected_name)
        self.letter_list_update()
        self.show()


class ScreenSelected(ScreenModal):
    """ Screen for selecting playback actions with an item selected from the library.

        :param screen_rect: The directory's rect where the library browser is drawn on.
        :param selected_type: The selected library item [artists, albums, songs].
        :param selected_title: The title of the selected library item.
    """

    def __init__(self, screen_rect, directory, selected_type, selected_item):
        ScreenModal.__init__(self, screen_rect, selected_item)
        self.directory_current = directory
        self.selected_type = selected_type
        self.selected_name = selected_item
        self.title_color = FIFTIES_YELLOW
        self.initialize()
        self.return_type = ""

    def initialize(self):
        """ Set-up screen controls. """
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        button_top = 30
        if self.selected_type == 'directory':
            label = "Browse directory " + self.selected_name
            self.add_component(ButtonText('btn_browse', self.screen, button_left, button_top, button_width, 32, label))
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

        if tag_name == 'btn_browse':
            self.return_object = mpd.directory_list(self.selected_name)
        elif tag_name == 'btn_add_play':
            play = True
        elif tag_name == 'btn_replace':
            play = True
            clear_playlist = True
        if tag_name == 'btn_add' or tag_name == 'btn_add_play' or tag_name == 'btn_replace':
            if self.selected_type == 'directory':
                mpd.playlist_add_directory(self.selected_name, play, clear_playlist)
            elif self.selected_type == 'file':
                mpd.playlist_add_file(self.selected_name, play, clear_playlist)
            self.return_object = None
        self.close()
