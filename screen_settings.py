"""
screen_settings.py: Settings screen
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
from screen_wifi import *


class ScreenSettings(ScreenModal):
    """ Screen for settings or quitting/shutting down

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """
    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Settings")

        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        label = "Quit Pi-Jukebox"
        self.add_component(ButtonText("btn_quit", self.screen, button_left, 30, button_width, label))
        label = "Playback options"
        self.add_component(ButtonText("btn_playback", self.screen, button_left, 72, button_width, label))
        label = "Entry"
        self.add_component(ButtonText("entry_1", self.screen, button_left, 114, button_width, label))
        label = "Entry"
        self.add_component(ButtonText("entry_2", self.screen, button_left, 156, button_width, label))
        label = "Back"
        self.add_component(ButtonText("btn_return", self.screen, button_left, 198, button_width, label))

    def on_click(self, x, y):
        tag_name = super(ScreenSettings, self).on_click(x, y)
        if tag_name == "btn_playback":
            screen_playback_options = ScreenSettingsPlayback(self.screen)
            screen_playback_options.show()
            self.show()
        elif tag_name == "btn_quit":
            screen_quit = ScreenSettingsQuit(self.screen)
            screen_quit.show()
            self.show()
        elif tag_name == "btn_return":
            self.close()


class ScreenSettingsQuit(ScreenModal):
    """ Screen for quitting pi-jukebox.

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Quit")
        self.window_x = 90
        self.window_y = 45
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True

        self.add_component(ButtonText("btn_quit", screen_rect, self.window_x + 10, self.window_y + 30, 120, "Quit"))
        self.add_component(
            ButtonText("btn_shutdown", screen_rect, self.window_x + 10, self.window_y + 70, 120, "Shutdown Pi"))
        self.add_component(
            ButtonText("btn_cancel", screen_rect, self.window_x + 10, self.window_y + 110, 120, "Cancel"))

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == "btn_quit":
            print ("Bye!")
            sys.exit()
        elif tag_name == "btn_shutdown":
            subprocess.call("sudo shutdown -h now")
        elif tag_name == "btn_cancel":
            self.close()


class ScreenSettingsPlayback(ScreenModal):
    """ Screen for settings playback options

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Playback settings")
        self.add_component(LabelText("lbl_shuffle", screen_rect, 10, 30, 80, 20, "Shuffle"))
        self.add_component(Switch("switch_shuffle", screen_rect, 150, 23))
        self.add_component(LabelText("lbl_repeat", screen_rect, 10, 60, 80, 20, "Repeat"))
        self.add_component(Switch("switch_repeat", screen_rect, 150, 53))
        self.add_component(LabelText("lbl_single", screen_rect, 10, 90, 80, 20, "Single"))
        self.add_component(Switch("switch_single", screen_rect, 150, 83))
        self.add_component(LabelText("lbl_consume", screen_rect, 10, 120, 120, 20, "Consume playlist"))
        self.add_component(Switch("switch_consume", screen_rect, 150, 113))
        self.add_component(ButtonText("btn_update", self.screen, 10, 150, self.window_width - 20, "Update library"))
        self.add_component(ButtonText("btn_return", screen_rect, 10, 192, self.window_width - 20, "Back"))

        self.__initialize()

    def __initialize(self):
        """ Sets the screen controls according to current mpd configuration.
        """
        for key, value in self.components.items():
            if key == "switch_shuffle":
                value.set_on(mpd.mpd_control.random)
            elif key == "switch_repeat":
                value.set_on(mpd.mpd_control.repeat)
            elif key == "switch_single":
                value.set_on(mpd.mpd_control.single)
            elif key == "switch_consume":
                value.set_on(mpd.mpd_control.consume)

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == "switch_shuffle":
            mpd.mpd_control.random_switch()
        elif tag_name == "switch_repeat":
            mpd.mpd_control.repeat_switch()
        elif tag_name == "switch_single":
            mpd.mpd_control.single_switch()
        elif tag_name == "switch_consume":
            mpd.mpd_control.consume_switch()
        elif tag_name == "btn_update":
            mpd.mpd_controller.update_library()
        elif tag_name == "btn_return":
            self.close()