import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from interface_widgets import *
from mpc_control import *
from settings import *
from screen_settings import *
"""
screen_player.py: contains everything for the playback screen.

Classes:
* Playlist      - Displays playlist information
* ScreenPlayer  - The screen containing everything to control playback
"""


class Playlist(ItemList):
    """ Displays playlist information
    """
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        ItemList.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.item_active_color = FIFTIES_ORANGE
        self.outline_color = FIFTIES_CHARCOAL
        self.font_color = FIFTIES_YELLOW
        self.outline_visible = False

    def show_playlist(self):
        updated = False
        playing_nr = mpd_controller.get_playlist_current_playing_index()
        if self.list != mpd_controller.get_playlist_current():
            self.list = mpd_controller.get_playlist_current()
            updated = True
        if self.item_selected != mpd_controller.get_playlist_current_playing_index():
            self.item_selected = mpd_controller.get_playlist_current_playing_index()
            updated = True
        if updated:
            self.draw()


class ScreenPlayer(Screen):
    """ The screen containing everything to control playback
    """
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER_ACTIVE, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS, 3, screen_height - 37))

        # Player specific buttons
        self.add_component(ButtonIcon("btn_play", self.screen, ICO_PLAY, screen_width - 52, 42))
        self.add_component(ButtonIcon("btn_prev", self.screen, ICO_PREVIOUS, screen_width - 52, 82))
        self.add_component(ButtonIcon("btn_next", self.screen, ICO_NEXT, screen_width - 52, 122))
        self.add_component(ButtonIcon("btn_volume_up", self.screen, ICO_VOLUME_UP, screen_width - 52, 164))
        self.add_component(ButtonIcon("btn_volume_down", self.screen, ICO_VOLUME_DOWN, screen_width - 52, 204))

        # Player specific labels
        self.add_component(LabelText("lbl_track_title", self.screen, 55, 5, screen_width - 130, 18))
        self.add_component(LabelText("lbl_track_artist", self.screen, 55, 23, 213, 18))
        self.add_component(LabelText("lbl_time", self.screen, screen_width - 75, 5, 75, 18))
        self.add_component(LabelText("lbl_volume", self.screen, screen_width - 70, 23, 70, 18))

        # Playlist
        self.add_component(Playlist("list_playing", self.screen, 52, 50, 216, 190))
        self.components["list_playing"].active_item_index = mpd_controller.get_playlist_current_playing_index()

    def show(self):
        super(ScreenPlayer, self).show()
        self.update()

    def update(self):
        self.components["list_playing"].active_item_index = mpd_controller.get_playlist_current_playing_index()
        self.components["list_playing"].show_playlist()
        if self.components["lbl_track_title"].caption != mpd_controller.track_name:
            self.components["lbl_track_title"].draw(mpd_controller.track_name)
        if self.components["lbl_track_artist"].caption != mpd_controller.track_artist:
            self.components["lbl_track_artist"].draw(mpd_controller.track_artist)
        self.components["lbl_time"].draw(mpd_controller.time_current + "/" + mpd_controller.time_total)
        self.components["lbl_volume"].draw("Vol: " + str(mpd_controller.volume) + "%")
        if self.components["btn_play"].image_file != ICO_PAUSE and mpd_controller.player_control == "playing":
            self.components["btn_play"].set_image_file(ICO_PAUSE)
            self.components["btn_play"].draw()
        elif self.components["btn_play"].image_file == ICO_PAUSE and mpd_controller.player_control != "playing":
            self.components["btn_play"].set_image_file(ICO_PLAY)
            self.components["btn_play"].draw()

    def on_click(self, x, y):
        tag_name = super(ScreenPlayer, self).on_click(x, y)
        if tag_name == "btn_home":
            return 0
        elif tag_name == "btn_library":
            return 1
        elif tag_name == "btn_settings":
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == "btn_play":
            if mpd_controller.player_control_get() == "playing":
                mpd_controller.player_control_set("pause")
            else:
                mpd_controller.player_control_set("play")
        elif tag_name == "btn_prev":
            mpd_controller.player_control_set("previous")
        elif tag_name == "btn_next":
            mpd_controller.player_control_set("next")
        elif tag_name == "btn_volume_up":
            mpd_controller.volume_set_relative(10)
        elif tag_name == "btn_volume_down":
            mpd_controller.volume_set_relative(-10)
        elif tag_name == "list_playing":
            mpd_controller.play_playlist_item(self.components["list_playing"].item_selected+1)


