"""
=======================================================
**screen_directory.py**: MPD Directory browsing screen
=======================================================

"""
__author__ = 'Mark Zwart'

from settings import *
from gui_screens import *
from gui_widgets import *
from screen_settings import *


class ScreenNavigation(WidgetContainer):
    def __init__(self, tag_name, surface, button_active):
        WidgetContainer.__init__(self, tag_name, surface, 0, 0, 53, 240)
        self.__radio_mode = False
        self.add_component(ButtonIcon('btn_player', self.surface, ICO_PLAYER_FILE_ACTIVE, 3, 5))
        self.add_component(ButtonIcon('btn_playlist', self.surface, ICO_PLAYLIST, 3, 45))
        self.add_component(ButtonIcon('btn_library', self.surface, ICO_LIBRARY, 3, 85))
        self.add_component(ButtonIcon('btn_directory', self.surface, ICO_DIRECTORY, 3, 125))
        self.add_component(ButtonIcon('btn_radio', self.surface, ICO_RADIO, 3, 165))
        self.add_component(ButtonIcon('btn_settings', self.surface, ICO_SETTINGS, 3, 205))
        self.button_active_set(button_active)

    def on_click(self, x, y):
        tag_name = super(ScreenNavigation, self).on_click(x, y)
        return tag_name

    def radio_mode_set(self, radio_mode_bool):
        self.__radio_mode = radio_mode_bool
        if radio_mode_bool:
            if self.__button_active == 'btn_player':
                self.components['btn_player'].icon_file_set(ICO_PLAYER_RADIO_ACTIVE)
            else:
                self.components['btn_player'].icon_file_set(ICO_PLAYER_RADIO)
        else:
            if self.__button_active == 'btn_player':
                self.components['btn_player'].icon_file_set(ICO_PLAYER_FILE_ACTIVE)
            else:
                self.components['btn_player'].icon_file_set(ICO_PLAYER_FILE)
        self.draw()

    def button_active_set(self, button_active):
        self.__button_active = button_active
        if self.__radio_mode:
            self.components['btn_player'].icon_file_set(ICO_PLAYER_RADIO)
        else:
            self.components['btn_player'].icon_file_set(ICO_PLAYER_FILE)
        self.components['btn_playlist'].icon_file_set(ICO_PLAYLIST)
        self.components['btn_library'].icon_file_set(ICO_LIBRARY)
        self.components['btn_directory'].icon_file_set(ICO_DIRECTORY)
        self.components['btn_radio'].icon_file_set(ICO_RADIO)

        if button_active == 'btn_player':
            if self.__radio_mode:
                self.components['btn_player'].icon_file_set(ICO_PLAYER_RADIO_ACTIVE)
            else:
                self.components['btn_player'].icon_file_set(ICO_PLAYER_FILE_ACTIVE)
        elif button_active == 'btn_playlist':
            self.components['btn_playlist'].icon_file_set(ICO_PLAYLIST_ACTIVE)
        elif button_active == 'btn_library':
            self.components['btn_library'].icon_file_set(ICO_LIBRARY_ACTIVE)
        elif button_active == 'btn_directory':
            self.components['btn_directory'].icon_file_set(ICO_DIRECTORY_ACTIVE)
        elif button_active == 'btn_radio':
            self.components['btn_radio'].icon_file_set(ICO_RADIO_ACTIVE)

        self.draw()
