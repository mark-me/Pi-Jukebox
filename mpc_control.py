"""
===========================================================
**mpc_control.py**: controlling and monitoring mpd via mpc.
===========================================================
"""
__author__ = 'Mark Zwart'


import sys, pygame
import time
import subprocess
import os
import glob
from mpd import *

MPC_TYPE_ARTIST = "artist"
MPC_TYPE_ALBUM = "album"
MPC_TYPE_SONGS = "title"


class MPDController(object):
    """ Controls playback and volume
    """
    def __init__(self):
        self.mpd_client = MPDClient()
        self.mpd_client.connect("localhost", 6600)
        self.update_interval = 1000 # Interval between mpc status update calls (milliseconds)
        self.player_control = ""    # Indicates whether mpd is playing, pausing or has stopped playing music
        self.track_name = ""        # Currently playing song name
        self.track_artist = ""      # Currently playing artist
        self.volume = 0             # Playback volume
        self.time_current = ""      # Currently playing song time
        self.time_total = ""        # Currently playing song duration
        self.time_percentage = 0    # Currently playing song time as a percentage of the song duration
        self.playlist_current = []  # Current playlist song title
        self.repeat = False         #
        self.random = False
        self.single = False
        self.consume = False
        self.updating_library = False

        self.__playlist_current_playing_index = 0
        self.__last_update_time = 0   # For checking last update time (milliseconds)
        self.__status = []            # mpc's current status output
        self.__status_previous = []   # mpc's previous status output

    def __parse_mpc_status(self):
        """ Parses the mpd status """

        # self.updating_library = status_line[:14] == "Updating DB (#"
        status = self.mpd_client.status()
        now_playing = self.mpd_client.currentsong()

        if len(now_playing) > 0:
            self.track_artist = now_playing["artist"]  # Artist of current song
            self.track_name = now_playing["title"]  # Song title of current song
        else:
            self.track_artist = ""
            self.track_name = ""

        self.volume = int(status["volume"])  # Current volume
        self.repeat = status["repeat"] == '1'
        self.random = status["random"] == '1'
        self.single = status["single"] == '1'
        self.consume = status["consume"] == '1'
        self.player_control = status["state"]

        if self.player_control != "stop":
            self.__playlist_current_playing_index = int(status["song"])  # Current playlist index
        else:
            self.__playlist_current_playing_index = -1
        if self.player_control != "stop":
            current_seconds = self.str_to_float(status["elapsed"])
            current_total = self.str_to_float(now_playing["time"])
            self.time_percentage = int(current_seconds / current_total * 100)
        else:
            current_seconds = 0
            current_total = 0
            self.time_percentage = 0

        self.time_current = self.make_time_string(current_seconds)  # Playing time current
        self.time_total = self.make_time_string(current_total)  # Total time current

    def status_get(self):
        """ Updates mpc data, returns True when status data is updated
             Wait at least 'update_interval' milliseconds before updating mpc status data
        """
        if pygame.time.get_ticks() > self.update_interval and pygame.time.get_ticks() - self.__last_update_time < self.update_interval:
            return False
        self.__last_update_time = pygame.time.get_ticks() # Reset update
        self.__parse_mpc_status()   # Parse mpc status output
        return True

    # Control playback
    def player_control_set(self, play_status=None):
        if play_status is None:
            self.status_get()
            return self.player_control
        elif play_status == "play":
            self.mpd_client.play()
        elif play_status == "pause":
            self.mpd_client.pause(1)
        elif play_status == "stop":
            self.mpd_client.stop()
        elif play_status == "next":
            self.mpd_client.next()
        elif play_status == "previous":
            self.mpd_client.previous()

    def player_control_get(self):
        self.status_get()
        return self.player_control

    def play_playlist_item(self, index):
        self.mpd_client.play(index - 1)

    def volume_set(self, percentage):
        if percentage < 0 or percentage > 100: return
        self.mpd_client.setvol(percentage)
        self.volume = percentage

    def volume_set_relative(self, percentage):
        if self.volume + percentage < 0:
            self.mpd_client.setvol(0)
        elif self.volume + percentage > 100:
            self.mpd_client.setvol(100)
        else:
            self.volume += percentage
            self.mpd_client.setvol(self.volume)

    def volume_mute(self):
        self.mpd_client.setvol(0)

    def random_switch(self):
        self.random = not self.random
        if self.random:
            self.mpd_client.random(1)
        else:
            self.mpd_client.random(0)

    def repeat_switch(self):
        self.repeat = not self.repeat
        if self.repeat:
            self.mpd_client.repeat(1)
        else:
            self.mpd_client.repeat(0)

    def single_switch(self):
        self.single = not self.single
        if self.consume:
            self.mpd_client.single(1)
        else:
            self.mpd_client.single(0)

    def consume_switch(self):
        self.consume = not self.consume
        if self.consume:
            self.mpd_client.consume(1)
        else:
            self.mpd_client.consume(0)

    def get_playlist_current(self):
        self.playlist_current = []
        for i in self.mpd_client.playlistinfo():
            self.playlist_current.append(i["id"] + ". " + i["title"])
        return self.playlist_current

    def get_playlist_current_playing_index(self):
        """
        :return: The track number playing on the current playlist.
        """
        self.status_get()
        return self.__playlist_current_playing_index

    def set_playlist_current_playing_index(self, index):
        """ Starts playing item _index_ of the current playlist.

        :param index: The track number to be played
        :return: The current playing index
        """
        if index > 0 and index <= self.playlist_current_count():
            self.mpd_client.playid(index)
            self.__playlist_current_playing_index = index
        return self.__playlist_current_playing_index

    def playlist_current_count(self):
        """
        :return: The number of items in the current playlist
        """
        return len(self.playlist_current)

    def playlist_current_clear(self):
        """ Removes everything from the current playlist """
        self.mpd_client.clear()
        self.playlist_current = []

    def make_time_string(self, seconds):
        minutes = int(seconds / 60)
        seconds_left = int(round(seconds - minutes * 60, 0))
        time_string = str(minutes) + ":"
        seconds_string = ""
        if seconds_left < 10:
            seconds_string = "0" + str(seconds_left)
        else:
            seconds_string = str(seconds_left)
        time_string += seconds_string
        return time_string

    def str_to_float(self, s):
        """ Checks whether a string is an integer.

        :param s: string
        :return: float
        """
        try:
            return float(s)
        except ValueError:
            return float(0)


class MPD(object):
    """ Browsing mpd library and adding to playlist
    """
    def __init__(self):
        self.mpd_control = MPDController()
        self.list_albums = []
        self.list_artists = []
        self.list_songs = []
        self.list_query_results = []

    def is_mpd_running(self):
        """ Checks whether MPD daemon is running.

        :return Boolean for mpd running
        """
        try:
            result_string = subprocess.check_output("mpc status", shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return False
        return True

    def library_update(self):
        """ Updates the mpd library """
        self.mpd_control.mpd_client.update()

    def library_rescan(self):
        """ Rebuild library. """
        self.mpd_control.mpd_client.rescan()

    def __search(self, tag_type):
        """ Searches all entries of a certain type.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :return: A list with search results.
        """
        result_list = self.mpd_control.mpd_client.list(tag_type)
        return result_list

    def __search_first_letter(self, tag_type, first_letter):
        """ Searches all entries of a certain type matching a first letter

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param first_letter: The first letter
        :return: A list with search results.
        """
        all_results = self.mpd_control.mpd_client.list(tag_type)
        end_result = []
        for i in all_results:
            if i[:1].upper() == first_letter.upper():
                end_result.append(i)
        return end_result

    def __search_partial(self, tag_type, part):
        """ Searches all entries of a certain type partially matching search string.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param part: Search string.
        :return: A list with search results.
        """
        test = self.mpd_control.mpd_client.list(tag_type, tag_type, part)
        return test

    def __search_of_type(self, type_result, type_filter, name_filter):
        """ Searching one type depending on another type (very clear description isn't it?)

        :param type_result: The type of result-set generated ["artist"s, "album"s, song"title"s]
        :param type_filter: The type of filter used ["artist"s, "album"s, song"title"s]
        :param name_filter: The name used to filter
        :return:
        """
        return self.mpd_control.mpd_client.list(type_result, type_filter, name_filter)

    def artists_get(self, part=None, only_start=True):
        """ Retrieves all artist names or matching by first letter(s) or partial search string.

        :param part: Search string
        :param only_start: Only search as first letter(s).
        :return: A list of matching artist names.
        """
        if part is None:
            if len(self.list_artists) == 0:
                self.list_artists = self.__search("artist")
            return self.list_artists
        elif only_start:
            self.list_query_results = self.__search_first_letter("artist", part)
        else:
            self.list_query_results = self.__search_partial("artist", part)
        return self.list_query_results

    def albums_get(self, part=None, only_start=True):
        """ Retrieves all album titles or matching by first letter(s) or partial search string.

        :param part: Search string.
        :param only_start: Only search as first letter(s).
        :return: A list of matching album titles.
        """
        if part is None:
            if len(self.list_albums) == 0:
                self.list_albums = self.__search("album")
            return self.list_albums
        elif only_start:
            self.list_query_results = self.__search_first_letter("album", part)
        else:
            self.list_query_results = self.__search_partial("album", part)
        return self.list_query_results

    def songs_get(self, part=None, only_start=True):
        """ Retrieves all song titles or matching by first letter(s) or partial search string

        :param part: Search string
        :param only_start: Only search as first letter(s)
        :return: A list of matching song titles
        """
        if part is None:
            if len(self.list_songs) == 0:
                self.list_songs = self.__search("title")
            return self.list_songs
        elif only_start:
            self.list_query_results = self.__search_first_letter("title", part)
        else:
            self.list_query_results = self.__search_partial("title", part)
        return self.list_query_results

    def artist_albums_get(self, artist_name):
        """ Retrieves artist's albums.

        :param artist_name: The name of the artist to retrieve the albums of.
        :return: A list of album titles.
        """
        return self.__search_of_type("album", "artist", artist_name)

    def artist_songs_get(self, artist_name):
        """ Retrieves artist's songs.

        :param artist_name: The name of the artist to retrieve the songs of.
        :return: A list of song titles
        """
        return self.__search_of_type("title", "artist", artist_name)

    def album_songs_get(self, album_name):
        """ Retrieves all song titles of an album.

        :param album_name: The name of the album
        :return: A list of song titles
        """
        return self.__search_of_type("title", "album", album_name)

    def playlists_get(self, first_letter=None):
        """ Retrieves all playlists or those matching the first letter

        :param first_letter: Letter
        :return: A list of playlist names
        """
        result_list = []
        if first_letter is None:
            for playlist in self.mpd_control.mpd_client.listplaylists():
                result_list.append(playlist["playlist"])
        else:
            for playlist in self.mpd_control.mpd_client.listplaylists():
                if playlist["playlist"][:1].upper() == first_letter.upper():
                    result_list.append(playlist["playlist"])
        return result_list

    def playlist_add(self, tag_type, tag_name, play=False, clear_playlist=False):
        """ Adds songs to the current playlist

        :param tag_type: Kind of add you want to do ["artist", "album", song"title"].
        :param tag_name: The name of the tag_type.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if clear_playlist:
            mpd.mpd_control.playlist_current_clear()
        i = mpd.mpd_control.playlist_current_count()
        self.mpd_control.mpd_client.findadd(tag_type, tag_name)
        if play:
            mpd.mpd_control.play_playlist_item(i + 1)

    def playlist_add_artist(self, artist_name, play=False, clear_playlist=False):
        """ Adds all artist's songs to the current playlist

        :param artist_name: The name of the artist.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add("artist", artist_name, play, clear_playlist)

    def playlist_add_album(self, album_name, play=False, clear_playlist=False):
        """ Adds all album's songs to the current playlist

        :param album_name: The album name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add("album", album_name, play, clear_playlist)

    def playlist_add_song(self, song_name, play=False, clear_playlist=False):
        """ Adds a song to the current playlist

        :param song_name: The song's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add("title", song_name, play, clear_playlist)

    def playlist_add_playlist(self, playlist_name, play=False, clear_playlist=False):
        """ Adds a playlist to the current playlist

        :param playlist_name: The playlist's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if clear_playlist:
            mpd.mpd_control.playlist_current_clear()
        i = mpd.mpd_control.playlist_current_count()
        self.mpd_control.mpd_client.load(playlist_name)
        if play:
            mpd.mpd_control.play_playlist_item(i + 1)


"""            # If updating is finished reload artist, album and song lists
            if self.updating_library and status_line[:14] != "Updating DB (#":
                self.list_artists = self.get_artists()
                self.list_albums = self.get_albums()
                self.list_songs = self.songs_get()
"""

mpd = MPD()