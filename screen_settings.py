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
from screen_wifi import *


class ScreenSettings(Screen):
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS_ACTIVE, 3, screen_height - 77))
        self.add_component(ButtonIcon("btn_exit", self.screen, ICO_EXIT, 3, screen_height - 37))

        label = "Update library"
        self.add_component(ButtonText("btn_update", self.screen, 55, 50, 260, label))
        label = "Setup wifi"
        self.add_component(ButtonText("btn_wifi", self.screen, 55, 92, 260, label))
        #label = "Replace playlist and play"
        #self.add_component(ButtonText("btn_replace", self.screen, 55, 134, 260, label))
        label = "Quit Pi-Jukebox "
        self.add_component(ButtonText("btn_quit", self.screen, 55, 176, 260, label))

    def on_click(self, x, y):
        tag_name = super(ScreenSettings, self).on_click(x, y)
        if tag_name == "btn_home":
            return 0
        elif tag_name == "btn_library":
            return 1
        elif tag_name == "btn_settings":
            return 2
        elif tag_name == "btn_exit":
            sys.exit()
        elif tag_name == "btn_update":
            mpc_controller.update_library()
        elif tag_name == "btn_wifi":
            screen_wifi = ScreenWifi()
        elif tag_name == "btn_quit":
            print ("Bye!")
            sys.exit()
