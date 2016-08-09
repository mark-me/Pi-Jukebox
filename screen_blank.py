"""
=======================================================
**screen_blank.py**: Blank screen.
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
from pij_screen_navigation import *
from settings import *
from config_file import *


class ScreenBlank(ScreenModal):
    """ Screensaver.

        :param screen_rect: The directory's rect where the library browser is drawn on.
    """

    def __init__(self):
        ScreenModal.__init__(self, screen, station_name)
        self.station_name = station_name
        self.station_URL = station_URL
        self.title_color = BLACK
        self.initialize()
        self.return_type = ""

    def on_click(self, x, y):
        """ Action that should be performed on a click. """
        tag_name = super(ScreenModal, self).on_click(x, y)
        self.close()
