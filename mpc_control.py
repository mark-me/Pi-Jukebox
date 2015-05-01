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

MPC_TYPE_ARTIST = "artist"
MPC_TYPE_ALBUM = "album"
MPC_TYPE_SONGS = "title"


class MPDController(object):
    """ Controls playback and volume
    """
    def __init__(self):
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
        line_count = 0
        for status_line in self.__status:

            self.updating_library = status_line[:14] == "Updating DB (#"

            if not self.updating_library and line_count == 0 and status_line[:7] != "volume:":
                self.track_artist = status_line[0:status_line.find(" - ")]                          # Artist of current song
                self.track_name = status_line[status_line.find(" - ")+3:status_line.find("\n")]     # Song title of current song

            if status_line[:7] == "volume:":
                volume = status_line[status_line.find("volume:")+7:status_line.find("%")]
                if self.is_int(volume):
                    self.volume = int(volume)   # Current volume
                else:
                    self.volume = 0
                self.repeat = status_line[status_line.find("repeat: ")+8:status_line.find("repeat: ")+10] == "on"
                self.random = status_line[status_line.find("random: ")+8:status_line.find("random: ")+10] == "on"
                self.single = status_line[status_line.find("single: ")+8:status_line.find("single: ")+10] == "on"
                self.consume = status_line[status_line.find("consume: ")+9:status_line.find("consume: ")+11] == "on"
            if status_line[:1] == "[":
                self.player_control = status_line[status_line.find("\n[")+2:status_line.find("]")]
                self.__playlist_current_playing_index = int(status_line[status_line.find("#")+1:status_line.find("/")]) - 1   # Current playlist index
                self.time_current = status_line[status_line.find(":")-2:status_line.find(":")+3]                    # Playing time current
                self.time_total = status_line[status_line.find("/", status_line.find("/")+1)+1:status_line.find("/", status_line.find("/")+1)+5] # Playing time total
                self.time_percentage = status_line[status_line.find("(")+1:status_line.find(")")-1]

            line_count += 1

        if line_count == 1:
            self.player_control = "stopped"
            self.track_artist = ""
            self.track_name = ""
            self.playlist_current_playing_index = 0
            self.time_current = "0:00"
            self.time_total = "0:00"
            self.time_percentage = 0

    # Updates mpc data, returns True when status data is updated
    def status_get(self):
        # Wait at least 'update_interval' milliseconds before updating mpc status data
        if pygame.time.get_ticks() > self.update_interval and pygame.time.get_ticks() - self.__last_update_time < self.update_interval:
            return False
        self.__last_update_time = pygame.time.get_ticks() # Reset update
        self.__status = subprocess.check_output("mpc status", shell=True, stderr=subprocess.STDOUT).split("\n")  # Read mpc status
        # If the status is the same as the last, indicate nothing was updated
        if self.__status == self.__status_previous: return False
        self.__status_previous = self.__status  # Set current status as previous for next comparison
        self.__parse_mpc_status()   # Parse mpc status output
        return True

    # Control playback
    def player_control_set(self, play_status=None):
        if play_status is None:
            self.status_get()
            return self.player_control
        elif play_status == "play":
            subprocess.call("mpc play", shell=True)
        elif play_status == "pause":
            subprocess.call("mpc pause", shell=True)
        elif play_status == "stop":
            subprocess.call("mpc stop", shell=True)
        elif play_status == "next":
            subprocess.call("mpc next", shell=True)
        elif play_status == "previous":
            subprocess.call("mpc prev", shell=True)

    def player_control_get(self):
        self.status_get()
        return self.player_control

    def play_playlist_item(self, number):
        subprocess.call("mpc play " + str(number), shell=True)

    def volume_set(self, percentage):
        if percentage < 0 or percentage > 100: return
        print ("mpc volume " + str(percentage))
        subprocess.call("mpc volume " + str(percentage), shell=True)
        self.volume = percentage

    def volume_set_relative(self, percentage):
        if self.volume + percentage < 0:
            self.volume_set(0)
        elif self.volume + percentage > 100:
            self.volume_set(100)
        else:
            self.volume_set(self.volume+percentage)

    def random_set(self):
        subprocess.call("mpc random", shell=True)

    def repeat_on_set(self):
        subprocess.call("mpc repeat", shell=True)

    def single_on_set(self):
        subprocess.call("mpc single on", shell=True)

    def consume_on_set(self):
        subprocess.call("mpc consume on", shell=True)

    def get_playlist_current(self):
        self.playlist_current = subprocess.check_output("mpc playlist -f \"[%position%. %title%]\"", shell=True, stderr=subprocess.STDOUT).split("\n")
        return self.playlist_current

    def get_playlist_current_playing_index(self):
        self.status_get()
        return self.__playlist_current_playing_index

    def set_playlist_current_playing_index(self, index):
        if index > 0 and index <= self.playlist_current_count():
            subprocess.call("mpc play " + str(index + 1), shell=True)
            self.__playlist_current_playing_index = index
        return self.__playlist_current_playing_index

    def playlist_current_count(self):
        return len(self.playlist_current)

    def playlist_current_clear(self):
        subprocess.call("mpc clear", shell=True)
        self.playlist_current = []

    def playlist_current_crop(self):
        subprocess.call("mpc crop", shell=True)

    def is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False


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

    def update_library(self):
        subprocess.call("mpc update")

    def __format_results(self, result_string):
        result_list = result_string.split("\n")
        result_list.sort()
        for i in result_list:
            if i == "":
                result_list.pop(0)     # Remove oddity of mpc
        return result_list

    def __search(self, tag_type):
        try:
            result_string = subprocess.check_output("mpc list " + tag_type, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return []
        return self.__format_results(result_string)

    def __search_first_letter(self, tag_type, first_letter):
        try:
            result_string = subprocess.check_output("mpc list " + tag_type + " | grep ^" + first_letter, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return []
        return self.__format_results(result_string)

    def __search_partial(self, tag_type, part):
        command = "mpc list " + tag_type + " | grep -i \"" + part + "\""
        try:
            result_string = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return []
        return self.__format_results(result_string)

    def __search_of_type(self, type_result, type_filter, name_filter):
        command = "mpc list " + type_result + " " + type_filter + " \"" + name_filter + "\""
        try:
            result_string = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return []
        return self.__format_results(result_string)

    def artists_get(self, part=None, only_start=True):
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
        return self.__search_of_type("album", "artist", artist_name)

    def artist_songs_get(self, artist_name):
        return self.__search_of_type("title", "artist", artist_name)

    def album_songs_get(self, album_name):
        return self.__search_of_type("title", "album", album_name)

    def playlists_get(self, first_letter=None):
        try:
            if first_letter is None:
                result_string = subprocess.check_output("mpc lsplaylists", shell=True, stderr=subprocess.STDOUT)
            else:
                result_string = subprocess.check_output("mpc lsplaylists | grep ^" + first_letter, shell=True,
                                                        stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            return []
        return self.__format_results(result_string)

    def playlist_add(self, tag_type, tag_name, play=False, clear_playlist=False):
        if clear_playlist:
            mpd.mpd_control.playlist_current_clear()
        i = mpd.mpd_control.playlist_current_count()
        subprocess.call("mpc findadd " + tag_type + " \"" + tag_name + "\"", shell=True)
        if play:
            mpd.mpd_control.play_playlist_item(i)

    def playlist_add_artist(self, artist_name, play=False, clear_playlist=False):
        self.playlist_add("artist", artist_name, play, clear_playlist)

    def playlist_add_album(self, album_name, play=False, clear_playlist=False):
        self.playlist_add("album", album_name, play, clear_playlist)

    def playlist_add_song(self, song_name, play=False, clear_playlist=False):
        self.playlist_add("title", song_name, play, clear_playlist)

    def playlist_add_playlist(self, playlist_name, play=False, clear_playlist=False):
        if clear_playlist:
            mpd.mpd_control.playlist_current_clear()
        i = mpd.mpd_control.playlist_current_count()
        subprocess.call("mpc load " + " \"" + playlist_name + "\"", shell=True)
        if play:
            mpd.mpd_control.play_playlist_item(i)


"""            # If updating is finished reload artist, album and song lists
            if self.updating_library and status_line[:14] != "Updating DB (#":
                self.list_artists = self.get_artists()
                self.list_albums = self.get_albums()
                self.list_songs = self.songs_get()
"""

mpd = MPD()