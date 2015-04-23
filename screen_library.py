__author__ = 'mark'

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from interface_widgets import *
from mpc_control import *
from settings import *
from screen_keyboard import *
from screen_settings import *

""" The graphical control for browsing the MPD library """
class LibraryBrowser(ItemList):
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        ItemList.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.outline_visible = False
        self.item_outline_visible = True
        self.font_color = FIFTIES_YELLOW
        self.set_item_alignment(HOR_LEFT, VERT_MID)

    def show_artists(self, letter=None, only_start=True):
        updated = False
        if self.list != mpc_controller.get_artists(letter, only_start):
            self.list = mpc_controller.get_artists(letter, only_start)
            updated = True
        if updated:
            self.draw()

    def show_albums(self, letter=None, only_start=True):
        updated = False
        if self.list != mpc_controller.get_albums(letter, only_start):
            self.list = mpc_controller.get_albums(letter, only_start)
            updated = True
        if updated: self.draw()

    def show_songs(self, letter=None, only_start=True):
        updated = False
        if self.list != mpc_controller.get_songs(letter, only_start):
            self.list = mpc_controller.get_songs(letter, only_start)
            updated = True
        if updated: self.draw()


""" The graphical control for selecting artists/albums/songs starting with a letter """
class LetterBrowser(ItemList):
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        ItemList.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.item_outline_visible = True
        self.outline_visible = False
        self.font_color = FIFTIES_GREEN
        self.set_item_alignment( HOR_MID, VERT_MID)
        self.list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"\
                        , "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" \
                        , "0", "1", "2", "3", "4", "5", "7", "8", "9"]


""" The screen where the user can browse in the MPD database and add items to playlists """
class ScreenLibrary(Screen):
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY_ACTIVE, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS, 3, screen_height - 37))

        self.add_component(ButtonIcon("btn_artists", self.screen, ICO_SEARCH_ARTIST, 55, 5))
        self.add_component(ButtonIcon("btn_albums", self.screen, ICO_SEARCH_ALBUM, 107, 5))
        self.add_component(ButtonIcon("btn_songs", self.screen, ICO_SEARCH_SONG, 159, 5))
        self.add_component(ButtonIcon("btn_search", self.screen, ICO_SEARCH, 211, 5))

        self.add_component(LibraryBrowser("list_library", self.screen, 55, 40, 210, 210))
        self.add_component(LetterBrowser("list_letters", self.screen, 268, 35, 52, 210))

        self.currently_showing = "artists"
        self.set_currently_showing("artists")
        self.components["list_library"].show_artists()

    def set_currently_showing(self, type_showing):
        self.currently_showing = type_showing
        if type_showing == "artists":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST_ACTIVE)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_search"].set_image_file(ICO_SEARCH)
        elif type_showing == "albums":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM_ACTIVE)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_search"].set_image_file(ICO_SEARCH)
        elif type_showing == "songs":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG_ACTIVE)
            self.components["btn_search"].set_image_file(ICO_SEARCH)
        elif type_showing == "search":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_search"].set_image_file(ICO_SEARCH_ACTIVE)

    def find_first_letter(self):
        letter = self.components["list_letters"].get_item_selected()
        if self.currently_showing == "artists":
            self.components["list_library"].show_artists(letter)
        elif self.currently_showing == "albums":
            self.components["list_library"].show_albums(letter)
        elif self.currently_showing == "songs":
            self.components["list_library"].show_songs(letter)

    def find_text(self):
        screen_search = ScreenSearch(self.screen)
        screen_search.show()
        search_text = screen_search.search_text
        search_type = screen_search.search_type
        if search_type == "artist":
            self.components["list_library"].show_artists(search_text, False)
            self.set_currently_showing("artists")
        elif search_type == "album":
            self.components["list_library"].show_albums(search_text, False)
            self.set_currently_showing("albums")
        elif search_type == "song":
            self.components["list_library"].show_songs(search_text, False)
            self.set_currently_showing("songs")
        print (search_text)
        self.show()

    def playlist_action(self):
        selected = self.components["list_library"].get_item_selected()
        select_screen = ScreenSelected(screen, self.currently_showing, selected)
        select_screen.show()
        if isinstance(select_screen.return_object, list):
            self.components["list_library"].list = select_screen.return_object
            self.components["list_library"].draw()
            self.set_currently_showing(select_screen.return_type)
        self.show()

    def on_click(self, x, y):
        tag_name = super(ScreenLibrary, self).on_click(x, y)
        if tag_name == "btn_home":
            return 0
        elif tag_name == "btn_library":
            return 1
        elif tag_name == "btn_settings":
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == "btn_artists":
            self.set_currently_showing("artists")
            self.components["list_library"].show_artists()
        elif tag_name == "btn_albums":
            self.set_currently_showing("albums")
            self.components["list_library"].show_albums()
        elif tag_name == "btn_songs":
            self.set_currently_showing("songs")
            self.components["list_library"].show_songs()
        elif tag_name == "btn_search":
            self.find_text()
        elif tag_name == "list_letters":
            self.find_first_letter()
        elif tag_name == "list_library":
            self.playlist_action()


""" Modal screen used for selecting playback actions with an item selected from the library """
class ScreenSearch(ScreenModal):
    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Search library for...")
        self.window_color = FIFTIES_TEAL
        self.search_type = ""
        self.search_text = ""
        self.initialize()

    def initialize(self):
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left

        label = "Artists"
        self.add_component(ButtonText("btn_artists", self.screen, button_left, 50, button_width, label))
        label = "Albums"
        self.add_component(ButtonText("btn_albums", self.screen, button_left, 92, button_width, label))
        label = "Songs"
        self.add_component(ButtonText("btn_songs", self.screen, button_left, 134, button_width, label))
        label = "Cancel"
        self.add_component(ButtonText("btn_cancel", self.screen, button_left, 176, button_width, label))

    def action(self, tag_name):

        if tag_name == "btn_cancel":
            pass

        if tag_name == "btn_artists":
            self.search_type = "artist"
            search_label = "Search artists"
        elif tag_name == "btn_albums":
            self.search_type = "album"
            search_label = "Search albums"
        elif tag_name == "btn_songs":
            self.search_type = "song"
            search_label = "Search songs"

        keyboard = Keyboard(self.screen, search_label)
        self.search_text = keyboard.show()

        self.close()


""" Modal screen used for selecting playback actions with an item selected from the library """
class ScreenSelected(ScreenModal):
    def __init__(self, screen_rect, selected_type, selected_title):
        ScreenModal.__init__(self, screen_rect, selected_title)
        self.type = selected_type
        self.selected = selected_title
        self.window_color = FIFTIES_TEAL
        self.initialize()
        self.return_type = ""

    def initialize(self):
        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left

        label = "Add to playlist"
        self.add_component(ButtonText("btn_add", self.screen, button_left, 30, button_width, label))
        label = "Add to playlist and play"
        self.add_component(ButtonText("btn_add_play", self.screen, button_left, 72, button_width, label))
        label = "Replace playlist and play"
        self.add_component(ButtonText("btn_replace", self.screen, button_left, 114, button_width, label))
        if self.type == "artists":
            label = "Albums of " + self.title
            self.add_component(ButtonText("btn_artist_get_albums", self.screen, button_left, 156, button_width, label))
            label = "Songs of " + self.title
            self.add_component(ButtonText("btn_artist_get_songs", self.screen, button_left, 198, button_width, label))
        elif self.type == "albums":
            label = "Songs of " + self.title
            self.add_component(ButtonText("btn_album_get_songs", self.screen, button_left, 156, button_width, label))
        #label = "Cancel"
        #self.add_component(ButtonText("btn_cancel", self.screen, button_left, 134, button_width, label))


        #label = "Search more of " + self.selected
        #self.add_component(ButtonText("btn_search", self.screen, button_left, 156, button_width, label))
        #label = "Cancel"
        #self.add_component(ButtonText("btn_cancel", self.screen, button_left, 188, button_width, label))

    def action(self, tag_name):
        play = False
        clear_playlist = False

        if tag_name == "btn_add_play":
            play = True
        elif tag_name == "btn_replace":
            play = True
            clear_playlist = True
        if tag_name == "btn_add" or tag_name == "btn_add_play" or tag_name == "btn_replace":
            if self.type == "artists":
                mpc_controller.add_artist(self.selected, play, clear_playlist)
            elif self.type == "albums":
                mpc_controller.add_album(self.selected, play, clear_playlist)
            elif self.type == "songs":
                mpc_controller.add_song(self.selected, play, clear_playlist)
            self.return_object = None
        elif tag_name == "btn_artist_get_albums":
            self.return_object = mpc_controller.get_artist_albums(self.selected)
            self.return_type = "albums"
            self.close()
        elif tag_name == "btn_artist_get_songs":
            self.return_object = mpc_controller.get_artist_songs(self.selected)
            self.return_type = "songs"
            self.close()
        elif tag_name == "btn_album_get_songs":
            self.return_object = mpc_controller.get_album_songs(self.selected)
            self.return_type = "songs"
            self.close()
        self.close()




