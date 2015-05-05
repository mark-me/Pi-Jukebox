"""
=======================================================
**screen_player.py**: Playback screen.
=======================================================
"""

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


class Playlist(ItemList):
    """ Displays playlist information.

        :param screen_rect: The display's rect where the library browser is drawn on.
    """

    def __init__(self, screen_rect):
        ItemList.__init__(self, "list_playing", screen_rect, 52, 46, 216, 189)
        self.item_height = 27
        self.item_active_color = FIFTIES_ORANGE
        self.outline_color = FIFTIES_CHARCOAL
        self.font_color = FIFTIES_YELLOW
        self.outline_visible = False

    def show_playlist(self):
        """ Display the playlist. """
        updated = False
        playing_nr = mpd.mpd_control.get_playlist_current_playing_index()
        if self.list != mpd.mpd_control.get_playlist_current():
            self.list = mpd.mpd_control.get_playlist_current()
            updated = True
        if self.active_item_index != mpd.mpd_control.get_playlist_current_playing_index():
            self.active_item_index = mpd.mpd_control.get_playlist_current_playing_index()
            updated = True
        if updated:
            self.draw()


class ScreenPlayer(Screen):
    """ The screen containing everything to control playback.
    """
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon("btn_home", self.screen, ICO_PLAYER_ACTIVE, 3, 5))
        self.add_component(ButtonIcon("btn_library", self.screen, ICO_LIBRARY, 3, 45))
        self.add_component(ButtonIcon("btn_settings", self.screen, ICO_SETTINGS, 3, SCREEN_HEIGHT - 37))

        # Player specific buttons
        self.add_component(ButtonIcon("btn_play", self.screen, ICO_PLAY, SCREEN_WIDTH - 52, 45))
        self.add_component(ButtonIcon("btn_prev", self.screen, ICO_PREVIOUS, SCREEN_WIDTH - 52, 85))
        self.add_component(ButtonIcon("btn_next", self.screen, ICO_NEXT, SCREEN_WIDTH - 52, 125))
        self.add_component(ButtonIcon("btn_volume_up", self.screen, ICO_VOLUME_UP, SCREEN_WIDTH - 52, 165))
        self.add_component(ButtonIcon("btn_volume_down", self.screen, ICO_VOLUME_DOWN, SCREEN_WIDTH - 52, 205))

        # Player specific labels
        self.add_component(LabelText("lbl_track_title", self.screen, 55, 5, SCREEN_WIDTH - 130, 18))
        self.add_component(LabelText("lbl_track_artist", self.screen, 55, 23, 213, 18))
        self.add_component(LabelText("lbl_time", self.screen, SCREEN_WIDTH - 67, 5, 67, 18))
        self.add_component(LabelText("lbl_volume", self.screen, SCREEN_WIDTH - 70, 23, 70, 18))

        self.add_component(Rectangle("rct_split", self.screen, 55, 43, 208, 1))

        # Playlist
        self.add_component(Playlist(self.screen))
        self.components["list_playing"].active_item_index = mpd.mpd_control.get_playlist_current_playing_index()

    def show(self):
        """ Displays the screen. """
        self.components["list_playing"].show_item_active()
        super(ScreenPlayer, self).show()  # Draw screen
        self.update()  # Update mpd status to components

    def update(self):
        """ Update controls that depend on mpd's status. """

        self.components["list_playing"].active_item_index = mpd.mpd_control.get_playlist_current_playing_index()
        self.components["list_playing"].show_playlist()
        if self.components["lbl_track_title"].caption != mpd.mpd_control.track_name:
            self.components["lbl_track_title"].draw(mpd.mpd_control.track_name)
        if self.components["lbl_track_artist"].caption != mpd.mpd_control.track_artist:
            self.components["lbl_track_artist"].draw(mpd.mpd_control.track_artist)
        self.components["lbl_time"].draw(mpd.mpd_control.time_current + "/" + mpd.mpd_control.time_total)
        self.components["lbl_volume"].draw("Vol: " + str(mpd.mpd_control.volume) + "%")
        if self.components["btn_play"].image_file != ICO_PAUSE and mpd.mpd_control.player_control == "playing":
            self.components["btn_play"].set_image_file(ICO_PAUSE)
            self.components["btn_play"].draw()
        elif self.components["btn_play"].image_file == ICO_PAUSE and mpd.mpd_control.player_control != "playing":
            self.components["btn_play"].set_image_file(ICO_PLAY)
            self.components["btn_play"].draw()

    def on_click(self, x, y):
        """
        :param x: The horizontal click position.
        :param y: The vertical click position.

        :return: Possibly returns a screen index number to switch to.
        """
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
            if mpd.mpd_control.player_control_get() == "playing":
                mpd.mpd_control.player_control_set("pause")
                self.components["btn_play"].set_image_file(ICO_PLAY)
            else:
                mpd.mpd_control.player_control_set("play")
                self.components["btn_play"].set_image_file(ICO_PAUSE)
            self.components["btn_play"].draw()
        elif tag_name == "btn_prev":
            mpd.mpd_control.player_control_set("previous")
        elif tag_name == "btn_next":
            mpd.mpd_control.player_control_set("next")
        elif tag_name == "btn_volume_up":
            mpd.mpd_control.volume_set_relative(10)
            self.components["lbl_volume"].draw("Vol: " + str(mpd.mpd_control.volume) + "%")
        elif tag_name == "btn_volume_down":
            mpd.mpd_control.volume_set_relative(-10)
            self.components["lbl_volume"].draw("Vol: " + str(mpd.mpd_control.volume) + "%")
        elif tag_name == "list_playing":
            selected_index = self.components["list_playing"].item_selected_index
            if selected_index > 0:
                mpd.mpd_control.play_playlist_item(selected_index + 1)
                self.components["list_playing"].active_item_index = selected_index
                self.components["list_playing"].draw()


