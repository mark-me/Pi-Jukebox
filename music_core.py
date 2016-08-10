# This file is part of pi-jukebox.
#
# pi-jukebox is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pi-jukebox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pi-jukebox. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2015- by Mark Zwart, <mark.zwart@pobox.com>
__author__ = 'mark'

import sys, pygame
import time
import subprocess
import os
import glob
import mpd
from collections import deque
from mutagen import File
from music_model import *


class MPDConnector(object):
    def __init__(self):
        self.server = mpd.MPDClient()
        self.host = 'localhost'
        self.port = 6600
        self.update_interval = 1000  # Interval between mpc status update calls (milliseconds)
        self.history = None
        self.library = None
        self.mixer = None
        self.playback = PlaybackController(self.server)
        self.playlists = None
        self.tracklist = None

    def connect(self):
        """ Connects to mpd server.

            :return: Boolean indicating if successfully connected to mpd server.
        """
        try:
            self.server.connect(self.host, self.port)
        except Exception:
            return False
        self.playback = MPDPlaybackController(self.server)
        self.history = None
        self.library = None
        self.mixer = None
        self.playlists = None
        self.tracklist = None
        return True

    def disconnect(self):
        """ Closes the connection to the mpd server. """
        self.server.close()
        self.server.disconnect()


class MPDPlaybackState(object):
    """
    Enum of playback states.
    """
    PAUSED = 'paused'  #: Constant representing the paused state.
    PLAYING = 'playing'  #: Constant representing the playing state.
    STOPPED = 'stopped'  #: Constant representing the stopped state.


class MPDPlaybackController(object):
    def __init__(self, server):
        self.server = server
        self.server_type
        self._current_track = None
        self._state = PlaybackState.STOPPED

    def get_current_track(self):
        return self._current_track

    def get_state(self):

    def get_time_position(self):

    def next(self):

    def pause(self):

    def play(self):

    def previous(self):

    def resume(self):

    def seek(self, time_position):

    def set_state(self, new_state):

    def stop(self):


class MPDTracklistController(object):
    def __init__(self, server):
        self.server = server
        self.random = False
        self.single = False
        self.consume = False
        self.repeat = False
        self.radio_mode = False
        self.playlist_current = []

    def add(self, tracks=None, at_position=None, uri=None, uris=None):

    def get_data(self):
        mpd_status = None
        try:
            status = self.server.status()
        except Exception:
            return False
        self.repeat = mpd_status['repeat'] == '1'
        self.random = mpd_status['random'] == '1'
        self.single = mpd_status['single'] == '1'
        self.consume = mpd_status['consume'] == '1'

        if not self.radio_mode:
            self.playlist_current = self.server.mpd_playlistinfo()

    def clear(self):

    def consume_get(self):
        return self.consume

    def consume_set(self, value):
        self.single = value
        if self.playback_state.single:
            self.server.single(1)
        else:
            self.server.single(0)

    def length_get(self):

    def random_get(self):
        return self.random

    def random_set(self, value):
        """ Switches random playing on or off. """
        self.random = value
        if self.random:
            self.server.random(1)
        else:
            self.server.random(0)

    def repeat_get(self):
        return self.repeat

    def repeat_set(self, value):
        """ Switches repeat playing on or off. """
        self.repeat = value
        if self.repeat:
            self.server.repeat(1)
        else:
            self.server.repeat(0)

    def single_get(self):
        return self.single

    def single_set(self, value):
        self.single = value
        if self.single:
            self.server.single(1)
        else:
            self.server.single(0)

    def tracks_get(self):
        return self.playlist_current

    def move(self, start, end, to_position):

    def slice(self, start, end):


class HistoryController(object):
    def __init__(self):

    def history_get(self):

    def length_get(self):


class LibraryController(object):
    def __init__(self):

    def browse(self, uri):

    def get_distinct(self, field, query=None):

    def get_images(self, uris):

    def lookup(self, uri=None, uris=None):

    def refresh(self, uri=None):

    def search(self, query=None, uris=None, exact=False, **kwargs):


class MixerController(object):
    def __init__(self):

    def mute_get(self):

    def mute_set(self, value):

    def volume_get(self):

    def volume_set(self, percentage):
