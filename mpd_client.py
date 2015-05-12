"""
==================================================================
**mpd_client.py**: controlling and monitoring mpd via python-mpd2.
==================================================================
"""

import sys, pygame
import time
import subprocess
import os
import glob
import mpd
from collections import deque
from mutagen import File


MPD_TYPE_ARTIST = 'artist'
MPD_TYPE_ALBUM = 'album'
MPD_TYPE_SONGS = 'title'

DEFAULT_COVER = 'default_cover_art.png'

reload(sys)
sys.setdefaultencoding('utf8')


class MPDController(object):
    """ Controls playback and volume
    """
    def __init__(self):
        self.mpd_client = mpd.MPDClient()
        self.host = 'localhost'
        self.port = 6600
        self.update_interval = 1000 # Interval between mpc status update calls (milliseconds)
        self.track_name = ""        # Currently playing song name
        self.track_artist = ""      # Currently playing artist
        self.track_album = ""       # Album the currently playing song is on
        self.track_file = ""  # File with path relative to MPD music directory
        self.volume = 0             # Playback volume
        self.__time_current_sec = 0  # Currently playing song time (seconds)
        self.time_current = ""  # Currently playing song time (string format)
        self.__time_total_sec = 0  # Currently playing song duration (seconds)
        self.time_total = ""  # Currently playing song duration (string format)
        self.time_percentage = 0    # Currently playing song time as a percentage of the song duration
        self.playlist_current = []  # Current playlist song title
        self.repeat = False         #
        self.random = False
        self.single = False
        self.consume = False
        self.updating_library = False
        self.music_directory = ""
        self.events = deque([])  # Queue of mpd events
        # Database search results
        self.searching_artist = ""  # Search path user goes through
        self.searching_album = ""
        self.list_albums = []
        self.list_artists = []
        self.list_songs = []
        self.list_query_results = []

        self.__current_song = None  # Dictionary containing currently playing song info
        self.__current_song_changed = False
        self.__player_control = ''  # Indicates whether mpd is playing, pausing or has stopped playing music
        self.__muted = False          # Indicates whether muted
        self.__playlist_current_playing_index = 0
        self.__last_update_time = 0   # For checking last update time (milliseconds)
        self.__status = None  # mps's current status output

    def connect(self):
        """ Connects to mpd server.

            :return: Boolean indicating if successfully connected to mpd server.
        """
        try:
            self.mpd_client.connect(self.host, self.port)
        except Exception:
            return False
        self.artists_get()
        self.albums_get()
        self.songs_get()
        return True

    def disconnect(self):
        """ Closes the connection to the mpd server. """
        self.mpd_client.close()
        self.mpd_client.disconnect()

    def __parse_mpc_status(self):
        """ Parses the mpd status and fills mpd event queue

            :return: Boolean indicating if the status was changed
        """
        current_seconds = 0
        current_total = 0
        try:
            current_song = self.mpd_client.currentsong()
        except Exception:
            return False

        if self.__current_song != current_song and len(current_song) > 0: # Changed to a new song
            self.__current_song = current_song
            self.track_name = current_song['title']      # Song title of current song
            if 'artist' in current_song:
                self.track_artist = current_song['artist']  # Artist of current song
            else:
                self.track_artist = "Unknown"
            if 'album' in current_song:
                self.track_album = current_song['album']  # Album the current song is on
            else:
                self.track_album = "Unknown"
            self.track_file = current_song['file']
            current_total = self.str_to_float(current_song['time'])
            self.__time_total_sec = current_total
            self.time_total = self.make_time_string(current_total)  # Total time current
            self.__current_song_changed = True
        elif len(current_song) == 0:  # Changed to no current song
            self.__current_song = None
            self.track_name = ""
            self.track_artist = ""
            self.track_album = ""
            self.track_file = ""
            self.time_percentage = 0
            self.__time_total_sec = 0
            self.time_total = self.make_time_string(0)  # Total time current
            self.__current_song_changed = True

        if self.__current_song_changed:
            self.events.append('playing_title')
            self.events.append('playing_artist')
            self.events.append('playing_album')
            self.events.append('playing_time_total')
            self.events.append('playing_time_percentage')

        try:
            status = self.mpd_client.status()
        except Exception:
            return False
        if self.__status == status:
            return False

        self.__status = status
        if self.volume != int(status['volume']):  # Current volume
            self.volume = int(status['volume'])
            self.events.append(['volume', self.volume])
            self.__muted = self.volume == 0

        if self.repeat != status['repeat'] == '1':
            self.repeat = status['repeat'] == '1'
            self.events.append('repeat')

        if self.random != status['random'] == '1':
            self.random = status['random'] == '1'
            self.events.append('random')

        if self.single != status['single'] == '1':
            self.single = status['single'] == '1'
            self.events.append('single')

        if self.consume != status['consume'] == '1':
            self.consume = status['consume'] == '1'
            self.events.append('consume')

        if self.__player_control != status['state']:
            self.__player_control = status['state']
            self.events.append('player_control')

        if self.__player_control != 'stop':
            if self.__playlist_current_playing_index != int(status['song']):  # Current playlist index
                self.__playlist_current_playing_index = int(status['song'])
                self.events.append('playing_index')
            current_seconds = self.str_to_float(status['elapsed'])
            if self.__time_current_sec != current_seconds:  # Playing time current
                self.__time_current_sec = current_seconds
                self.time_percentage = int(self.__time_current_sec / self.__time_total_sec * 100)
                self.time_current = self.make_time_string(current_seconds)
                self.events.append('time_elapsed')
        else:
            if self.__playlist_current_playing_index != -1:
                self.__playlist_current_playing_index = -1
                self.events.append('playing_index')
            if self.__time_current_sec != 0:
                self.__time_current_sec = 0
                self.time_current = self.make_time_string(0)  # Playing time current
                self.time_percentage = 0
                self.events.append('time_elapsed')

        return True

    def status_get(self):
        """ Updates mpc data, returns True when status data is updated. Wait at
            least 'update_interval' milliseconds before updating mpc status data.

            :return: Returns boolean whether updated or not.
        """
        time_elapsed = pygame.time.get_ticks() - self.__last_update_time
        if pygame.time.get_ticks() > self.update_interval and time_elapsed < self.update_interval:
            return False
        self.__last_update_time = pygame.time.get_ticks() # Reset update
        return self.__parse_mpc_status()   # Parse mpc status output

    def current_song_changed(self):
        if self.__current_song_changed:
            self.__current_song_changed = False
            return True
        else:
            return False

    def get_cover_art(self, dest_file_name="covert_art.jpg"):
        if self.track_file == "":
            return DEFAULT_COVER
        try:
            music_file = File(self.music_directory + self.track_file)
        except IOError:
            return DEFAULT_COVER
        cover_art = None
        if 'covr' in music_file:
            cover_art = music_file.tags['covr'].data
        elif 'APIC:' in music_file:
            cover_art = music_file.tags['APIC:'].data
        else:
            return DEFAULT_COVER

        with open(dest_file_name, 'wb') as img:
            img.write(cover_art) # write artwork to new image
        return dest_file_name

    def player_control_set(self, play_status):
        """ Controls playback

            :param play_status: Playback action ['play', 'pause', 'stop', 'next', 'previous'].
        """
        if play_status == 'play':
            if self.__player_control == 'pause':
                self.mpd_client.pause(0)
            else:
                self.mpd_client.play()
        elif play_status == 'pause':
            self.mpd_client.pause(1)
        elif play_status == 'stop':
            self.mpd_client.stop()
        elif play_status == 'next':
            self.mpd_client.next()
        elif play_status == 'previous':
            self.mpd_client.previous()

    def player_control_get(self):
        """ :return: Current playback mode. """
        self.status_get()
        return self.__player_control

    def play_playlist_item(self, index):
        """ Starts playing in playlist on item.

            :param index: Playlist item index
        """
        self.mpd_client.play(index - 1)

    def volume_set(self, percentage):
        """ Sets volume in absolute percentage.

            :param percentage: Percentage at which volume should be set.
        """
        if percentage < 0 or percentage > 100: return
        self.mpd_client.setvol(percentage)
        self.volume = percentage

    def volume_set_relative(self, percentage):
        """ Sets volume relatively to current volume.

            :param percentage: Percentage point volume increase.
        """
        if self.volume + percentage < 0:
            self.volume = 0
            self.mpd_client.setvol(0)
        elif self.volume + percentage > 100:
            self.volume = 100
            self.mpd_client.setvol(100)
        else:
            self.volume += percentage
            self.mpd_client.setvol(self.volume)

    def volume_mute_switch(self):
        """ Switches volume muting on or off. """
        if self.__muted:
            self.mpd_client.setvol(self.volume)
            self.__muted = False
        else:
            self.mpd_client.setvol(0)
            self.__muted = True

    def volume_mute_get(self):
        return self.__muted

    def random_switch(self):
        """ Switches random playing on or off. """
        self.random = not self.random
        if self.random:
            self.mpd_client.random(1)
        else:
            self.mpd_client.random(0)

    def repeat_switch(self):
        """ Switches repeat playing on or off. """
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
        """ Switches playlist consuming on or off. """
        self.consume = not self.consume
        if self.consume:
            self.mpd_client.consume(1)
        else:
            self.mpd_client.consume(0)

    def get_playlist_current(self):
        self.playlist_current = []
        track_no = 0
        for i in self.mpd_client.playlistinfo():
            track_no += 1
            self.playlist_current.append(str(track_no) + '. ' + i['title'])
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
        seconds_left = int(round(seconds - (minutes * 60), 0))
        if seconds_left > 59:
            seconds_left = 59
        time_string = str(minutes) + ':'
        seconds_string = ''
        if seconds_left < 10:
            seconds_string = '0' + str(seconds_left)
        else:
            seconds_string = str(seconds_left)
        time_string += seconds_string
        return time_string

    def str_to_float(self, s):
        try:
            return float(s)
        except ValueError:
            return float(0)

    def library_update(self):
        """ Updates the mpd library """
        self.mpd_client.update()

    def library_rescan(self):
        """ Rebuild library. """
        self.mpd_client.rescan()

    def __search(self, tag_type):
        """ Searches all entries of a certain type.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :return: A list with search results.
        """
        self.list_query_results = self.mpd_client.list(tag_type)
        return self.list_query_results

    def __search_first_letter(self, tag_type, first_letter):
        """ Searches all entries of a certain type matching a first letter

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param first_letter: The first letter
        :return: A list with search results.
        """
        temp_results = []
        for i in self.list_query_results:
            if i[:1].upper() == first_letter.upper():
                temp_results.append(i)
        self.list_query_results = temp_results
        return self.list_query_results

    def __search_partial(self, tag_type, part):
        """ Searches all entries of a certain type partially matching search string.

        :param tag_type: ["artist"s, "album"s, song"title"s]
        :param part: Search string.
        :return: A list with search results.
        """
        all_results = self.mpd_client.list(tag_type)
        self.list_query_results = []
        for i in all_results:
            result = i.upper()
            if result.find(part.upper()) > -1:
                self.list_query_results.append(i)
        return self.list_query_results

    def __search_of_type(self, type_result, type_filter, name_filter):
        """ Searching one type depending on another type (very clear description isn't it?)

        :param type_result: The type of result-set generated ["artist"s, "album"s, song"title"s]
        :param type_filter: The type of filter used ["artist"s, "album"s, song"title"s]
        :param name_filter: The name used to filter
        :return:
        """
        if self.searching_artist == "" and self.searching_album == "":
            self.list_query_results = self.mpd_client.list(type_result, type_filter, name_filter)
        elif self.searching_artist != "" and self.searching_album == "":
            self.list_query_results = self.mpd_client.list(type_result, 'artist', self.searching_artist, type_filter,
                                                           name_filter)
        elif self.searching_artist == "" and self.searching_album != "":
            self.list_query_results = self.mpd_client.list(type_result, 'album', self.searching_album, type_filter,
                                                           name_filter)
        elif self.searching_artist != "" and self.searching_album != "":
            self.list_query_results = self.mpd_client.list(type_result, 'artist', self.searching_artist, 'album',
                                                           self.searching_album, type_filter, name_filter)
        return self.list_query_results

    def artists_get(self, part=None, only_start=True):
        """ Retrieves all artist names or matching by first letter(s) or partial search string.

        :param part: Search string
        :param only_start: Only search as first letter(s).
        :return: A list of matching artist names.
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_artists) == 0:
                self.list_artists = self.__search('artist')
            return self.list_artists
        elif only_start:
            self.list_query_results = self.__search_first_letter('artist', part)
        else:
            self.list_query_results = self.__search_partial('artist', part)
        return self.list_query_results

    def albums_get(self, part=None, only_start=True):
        """ Retrieves all album titles or matching by first letter(s) or partial search string.

        :param part: Search string.
        :param only_start: Only search as first letter(s).
        :return: A list of matching album titles.
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_albums) == 0:
                self.list_albums = self.__search('album')
            return self.list_albums
        elif only_start:
            self.list_query_results = self.__search_first_letter('album', part)
        else:
            self.list_query_results = self.__search_partial('album', part)
        return self.list_query_results

    def songs_get(self, part=None, only_start=True):
        """ Retrieves all song titles or matching by first letter(s) or partial search string

        :param part: Search string
        :param only_start: Only search as first letter(s)
        :return: A list of matching song titles
        """
        self.searching_artist = ""
        self.searching_album = ""
        if part is None:
            if len(self.list_songs) == 0:
                self.list_songs = self.__search('title')
            return self.list_songs
        elif only_start:
            self.list_query_results = self.__search_first_letter('title', part)
        else:
            self.list_query_results = self.__search_partial('title', part)
        return self.list_query_results

    def artist_albums_get(self, artist_name):
        """ Retrieves artist's albums.

        :param artist_name: The name of the artist to retrieve the albums of.
        :return: A list of album titles.
        """
        self.searching_artist = artist_name
        return self.__search_of_type('album', 'artist', artist_name)

    def artist_songs_get(self, artist_name):
        """ Retrieves artist's songs.

        :param artist_name: The name of the artist to retrieve the songs of.
        :return: A list of song titles
        """
        self.searching_artist = artist_name
        return self.__search_of_type('title', 'artist', artist_name)

    def album_songs_get(self, album_name):
        """ Retrieves all song titles of an album.

        :param album_name: The name of the album
        :return: A list of song titles
        """
        self.searching_album = album_name
        return self.__search_of_type('title', 'album', album_name)

    def playlists_get(self, first_letter=None):
        """ Retrieves all playlists or those matching the first letter

        :param first_letter: Letter
        :return: A list of playlist names
        """
        result_list = []
        if first_letter is None:
            for playlist in self.mpd_client.listplaylists():
                result_list.append(playlist['playlist'])
        else:
            for playlist in self.mpd_client.listplaylists():
                if playlist['playlist'][:1].upper() == first_letter.upper():
                    result_list.append(playlist['playlist'])
        return result_list

    def playlist_add(self, tag_type, tag_name, play=False, clear_playlist=False):
        """ Adds songs to the current playlist

        :param tag_type: Kind of add you want to do ["artist", "album", song"title"].
        :param tag_name: The name of the tag_type.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        if self.searching_artist == "" and self.searching_album == "":
            self.mpd_client.findadd(tag_type, tag_name)
        elif self.searching_artist != "" and self.searching_album == "":
            self.mpd_client.findadd('artist', self.searching_artist, tag_type, tag_name)
        elif self.searching_artist == "" and self.searching_album != "":
            self.mpd_client.findadd('album', self.searching_album, tag_type, tag_name)
        elif self.searching_artist != "" and self.searching_album != "":
            self.mpd_client.findadd('artist', self.searching_artist, 'album', self.searching_album, tag_type, tag_name)
        if play:
            self.play_playlist_item(i + 1)

    def playlist_add_artist(self, artist_name, play=False, clear_playlist=False):
        """ Adds all artist's songs to the current playlist

        :param artist_name: The name of the artist.
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add('artist', artist_name, play, clear_playlist)

    def playlist_add_album(self, album_name, play=False, clear_playlist=False):
        """ Adds all album's songs to the current playlist

        :param album_name: The album name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add('album', album_name, play, clear_playlist)

    def playlist_add_song(self, song_name, play=False, clear_playlist=False):
        """ Adds a song to the current playlist

        :param song_name: The song's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        self.playlist_add('title', song_name, play, clear_playlist)

    def playlist_add_playlist(self, playlist_name, play=False, clear_playlist=False):
        """ Adds a playlist to the current playlist

        :param playlist_name: The playlist's name
        :param play: Boolean indicating whether you want to start playing what was just added.
        :param clear_playlist: Boolean indicating whether to remove all previous entries from the current playlist.
        """
        if clear_playlist:
            self.playlist_current_clear()
        i = self.playlist_current_count()
        self.mpd_client.load(playlist_name)
        if play:
            self.play_playlist_item(i + 1)


"""            # If updating is finished reload artist, album and song lists
            if self.updating_library and status_line[:14] != "Updating DB (#":
                self.list_artists = self.get_artists()
                self.list_albums = self.get_albums()
                self.list_songs = self.songs_get()
"""

mpd = MPDController()