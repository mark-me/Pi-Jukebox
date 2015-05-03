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
from interface_widgets import *
from mpc_control import *
from settings import *
from screen_keyboard import *
from screen_settings import *

class LibraryBrowser(ItemList):
    """ The component that displays mpd library entries.

        :param screen_rect: The screen rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, "list_library", screen_rect, 55, 40, 210, 210)
        self.outline_visible = False
        self.item_outline_visible = True
        self.font_color = FIFTIES_YELLOW
        self.set_item_alignment(HOR_LEFT, VERT_MID)

    def show_artists(self, search=None, only_start=True):
        """ Displays all artists or based on the first letter or partial string match.

            :param search: Search string, default = None
            :param only_start: Boolean indicating whether the search string only matches the first letters, default = True
        """
        updated = False
        if self.list != mpd.artists_get(search, only_start):
            self.list = mpd.artists_get(search, only_start)
            updated = True
        if updated:
            self.draw()

    def show_albums(self, search=None, only_start=True):
        """ Displays all albums or based on the first letter or partial string match.

            :param search: Search string, default = None
            :param only_start: Boolean indicating whether the search string only matches the first letters, default = True
        """
        updated = False
        if self.list != mpd.albums_get(search, only_start):
            self.list = mpd.albums_get(search, only_start)
            updated = True
        if updated: self.draw()

    def show_songs(self, search=None, only_start=True):
        """ Displays all songs or based on the first letter or partial string match.

            :param search: Search string, default = None
            :param only_start: Boolean indicating whether the search string only matches the first letters, default = True
        """
        updated = False
        if self.list != mpd.songs_get(search, only_start):
            self.list = mpd.songs_get(search, only_start)
            updated = True
        if updated: self.draw()

    def show_playlists(self, first_letter=None):
        """ Displays all playlists or based on the first letter.

            :param first_letter: Search string, default = None
        """
        updated = False
        if self.list != mpd.playlists_get(first_letter):
            self.list = mpd.playlists_get(first_letter)
            updated = True
        if updated: self.draw()


class LetterBrowser(ItemList):
    """ The graphical control for selecting artists/albums/songs starting with a letter.

        :param screen_rect: The screen rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, "list_letters", screen_rect, 268, 35, 52, 210)
        self.item_outline_visible = True
        self.outline_visible = False
        self.font_color = FIFTIES_GREEN
        self.set_item_alignment( HOR_MID, VERT_MID)
        self.list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"\
                        , "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" \
                        , "0", "1", "2", "3", "4", "5", "7", "8", "9"]


class ScreenLibrary(Screen):
    """ The screen where the user can browse in the MPD database and playlist_add items to playlists

        :param screen_rect: The display's rect where the library browser is drawn on.
    """
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY_ACTIVE, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS, 3, SCREEN_HEIGHT - 37))

        self.add_component(ButtonIcon("btn_artists", self.screen, ICO_SEARCH_ARTIST, 55, 5))
        self.add_component(ButtonIcon("btn_albums", self.screen, ICO_SEARCH_ALBUM, 107, 5))
        self.add_component(ButtonIcon("btn_songs", self.screen, ICO_SEARCH_SONG, 159, 5))
        self.add_component(ButtonIcon("btn_playlists", self.screen, ICO_PLAYLISTS, 211, 5))
        self.add_component(ButtonIcon("btn_search", self.screen, ICO_SEARCH, 263, 5))

        self.add_component(LibraryBrowser(self.screen))
        self.add_component(LetterBrowser(self.screen))

        self.currently_showing = "artists"
        self.set_currently_showing("artists")
        self.components["list_library"].show_artists()

    def set_currently_showing(self, type_showing):
        """ Switch icons to active dependent on which kind of searching is active.

            :param type_showing: The type of search results showing [artists, albums, songs, playlists]
        """
        self.currently_showing = type_showing
        if type_showing == "artists":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST_ACTIVE)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_playlists"].set_image_file(ICO_PLAYLISTS)
        elif type_showing == "albums":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM_ACTIVE)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_playlists"].set_image_file(ICO_PLAYLISTS)
        elif type_showing == "songs":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG_ACTIVE)
            self.components["btn_playlists"].set_image_file(ICO_PLAYLISTS)
        elif type_showing == "playlists":
            self.components["btn_artists"].set_image_file(ICO_SEARCH_ARTIST)
            self.components["btn_albums"].set_image_file(ICO_SEARCH_ALBUM)
            self.components["btn_songs"].set_image_file(ICO_SEARCH_SONG)
            self.components["btn_playlists"].set_image_file(ICO_PLAYLISTS_ACTIVE)

    def find_first_letter(self):
        """ Adjust current search type according to the letter clicked in the letter list """
        letter = self.components["list_letters"].item_selected_get()
        if self.currently_showing == "artists":
            self.components["list_library"].show_artists(letter)
        elif self.currently_showing == "albums":
            self.components["list_library"].show_albums(letter)
        elif self.currently_showing == "songs":
            self.components["list_library"].show_songs(letter)
        elif self.currently_showing == "playlists":
            self.components["list_library"].show_playlists(letter)

    def find_text(self):
        """ Find results according to part of the text.
            Launching a keyboard so that the user can specify the search string.
        """
        screen_search = ScreenSearch(self.screen)  # The search screen
        screen_search.show()
        search_text = screen_search.search_text  # The text the user searches for
        search_type = screen_search.search_type  # The type of tag the user searches for (artist, album, song)
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
        """ Displays screen for follow-up actions when an item was selected from the library. """
        selected = self.components["list_library"].item_selected_get()
        select_screen = ScreenSelected(self.screen, self.currently_showing, selected)
        select_screen.show()
        if isinstance(select_screen.return_object, list):
            self.components["list_library"].list = select_screen.return_object
            self.components["list_library"].draw()
            self.set_currently_showing(select_screen.return_type)
        self.show()

    def on_click(self, x, y):
        """ Handles click event. """
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
        elif tag_name == "btn_playlists":
            self.set_currently_showing("playlists")
            self.components["list_library"].show_playlists()
        elif tag_name == "btn_search":
            self.find_text()
        elif tag_name == "list_letters":
            self.find_first_letter()
        elif tag_name == "list_library":
            self.playlist_action()


class ScreenSearch(ScreenModal):
    """ Screen used further searching based on an item selected from the library

        :param screen_rect: The display's rect where the library browser is drawn on.

        :ivar search_type: Searching for... [artist, album, song].
        :ivar search_text: Partial text which should be searched for
    """
    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Search library for...")
        self.title_color = FIFTIES_TEAL
        self.search_type = ""
        self.search_text = ""
        self.initialize()

    def initialize(self):
        """ Set-up screen controls. """
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
        """ Action that should be performed on a click.

            :param tag_name: The identifying tag_name of the clicked widget.
        """
        search_label = tag_name
        if tag_name == "btn_cancel":
            self.close()
        elif tag_name == "btn_artists":
            self.search_type = "artist"
            search_label = "Search artists"
        elif tag_name == "btn_albums":
            self.search_type = "album"
            search_label = "Search albums"
        elif tag_name == "btn_songs":
            self.search_type = "song"
            search_label = "Search songs"
        # Open on-screen keyboard for entering search string
        keyboard = Keyboard(self.screen, search_label)
        self.search_text = keyboard.show()  # Get entered search text
        self.close()


class ScreenSelected(ScreenModal):
    """ Screen for selecting playback actions with an item selected from the library.

        :param screen_rect: The display's rect where the library browser is drawn on.
        :param selected_type: The selected library item [artists, albums, songs].
        :param selected_title: The title of the selected library item.
    """
    def __init__(self, screen_rect, selected_type, selected_title):
        ScreenModal.__init__(self, screen_rect, selected_title)
        self.type = selected_type
        self.selected = selected_title
        self.title_color = FIFTIES_TEAL
        self.initialize()
        self.return_type = ""

    def initialize(self):
        """ Set-up screen controls """
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

    def action(self, tag_name):
        """ Action that should be performed on a click """
        play = False
        clear_playlist = False

        if tag_name == "btn_add_play":
            play = True
        elif tag_name == "btn_replace":
            play = True
            clear_playlist = True
        if tag_name == "btn_add" or tag_name == "btn_add_play" or tag_name == "btn_replace":
            if self.type == "artists":
                mpd.playlist_add_artist(self.selected, play, clear_playlist)
            elif self.type == "albums":
                mpd.playlist_add_album(self.selected, play, clear_playlist)
            elif self.type == "songs":
                mpd.playlist_add_song(self.selected, play, clear_playlist)
            elif self.type == "playlists":
                mpd.playlist_add_playlist(self.selected, play, clear_playlist)
            self.return_object = None
        elif tag_name == "btn_artist_get_albums":
            self.return_object = mpd.artist_albums_get(self.selected)
            self.return_type = "albums"
            self.close()
        elif tag_name == "btn_artist_get_songs":
            self.return_object = mpd.artist_songs_get(self.selected)
            self.return_type = "songs"
            self.close()
        elif tag_name == "btn_album_get_songs":
            self.return_object = mpd.album_songs_get(self.selected)
            self.return_type = "songs"
            self.close()
        self.close()
