import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
from interface_widgets import *
from mpc_control import *
from settings import *


class Playlist(ItemList):
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        ItemList.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.item_active_color = FIFTIES_ORANGE
        self.outline_color = FIFTIES_CHARCOAL
        self.font_color = FIFTIES_YELLOW
        self.outline_visible = False

    def show_playlist(self):
        updated = False
        playing_nr = mpc_controller.get_playlist_current_playing_index()
        if self.list != mpc_controller.get_playlist_current():
            self.list = mpc_controller.get_playlist_current()
            updated = True
        if self.item_selected != mpc_controller.get_playlist_current_playing_index():
            self.item_selected = mpc_controller.get_playlist_current_playing_index()
            updated = True
        if updated:
            self.draw()


class ScreenPlayer(Screen):
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER_ACTIVE, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS, 3, screen_height - 77))
        self.add_component(ButtonIcon("btn_exit", self.screen, ICO_EXIT, 3, screen_height - 37))

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
        self.components["list_playing"].active_item_index = mpc_controller.get_playlist_current_playing_index()

    def show(self):
        super(ScreenPlayer, self).show()
        self.update()

    def update(self):
        self.components["list_playing"].active_item_index = mpc_controller.get_playlist_current_playing_index()
        self.components["list_playing"].show_playlist()
        if self.components["lbl_track_title"].caption != mpc_controller.track_name:
            self.components["lbl_track_title"].draw(mpc_controller.track_name)
        if self.components["lbl_track_artist"].caption != mpc_controller.track_artist:
            self.components["lbl_track_artist"].draw(mpc_controller.track_artist)
        self.components["lbl_time"].draw(mpc_controller.time_current + "/" + mpc_controller.time_total)
        self.components["lbl_volume"].draw("Vol: " + str(mpc_controller.volume) + "%")
        if self.components["btn_play"].image_file != ICO_PAUSE and mpc_controller.player_control == "playing":
            self.components["btn_play"].set_image_file(ICO_PAUSE)
            self.components["btn_play"].draw()
        elif self.components["btn_play"].image_file == ICO_PAUSE and mpc_controller.player_control != "playing":
            self.components["btn_play"].set_image_file(ICO_PLAY)
            self.components["btn_play"].draw()

    def on_click(self, x, y):
        tag_name = super(ScreenPlayer, self).on_click(x, y)
        if tag_name == "btn_home":
            return 0
        elif tag_name == "btn_library":
            return 1
        elif tag_name == "btn_settings":
            return 2
        elif tag_name == "btn_exit":
            sys.exit()

        elif tag_name == "btn_play":
            if mpc_controller.get_player_control() == "playing":
                mpc_controller.set_player_control("pause")
            else:
                mpc_controller.set_player_control("play")

        elif tag_name == "btn_prev":
            mpc_controller.set_player_control("previous")
        elif tag_name == "btn_next":
            mpc_controller.set_player_control("next")
        elif tag_name == "btn_volume_up":
            mpc_controller.set_volume_relative(10)
        elif tag_name == "btn_volume_down":
            mpc_controller.set_volume_relative(-10)
        elif tag_name == "list_playing":
            mpc_controller.play_playlist_item(self.components["list_playing"].item_selected+1)


