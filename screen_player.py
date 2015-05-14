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
from gui_widgets import *
from mpd_client import *
from settings import *
from screen_settings import *

class Playlist(ItemList):
    """ Displays playlist information.

        :param screen_rect: The display's rect where the library browser is drawn on.
    """
    def __init__(self, screen_rect):
        ItemList.__init__(self, 'list_playing', screen_rect, 52, 46, 216, 189)
        self.item_height = 27
        self.item_active_color = FIFTIES_ORANGE
        self.outline_color = FIFTIES_CHARCOAL
        self.font_color = FIFTIES_YELLOW
        self.outline_visible = False

    def show_playlist(self):
        """ Display the playlist. """
        updated = False
        playing_nr = mpd.get_playlist_current_playing_index()
        if self.list != mpd.get_playlist_current():
            self.list = mpd.get_playlist_current()
            updated = True
        if self.active_item_index != mpd.get_playlist_current_playing_index():
            self.active_item_index = mpd.get_playlist_current_playing_index()
            updated = True
        if updated:
            self.draw()


class ScreenPlaylist(Screen):
    """ The screen containing everything to control playback.
    """
    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon('btn_player', self.screen, ICO_PLAYER, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.screen, ICO_PLAYLIST_ACTIVE, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.screen, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.screen, ICO_DIRECTORY, 3, 125))
        self.add_component(ButtonIcon('btn_settings', self.screen, ICO_SETTINGS, 3, SCREEN_HEIGHT - 37))
        # Player specific buttons
        self.add_component(ButtonIcon('btn_play', self.screen, ICO_PLAY, SCREEN_WIDTH - 51, 45))
        self.add_component(ButtonIcon('btn_stop', self.screen, ICO_STOP, SCREEN_WIDTH - 51, 85))
        self.add_component(ButtonIcon('btn_prev', self.screen, ICO_PREVIOUS, SCREEN_WIDTH - 51, 125))
        self.add_component(ButtonIcon('btn_next', self.screen, ICO_NEXT, SCREEN_WIDTH - 51, 165))
        self.add_component(ButtonIcon('btn_volume', self.screen, ICO_VOLUME, SCREEN_WIDTH - 51, 205))
        # Player specific labels
        self.add_component(LabelText('lbl_track_title', self.screen, 55, 5, SCREEN_WIDTH - 130, 18))
        self.add_component(LabelText('lbl_track_artist', self.screen, 55, 23, SCREEN_WIDTH - 130, 18))
        self.add_component(LabelText('lbl_time', self.screen, SCREEN_WIDTH - 67, 5, 67, 18))
        self.add_component(LabelText('lbl_volume', self.screen, SCREEN_WIDTH - 70, 23, 70, 18))
        # Splits labels from playlist
        self.add_component(Rectangle('rct_split', self.screen, 55, 43, 208, 1))
        # Playlist
        self.add_component(Playlist(self.screen))
        self.components['list_playing'].active_item_index = mpd.get_playlist_current_playing_index()

    def show(self):
        """ Displays the screen. """
        self.components['lbl_time'].draw(mpd.time_current + '/' + mpd.time_total)
        self.components['lbl_volume'].draw('Vol: ' + str(mpd.volume) + '%')
        if mpd.player_control_get() == 'play':
            self.components['btn_play'].set_image_file(ICO_PAUSE)
        else:
            self.components['btn_play'].set_image_file(ICO_PLAY)
        self.components['btn_play'].draw()
        self.components['lbl_track_title'].draw(mpd.track_name)
        self.components['lbl_track_artist'].draw(mpd.track_artist)
        super(ScreenPlaylist, self).show()  # Draw screen
        self.components['list_playing'].show_playlist()
        self.components['list_playing'].show_item_active()  # Makes sure currently playing playlist item is on screen

    def update(self):
        while True:
            try:
                event = mpd.events.popleft()
                if event == 'volume':
                    self.components['lbl_volume'].draw('Vol: ' + str(mpd.volume) + '%')
                elif event == 'playing_index':
                    self.components['list_playing'].show_playlist()
                elif event == 'time_elapsed' or event == 'playing_time_total':
                    self.components['lbl_time'].draw(mpd.time_current + '/' + mpd.time_total)
                elif event == 'playing_title':
                    self.components['lbl_track_title'].draw(mpd.track_name)
                elif event == 'playing_artist':
                    self.components['lbl_track_artist'].draw(mpd.track_artist)
                elif event == 'state':
                    state = mpd.player_control_get()
                    if self.components['btn_play'].image_file != ICO_PAUSE and state == 'play':
                        self.components['btn_play'].draw(ICO_PAUSE)
                    elif self.components['btn_play'].image_file == ICO_PAUSE and state != 'play':
                        self.components['btn_play'].draw(ICO_PLAY)
            except IndexError:
                break

    def on_click(self, x, y):
        """
        :param x: The horizontal click position.
        :param y: The vertical click position.

        :return: Possibly returns a screen index number to switch to.
        """
        tag_name = super(ScreenPlaylist, self).on_click(x, y)
        if tag_name == 'btn_player':
            return 0
        elif tag_name == 'btn_playlist':
            return 1
        elif tag_name == 'btn_library':
            return 2
        elif tag_name == 'btn_directory':
            return 3
        elif tag_name == 'btn_settings':
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == 'btn_play':
            if mpd.player_control_get() == 'play':
                mpd.player_control_set('pause')
                self.components['btn_play'].set_image_file(ICO_PLAY)
            else:
                mpd.player_control_set('play')
                self.components['btn_play'].set_image_file(ICO_PAUSE)
            self.components['btn_play'].draw()
        elif tag_name == 'btn_stop':
            self.components['btn_play'].set_image_file(ICO_PLAY)
            mpd.player_control_set('stop')
        elif tag_name == 'btn_prev':
            mpd.player_control_set('previous')
        elif tag_name == 'btn_next':
            mpd.player_control_set('next')
        elif tag_name == 'btn_volume':
            screen_volume = ScreenVolume(self.screen)
            screen_volume.show()
            self.show()
        elif tag_name == 'list_playing':
            selected_index = self.components['list_playing'].item_selected_index
            if selected_index >= 0:
                mpd.play_playlist_item(selected_index + 1)
                self.components['list_playing'].active_item_index = selected_index
                self.components['list_playing'].draw()


class ScreenPlaying(Screen):
    """ Screen cover art

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_rect):
        Screen.__init__(self, screen_rect)
        # Screen navigation buttons
        self.add_component(ButtonIcon('btn_player', self.screen, ICO_PLAYER_ACTIVE, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.screen, ICO_PLAYLIST, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.screen, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.screen, ICO_DIRECTORY, 3, 125))
        self.add_component(ButtonIcon('btn_settings', self.screen, ICO_SETTINGS, 3, SCREEN_HEIGHT - 37))
        # Player specific buttons
        self.add_component(ButtonIcon('btn_play', self.screen, ICO_PLAY, SCREEN_WIDTH - 51, 5))
        self.add_component(ButtonIcon('btn_stop', self.screen, ICO_STOP, SCREEN_WIDTH - 51, 45))
        self.add_component(ButtonIcon('btn_prev', self.screen, ICO_PREVIOUS, SCREEN_WIDTH - 51, 85))
        self.add_component(ButtonIcon('btn_next', self.screen, ICO_NEXT, SCREEN_WIDTH - 51, 125))
        self.add_component(ButtonIcon('btn_volume', self.screen, ICO_VOLUME, SCREEN_WIDTH - 51, 165))
        # Cover art
        self.add_component(Picture('pic_cover_art', self.screen, 79, 40, 162, 162, mpd.get_cover_art()))
        # Player specific labels
        self.add_component(LabelText('lbl_track_artist', self.screen, 54, 3, 215, 18))
        self.components['lbl_track_artist'].set_alignment(HOR_MID, VERT_MID)
        self.add_component(LabelText('lbl_track_album', self.screen, 54, 19, 215, 18))
        self.components['lbl_track_album'].set_alignment(HOR_MID, VERT_MID)
        self.add_component(LabelText('lbl_track_title', self.screen, 55, SCREEN_HEIGHT - 27, 212, 18))
        self.components['lbl_track_title'].set_alignment(HOR_MID, VERT_MID)
        self.add_component(LabelText('lbl_time_current', self.screen, SCREEN_WIDTH - 51, 205, 48, 18))
        self.components['lbl_time_current'].set_alignment(HOR_MID, VERT_MID)
        self.add_component(LabelText('lbl_time_total', self.screen, SCREEN_WIDTH - 51, 221, 48, 18))
        self.components['lbl_time_total'].set_alignment(HOR_MID, VERT_MID)
        self.add_component(Slider2('slide_time', self.screen, 55, SCREEN_HEIGHT - 35, 212, 3))

    def show(self):
        """ Displays the screen. """
        self.components['lbl_time_current'].draw(mpd.time_current)
        self.components['lbl_time_total'].draw(mpd.time_total)
        if mpd.player_control_get() == 'play':
            self.components['btn_play'].set_image_file(ICO_PAUSE)
        else:
            self.components['btn_play'].set_image_file(ICO_PLAY)
        self.components['btn_play'].draw()
        self.components['pic_cover_art'].draw(mpd.get_cover_art())
        self.components['lbl_track_title'].draw(mpd.track_name)
        self.components['lbl_track_artist'].draw(mpd.track_artist)
        self.components['lbl_track_album'].draw(mpd.track_album)
        super(ScreenPlaying, self).show()  # Draw screen

    def update(self):
        while True:
            try:
                event = mpd.events.popleft()
                if event == 'playing_index':
                    self.components['pic_cover_art'].draw(mpd.get_cover_art())
                elif event == 'time_elapsed':
                    self.components['lbl_time_current'].draw(mpd.time_current)
                    self.components['slide_time'].draw(mpd.time_percentage)
                elif event == 'playing_time_total':
                    self.components['lbl_time_total'].draw(mpd.time_total)
                elif event == 'playing_title':
                    self.components['lbl_track_title'].draw(mpd.track_name)
                elif event == 'playing_artist':
                    self.components['lbl_track_artist'].draw(mpd.track_artist)
                elif event == 'playing_album':
                    self.components['lbl_track_album'].draw(mpd.track_album)
                elif event == 'state':
                    if self.components['btn_play'].image_file != ICO_PAUSE and mpd.player_control_get() == 'play':
                        self.components['btn_play'].draw(ICO_PAUSE)
                    elif self.components['btn_play'].image_file == ICO_PAUSE and mpd.player_control_get() != 'play':
                        self.components['btn_play'].draw(ICO_PLAY)
            except IndexError:
                break

    def on_click(self, x, y):
        tag_name = super(ScreenPlaying, self).on_click(x, y)
        if tag_name == 'btn_player':
            return 0
        elif tag_name == 'btn_playlist':
            return 1
        elif tag_name == 'btn_library':
            return 2
        elif tag_name == 'btn_directory':
            return 3
        elif tag_name == 'btn_settings':
            setting_screen = ScreenSettings(self.screen)
            setting_screen.show()
            self.show()
        elif tag_name == 'btn_play':
            if mpd.player_control_get() == 'play':
                mpd.player_control_set('pause')
                self.components['btn_play'].set_image_file(ICO_PLAY)
            else:
                mpd.player_control_set('play')
                self.components['btn_play'].set_image_file(ICO_PAUSE)
            self.components['btn_play'].draw()
        elif tag_name == 'btn_stop':
            self.components['btn_play'].set_image_file(ICO_PLAY)
            mpd.player_control_set('stop')
        elif tag_name == 'btn_prev':
            mpd.player_control_set('previous')
        elif tag_name == 'btn_next':
            mpd.player_control_set('next')
        elif tag_name == 'btn_volume':
            screen_volume = ScreenVolume(self.screen)
            screen_volume.show()
            self.show()


class ScreenVolume(ScreenModal):
    """ Screen setting volume

        :param screen_rect: The display's rectangle where the screen is drawn on.
    """

    def __init__(self, screen_rect):
        ScreenModal.__init__(self, screen_rect, "Volume")
        self.window_x = 15
        self.window_y = 52
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.title_color = FIFTIES_GREEN
        self.outline_color = FIFTIES_GREEN

        self.add_component(ButtonIcon('btn_mute', screen_rect, ICO_VOLUME_MUTE, self.window_x + 5, self.window_y + 25))
        self.components['btn_mute'].x_pos = self.window_x + self.window_width / 2 - self.components[
                                                                                        'btn_mute'].width / 2
        self.add_component(
            ButtonIcon('btn_volume_down', self.screen, ICO_VOLUME_DOWN, self.window_x + 5, self.window_y + 25))
        self.add_component(
            ButtonIcon('btn_volume_up', self.screen, ICO_VOLUME_UP, self.window_width - 40, self.window_y + 25))
        self.add_component(
            Slider('slide_volume', self.screen, self.window_x + 8, self.window_y + 63, self.window_width - 18, 30))
        self.components['slide_volume'].progress_percentage_set(mpd.volume)
        self.add_component(
            ButtonText('btn_back', self.screen, self.window_x + self.window_width / 2 - 23, self.window_y + 98, 46, 32,
                       "Back"))
        self.components['btn_back'].button_color = FIFTIES_TEAL

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_mute':
            mpd.volume_mute_switch()
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'btn_volume_down':
            mpd.volume_set_relative(-10)
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'btn_volume_up':
            mpd.volume_set_relative(10)
            self.components['slide_volume'].progress_percentage_set(mpd.volume)
        elif tag_name == 'slide_volume':
            mpd.volume_set(self.components['slide_volume'].progress_percentage)
        elif tag_name == 'btn_back':
            self.close()
        if mpd.volume == 0 or mpd.volume_mute_get():
            self.components['btn_mute'].set_image_file(ICO_VOLUME_MUTE_ACTIVE)
        else:
            self.components['btn_mute'].set_image_file(ICO_VOLUME_MUTE)
        self.components['btn_mute'].draw()
