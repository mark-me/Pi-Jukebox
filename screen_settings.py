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


class ScreenSettings(ScreenModal):
    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Settings")

        button_left = self.window_x + 10
        button_width = self.window_width - 2 * button_left
        label = "Update library"
        self.add_component(ButtonText("btn_update", self.screen, button_left, 30, button_width, label))
        label = "Setup wifi"
        self.add_component(ButtonText("btn_wifi", self.screen, button_left, 72, button_width, label))
        label = "Shut down Raspberry Pi"
        self.add_component(ButtonText("btn_shutdown", self.screen, button_left, 114, button_width, label))
        label = "Quit Pi-Jukebox "
        self.add_component(ButtonText("btn_quit", self.screen, button_left, 156, button_width, label))
        label = "Cancel "
        self.add_component(ButtonText("btn_cancel", self.screen, button_left, 198, button_width, label))

    def on_click(self, x, y):
        tag_name = super(ScreenSettings, self).on_click(x, y)
        if tag_name == "btn_update":
            mpc_controller.update_library()
        elif tag_name == "btn_wifi":
            screen_wifi = ScreenWifi()
        elif tag_name == "btn_shutdown":
            subprocess.call("sudo shutdown -h now")
        elif tag_name == "btn_quit":
            print ("Bye!")
            sys.exit()
        elif tag_name == "btn_cancel":
            self.close()
