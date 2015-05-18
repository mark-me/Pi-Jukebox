"""
======================================================================
**gui_screens.py**: Building blocks for creating screens and dialogues
======================================================================
"""

__author__ = 'Mark Zwart'

import sys, pygame
from pygame.locals import *
import time
import math
from gui_widgets import *
from settings import *

""" Mouse related variables """
GESTURE_MOVE_MIN = 50  # Minimum movement in pixels to call it a move
GESTURE_CLICK_MAX = 15  # Maximum movement in pixels to call it a click
GESTURE_PRESS_MIN = 500  # Minimum time to call a click a long press
# Gesture enumeration
GESTURE_NONE = -1
GESTURE_CLICK = 0
GESTURE_SWIPE_LEFT = 1
GESTURE_SWIPE_RIGHT = 2
GESTURE_SWIPE_UP = 3
GESTURE_SWIPE_DOWN = 4
GESTURE_LONG_PRESS = 5
GESTURE_DRAG_VERTICAL = 6
GESTURE_DRAG_HORIZONTAL = 7

# Standard icons
ICO_INFO = RESOURCES + 'icon_info.png'
ICO_WARNING = RESOURCES + 'icon_warning.png'
ICO_ERROR = RESOURCES + 'icon_warning.png'


class GestureDetector(object):
    """ Class for detecint mouse gestures
    """
    def __init__(self):
        self.gesture = GESTURE_NONE
        self.x_start = 0
        self.y_start = 0
        self.x_moved = 0
        self.y_moved = 0
        self.drag_length = 0
        self.press_duration = 0
        self.x_start, self.y_start = pygame.mouse.get_pos()

    def capture_gesture(self, event):
        """ Mouse event loop, runs from mouse down to mouse up event.

            :param event: pygame event.
        """

        if event.type != pygame.MOUSEBUTTONDOWN:
            return GESTURE_NONE

        gesture_ended = False

        mouse_down_time = pygame.time.get_ticks()  # Start timer to detect long mouse clicks
        self.x_start, self.y_start = pygame.mouse.get_pos()  # Get click position (= start position for swipe)
        pygame.mouse.get_rel()  # Start tracking mouse movement
        mouse_down_time = pygame.time.get_ticks()

        while not gesture_ended:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONUP:  # Gesture end
                    self.press_duration = pygame.time.get_ticks() - mouse_down_time
                    self.x_moved, self.y_moved = pygame.mouse.get_rel()  # Movements since start gesture
                    self.gesture = self.__determine_gesture_type()  # Determines the kind of gesture used
                    gesture_ended = True

        return self.gesture

    def __determine_gesture_type(self):
        """ Determines the kind of gesture.

            :return: The type of gesture [:py:const:GESTURE_CLICK, :py:const:GESTURE_SWIPE_DOWN, :py:const:GESTURE_SWIPE_UP, :py:const:GESTURE_SWIPE_LEFT, :py:const:GESTURE_SWIPE_RIGHT]
        """
        x = self.x_moved
        y = self.y_moved
        if self.press_duration < GESTURE_PRESS_MIN:
            if abs(x) <= GESTURE_MOVE_MIN:
                if abs(y) <= GESTURE_MOVE_MIN:
                    if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
                        return GESTURE_CLICK  # Tap (click)
                    else:
                        return -1  # No idea what the user did
                elif y > GESTURE_MOVE_MIN:  # Down swipe
                    return GESTURE_SWIPE_DOWN
                elif y < -GESTURE_MOVE_MIN:  # Up swipe
                    return GESTURE_SWIPE_UP
            elif abs(y) <= GESTURE_MOVE_MIN:
                if x > GESTURE_MOVE_MIN:  # Left swipe
                    return GESTURE_SWIPE_LEFT
                elif x < -GESTURE_MOVE_MIN:  # Right swipe
                    return GESTURE_SWIPE_RIGHT
        elif self.press_duration >= GESTURE_PRESS_MIN:
            if abs(x) <= GESTURE_MOVE_MIN:
                if abs(y) <= GESTURE_MOVE_MIN:
                    if abs(x) < GESTURE_CLICK_MAX and abs(y) < GESTURE_CLICK_MAX:
                        return GESTURE_LONG_PRESS  # Long press
                    else:
                        return -1  # No idea what the user did
                elif abs(y) > GESTURE_MOVE_MIN:
                    return GESTURE_DRAG_VERTICAL  # Vertical drag
            elif abs(y) <= GESTURE_MOVE_MIN:
                if abs(x) > GESTURE_MOVE_MIN:
                    return GESTURE_DRAG_HORIZONTAL  # Horizontal drag
        else:
            pass
            return GESTURE_NONE


class Screen(object):
    """ Basic screen used for displaying widgets. This type of screen should be used for the entire program.

        :param screen_rect: The screen's rectangle where the screen is drawn on

        :ivar components: Dictionary holding the screen's widgets with a tag_name as key and the widget as value
        :ivar color: The screen's background color, default = :py:const:BLACK
    """

    def __init__(self, screen_rect):
        self.screen = screen_rect
        self.components = {}  # Interface dictionary
        self.color = BLACK

    def add_component(self, widget):
        """ Adds components to component list, thus ensuring a component is found on a mouse event.

            :param widget: The widget that should be added to the dictionary.
        """
        self.components[widget.tag_name] = widget

    def show(self):
        """ Displays the screen. """
        self.screen.fill(self.color)
        for key, value in self.components.items():
            if value.visible:
                value.draw()
        pygame.display.flip()

    def on_click(self, x, y):
        """ Determines which component was clicked and fires it's click function in turn.

            :param x: The horizontal click position.
            :param y: The vertical click position.

            :return: The tag_name of the clicked component.
        """
        for key, value in self.components.items():
            if isinstance(value, ButtonIcon) or isinstance(value, ButtonText) or \
                    isinstance(value, Switch) or isinstance(value, Slider) and value.visible or \
                    isinstance(value, Picture):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    value.on_click(x, y)
                    return key
            if isinstance(value, ItemList) and value.visible:
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    value.clicked_item(x, y)
                    return key
            if isinstance(value, WidgetContainer):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    return value.on_click(x, y)


    def on_swipe(self, x, y, swipe_type):
        """ Relays swipe to ItemList components for next(up)/previous(down) swipes for ItemLists.

            :param x: The horizontal start position of the swipe move.
            :param y: The vertical start position of the swipe move.
            :param swipe_type: The type of swipe movement done.
        """
        for key, value in self.components.items():
            if isinstance(value, ItemList):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    if swipe_type == GESTURE_SWIPE_UP:
                        value.show_next_items()
                    if swipe_type == GESTURE_SWIPE_DOWN:
                        value.show_prev_items()


class Screens(object):
    """ Manages screens of type Screen.
        Handles screen switching, clicking and swiping and mpd status updating.

        :ivar screen_list: List containing all screen objects.
        :ivar current_index: Points to current screen in screen_list.
        :ivar mouse_down_pos: Mouse position on mouse down.
    """

    def __init__(self):
        self.screen_list = []  #
        self.current_index = 0
        self.gesture_detect = GestureDetector()

    def show(self):
        """ Show the current screen """
        self.screen_list[self.current_index].show()

    def add_screen(self, screen):
        """ Adds screen to list """
        self.screen_list.append(screen)

    def process_mouse_event(self, event):
        """ Processes mouse events. """
        if event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.MOUSEBUTTONDOWN:
            return None
        gesture = self.gesture_detect.capture_gesture(event)
        x = self.gesture_detect.x_start
        y = self.gesture_detect.y_start

        if gesture == GESTURE_CLICK:  # Fire click function
            ret_value = self.screen_list[self.current_index].on_click(x, y)  # Relay tap/click to active screen
            # If the screen requests a screen switch
            if ret_value >= 0 and ret_value < len(self.screen_list):
                self.current_index = ret_value
                self.show()
        # Switch screens with horizontal swiping
        if gesture == GESTURE_SWIPE_LEFT and self.current_index - 1 >= 0:
            self.current_index -= 1
            self.show()
        if gesture == GESTURE_SWIPE_RIGHT and self.current_index + 1 < len(self.screen_list):
            self.current_index += 1
            self.show()
        # Relay vertical swiping to active screen controls
        if gesture == GESTURE_SWIPE_UP or gesture == GESTURE_SWIPE_DOWN:
            x = self.gesture_detect.x_start
            y = self.gesture_detect.y_start
            self.screen_list[self.current_index].on_swipe(x, y, gesture)


class ScreenModal(Screen):
    """ Screen with its own event capture loop.

        :param screen_rect: The display's rectangle where the screen is drawn on.
        :param title: The title displayed at the top of the screen.

        :ivar title: The title displayed at the top of the screen.
    """

    def __init__(self, screen_rect, title):
        Screen.__init__(self, screen_rect)
        self.title = title
        self.window_x = 0
        self.window_y = 0
        self.window_width = SCREEN_WIDTH
        self.window_height = SCREEN_HEIGHT
        self.return_object = None
        self.close_screen = False
        self.title_color = FIFTIES_ORANGE
        self.outline_shown = False
        self.outline_color = FIFTIES_ORANGE
        self.gesture_detect = GestureDetector()

    def show(self):
        """ Displays screen and starts own event capture loop.

            :return: A return object.
        """
        self.close_screen = False
        self.__draw_window()
        # Draw components
        for key, value in self.components.items():
            value.draw()
        pygame.display.flip()
        self.event_loop()  # Start the loop capturing user input
        return self.return_object

    def close(self):
        """ Closes event loop.

            :return: Window's return object.
        """
        self.close_screen = True
        return self.return_object

    def __draw_window(self):
        """ Draws window border and title. """
        # Draws backdrop screen
        if self.window_width < SCREEN_WIDTH or self.window_height < SCREEN_HEIGHT:
            backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            backdrop.set_alpha(128)
            backdrop.fill(BLACK)
            SCREEN.blit(backdrop, (0, 0))
        # Drawing window
        window_rect = Rect(self.window_x, self.window_y, self.window_width, self.window_height)
        pygame.draw.rect(self.screen, BLACK, window_rect)
        # Draw outline
        if self.outline_shown:
            pygame.draw.rect(self.screen, self.outline_color, window_rect, 1)
        # Window title bar
        title_rect = Rect(self.window_x, self.window_y, self.window_width, 20)
        pygame.draw.rect(self.screen, self.title_color, title_rect)
        font_height = FONT.size("Tg")[1]
        font_width = FONT.size(self.title)[0]
        image = FONT.render(self.title, True, BLACK)
        self.screen.blit(image, (title_rect.centerx - font_width / 2, title_rect.centery - font_height / 2))

    def event_loop(self):
        """ The window's event loop """
        while not self.close_screen:
            self.event_loop_hook()
            pygame.time.wait(PYGAME_EVENT_DELAY)
            for event in pygame.event.get():

                gesture = self.gesture_detect.capture_gesture(event)

                # Relays click to active screen controls
                if gesture == GESTURE_CLICK:
                    self.action(self.on_click(self.gesture_detect.x_start, self.gesture_detect.y_start))
                # Relay vertical swiping to active screen controls
                elif gesture == GESTURE_SWIPE_UP or gesture == GESTURE_SWIPE_DOWN:
                    self.on_swipe(self.gesture_detect.x_start, self.gesture_detect.y_start, gesture)

                # Possibility to close modal window with 'Esc' key
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.return_object = None
                    self.close_screen = True

    def action(self, tag_name):
        """ Virtual function for event-related execution. """
        pass

    def event_loop_hook(self):
        """ Virtual function where you can add functions you want to execute during the event loop """
        pass


class ScreenMessage(ScreenModal):
    """ A screen that displays a message.

        :param screen_rect: The display's rectangle where the screen is drawn on.
        :param caption: The title displayed at the top of the screen.
        :param text: Text displayed in the screen.
        :param message_type: Determines the lay-out of the screen [information, warning, error]
    """
    def __init__(self, screen_rect, caption, text, message_type=None):
        ScreenModal.__init__(self, screen_rect, caption)
        if message_type == 'information':
            self.add_component(
                Picture('pic_icon', self.screen, self.window_x + 5, self.window_y + 30, 48, 48, ICO_INFO))
            self.title_color = FIFTIES_GREEN
        elif message_type == 'warning':
            self.add_component(
                Picture('pic_icon', self.screen, self.window_x + 5, self.window_y + 30, 48, 48, ICO_WARNING))
            self.title_color = FIFTIES_YELLOW
        elif message_type == 'error':
            self.add_component(
                Picture('pic_icon', self.screen, self.window_x + 5, self.window_y + 30, 48, 48, ICO_ERROR))
            self.title_color = FIFTIES_ORANGE
        else:
            self.title_color = FIFTIES_TEAL
        x = self.window_x + 55
        y = self.window_y + 30
        width = self.window_width - x - 5
        height = self.window_height - y - 32
        self.add_component(Memo('memo_text', self.screen, x, y, width, height, text))
        self.add_component(ButtonText('btn_ok', self.screen, self.window_x + self.window_width - 60,
                                      self.window_y + self.window_height - 37, 55, 32, "OK"))
        self.components['btn_ok'].button_color = FIFTIES_YELLOW

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_ok':
            self.close()


class ScreenYesNo(ScreenModal):
    """ A screen that displays a message.

        :param screen_rect: The display's rectangle where the screen is drawn on.
        :param caption: The title displayed at the top of the screen.
        :param text: Text displayed in the screen.
    """

    def __init__(self, screen_rect, caption, text):
        ScreenModal.__init__(self, screen_rect, caption)
        self.window_x = 70
        self.window_y = 60
        self.window_width -= 2 * self.window_x
        self.window_height -= 2 * self.window_y
        self.outline_shown = True
        self.add_component(Picture('pic_icon', self.screen, self.window_x + 5, self.window_y + 30, 48, 48, ICO_WARNING))
        self.title_color = FIFTIES_ORANGE
        width = self.window_width - 58
        height = self.window_height - self.window_y - 32
        self.add_component(Memo('memo_text', self.screen, self.window_x + 55, self.window_y + 32, width, height, text))
        self.add_component(ButtonText('btn_yes', self.screen, self.window_x + self.window_width - 60,
                                      self.window_y + self.window_height - 37, 55, 32, "Yes"))
        self.components['btn_yes'].button_color = FIFTIES_ORANGE
        self.add_component(
            ButtonText('btn_no', self.screen, self.window_x + 5, self.window_y + self.window_height - 37, 55, 32, "No"))
        self.components['btn_no'].button_color = FIFTIES_ORANGE

    def on_click(self, x, y):
        tag_name = super(ScreenModal, self).on_click(x, y)
        if tag_name == 'btn_yes':
            self.return_object = 'yes'
            self.close()
        elif tag_name == 'btn_no':
            self.return_object = 'no'
            self.close()
