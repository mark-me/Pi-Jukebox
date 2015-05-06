#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mzwa
#
# Created:     20-04-2015
# Copyright:   (c) mzwa 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from interface_widgets import *
from settings import *
from screen_keyboard import *


class WifiConnection(object):
    def __init__(self):
        self.connected = False
        self.SSID_list = []
        self.adapter = 'wlan0'
        self.SSID = ''
        self.passphrase = ''

    def get_SSIDs (self):
        self.SSID_list = subprocess.check_output("sudo iwlist " + self.adapter + " scan | grep ESSID", shell=True,
                                                 stderr=subprocess.STDOUT).split("\n")

    def connect_to(self, SSID, passphrase):
        self.SSID = SSID
        self.passphrase = passphrase
        command = "ip link set " + self.adapter + " up"
        subprocess.call(command, shell=True)
        command = "sudo wpa_passphrase " + SSID + " " + PASSPHRASE + " >> /etc/wpa_supplicant.conf"
        subprocess.call(command, shell=True)
        command = "wpa_supplicant -B -i" + self.adapter + " -c/etc/wpa_supplicant.conf -Dwext && dhclient " + self.adapter
        subprocess.call(command, shell=True)
        command = "ip link set " + self.adapter + " up"
        subprocess.call("ip link set wlan0 up", shell=True)
        return self.is_connected()

    def is_connected(self):
        status = subprocess.check_output("iw dev " + self.adapter + " link", shell=True, stderr=subprocess.STDOUT).split("\n")
        status_line = status[0]
        if status_line == "Not connected.":
            return False
        if status_line[:13] == "Connected to":
            return True


class ScreenWifi(ScreenModal):
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect, "Setup WiFi connection")
        self.add_components(ItemList('list_SSID', self.screen, 55, 40, 210, 165))
        self.add_component(ButtonText('btn_connect', self.__init__screen, 235, 205, 80, text='Connect'))




