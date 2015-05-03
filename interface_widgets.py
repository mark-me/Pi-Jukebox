"""
=======================================================
**interface_widgets.py**: graphical widgets for the GUI
=======================================================
"""

__author__ = 'Mark Zwart'

import sys, pygame
from pygame.locals import *
import time
from settings import *

# Alignment variables
HOR_LEFT = 0
HOR_MID = 1
HOR_RIGHT = 2
VERT_TOP = 0
VERT_MID = 1
VERT_BOTTOM = 2


class Widget(object):
    """ Widget is the base class of screen widgets and should not be instantiated by itself.

        :param tag_name: Text identifying the widget.
        :param screen_rect: The screen's rectangle where the widget is drawn on.
        :param x: The horizontal starting position of the widget's rectangle.
        :param y: The vertical starting position of the widget's rectangle.
        :param width: The width of the widget's rectangle.
        :param height: The height of the widget's rectangle.

    """
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        self.tag_name = tag_name
        self.screen = screen_rect
        self.x_pos = x
        self.y_pos = y
        self.width = width
        self.height = height
        self.rect = Rect(x, y, width, height)
        self.outline_visible = False
        self.outline_color = WHITE
        self.background_color = BLACK
        self.font = FONT
        self.font_color = FIFTIES_YELLOW
        self.font_height = self.font.size("Tg")[1]

    def on_click(self, x, y):
        """ The function called when a widget is clicked """
        return self.tag_name

    def set_font(self, font_name, font_size, font_color=FIFTIES_YELLOW):
        self.font = pygame.font.Font(font_name, font_size)
        self.font_color = font_color


class LabelText(Widget):
    """ LabelText is used to write text that needs to fit in a pre-defined rectangle.

        :param tag_name: Text identifying the label.
        :param screen_rect: The screen's rectangle where the label is drawn on.
        :param x: The horizontal starting position of the label's rectangle.
        :param y: The vertical starting position of the label's rectangle.
        :param width: The width of the label's rectangle.
        :param height: The height of the label's rectangle.
    """
    def __init__(self, tag_name, screen_rect, x, y, width, height, text=""):
        Widget.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.caption = text
        self.alignment_horizontal = HOR_LEFT
        self.alignment_vertical = VERT_MID
        self.indent_horizontal = 0
        self.indent_vertical = 0
        self.outline_show = False
        self.outline_color = FIFTIES_CHARCOAL
        self.transparent = False

    def set_alignment(self, horizontal, vertical, hor_indent=0, vert_indent=0):
        """ Sets the label's alignment within the defined rectangle, """
        self.alignment_horizontal = horizontal
        self.alignment_vertical = vertical
        self.indent_horizontal = hor_indent
        self.indent_vertical = vert_indent

    def draw(self, text=""):
        """ Draws the label.

            :param text: default = "", set's the label's text,

            :return: Text that couldn't be fitted inside the label's rectangle,
        """
        if text == "":
            self.caption = self.caption.decode('utf-8')
        else:
            self.caption = text.decode('utf-8')
        if not self.transparent:
            self.screen.fill(self.background_color, self.rect) # Background
        if self.outline_show:
            pygame.draw.rect(self.screen, self.outline_color, self.rect,1)
        pygame.display.update(self.rect)

        # Determine maximum width of line
        i = 1
        while self.font.size(self.caption[:i])[0] < self.rect.width and i < len(self.caption):
            i += 1
        caption_width = self.font.size(self.caption[:i])[0]
        caption_height = self.font.size(self.caption[:i])[1]

        # Horizontal alignment
        if self.alignment_horizontal == HOR_LEFT:
            x = self.rect.left + self.indent_horizontal
        elif self.alignment_horizontal == HOR_MID:
            x = self.rect.centerx + self.indent_horizontal - caption_width / 2
        elif self.alignment_horizontal == HOR_RIGHT:
            x = self.rect.right - self.indent_horizontal - caption_width
        # Vertical alignment
        if self.alignment_vertical == VERT_TOP:
            y = self.rect.top + self.indent_vertical
        elif self.alignment_vertical == VERT_MID:
            y = self.rect.centery + self.indent_vertical - caption_height / 2
        elif self.alignment_vertical == VERT_BOTTOM:
            y = self.rect.bottom - self.indent_vertical - caption_height

        image = FONT.render(self.caption[:i], True, self.font_color)
        self.screen.blit(image, (x, y))
        pygame.display.update(self.rect)

        return self.caption[i:]


class ButtonIcon(Widget):
    """ ButtonIcon class is a button that only displays an icon.

        :param tag_name: Text identifying the widget,
        :param screen_rect: The screen's rectangle where the button should be drawn,
        :param x: The horizontal position of the button,
        :param y: The vertical position of the button,

        :ivar caption: The button's caption,
        :ivar image_file: The button's icon image file name,
    """
    def __init__(self, tag_name, screen_rect, image, x, y):
        self.image_file = image
        self.__icon = pygame.image.load(self.image_file)
        Widget.__init__(self, tag_name, screen_rect, x, y, self.__icon.get_width(), self.__icon.get_height())
        self.caption = ""

    def draw(self):
        """ Draws the button """
        rect = self.screen.blit(self.__icon, (self.x_pos, self.y_pos))
        pygame.display.update(rect)

    def set_image_file(self, file_name):
        """ Sets the buttons icon.

            :param file_name: Points to the icon's file name.
        """
        self.image_file = file_name
        self.__icon = pygame.image.load(self.image_file)
        self.width = self.__icon.get_width()
        self.height = self.__icon.get_height()
        self.draw()


class ButtonText(LabelText):
    """ ButtonText class is a button with text that uses two images for button rendering.

        :param tag_name: Text identifying the widget,
        :param screen_rect: The screen's rectangle where the button should be drawn,
        :param x: The horizontal position of the button,
        :param y: The vertical position of the button,
        :param width: The label's rectangle width,
        :param text: default "", The label's caption,

        :ivar transparent: Whether the label's background is transparent, default = False,
        :ivar font_color: The text font color,
        :ivar alignment_horizontal: The button's text horizontal alignment, default = :py:const:HOR_MID.
        :ivar alignment_vertical: The button's text vertical alignment, default = :py:const:VERT_MID,
    """
    def __init__(self, tag_name, screen_rect, x, y, width, text=""):
        LabelText.__init__(self, tag_name, screen_rect, x, y, width, 32, text)
        self.__background_left = None
        self.__background_middle = None
        self.__background_right = None
        self.transparent = True
        self.font_color = BLACK
        self.alignment_vertical = VERT_MID
        self.alignment_horizontal = HOR_MID
        self.__initialize_background()

    def draw(self):
        """ Draws the button on the screen. """
        # Left
        rect_left = self.screen.blit(self.__background_left, (self.x_pos, self.y_pos))
        pygame.display.update(rect_left)
        # Middle
        x = self.x_pos + self.__background_left.get_width()
        rect_middle = self.screen.blit(self.__background_middle, (x, self.y_pos))
        pygame.display.update(rect_middle)
        # Right
        x += self.__background_middle.get_width()
        rect_right = self.screen.blit(self.__background_right, (x, self.y_pos))
        pygame.display.update(rect_right)
        # Text
        super(ButtonText,self).draw()

    def __initialize_background(self):
        """ Sets up the button's background. """
        # Left side
        background_left_file = RESOURCES + "button_bg_left_32.png"
        self.__background_left = pygame.image.load(background_left_file).convert()
        # Middle
        background_middle_file = RESOURCES + "button_bg_middle_32.png"
        self.__background_middle = pygame.image.load(background_middle_file).convert()
        width = self.width - (2 * self.__background_left.get_width())
        self.__background_middle = pygame.transform.scale(self.__background_middle, (width, self.height))
        # Right
        self.__background_right = pygame.transform.flip(self.__background_left, True, False)


class Switch(Widget):
    def __init__(self, tag_name, screen_rect, x, y):
        self.__icon_on = pygame.image.load(ICO_SWITCH_ON)
        self.__icon_off = pygame.image.load(ICO_SWITCH_OFF)
        self.width = self.__icon_on.get_width()
        self.height = self.__icon_on.get_height()
        Widget.__init__(self, tag_name, screen_rect, x, y, self.width, self.height)
        self.__is_on = False

    def set_on(self, boolean):
        self.__is_on = boolean
        self.draw()

    def get_on(self):
        return self.__is_on

    def on_click(self, x, y):
        self.screen.fill(self.background_color, self.rect)
        self.__is_on = not self.__is_on
        self.draw()
        return self.tag_name

    def draw(self):
        if self.__is_on:
            rect = self.screen.blit(self.__icon_on, (self.x_pos, self.y_pos))
        else:
            rect = self.screen.blit(self.__icon_off, (self.x_pos, self.y_pos))
        pygame.display.update(rect)


class ItemList(Widget):
    """ List of text items that can be clicked.

        :param tag_name: Text identifying the list.
        :param screen_rect: The screen's rectangle where the list is drawn on.
        :param x: The horizontal starting position of the list's rectangle.
        :param y: The vertical starting position of the list's rectangle.
        :param width: The width of the list's rectangle.
        :param height: The height of the list's rectangle.

        :ivar list: List containing items for ItemList.
        :ivar outline_visible: Indicates whether the outline of the list is visible, default = True.

        :ivar item_height: The height of one list item, default = 25.
        :ivar item_indent: The indent for the text of a list item, default = 2.
        :ivar item_alignment_horizontal: Horizontal alignment of an item's text, default = :py:const:HOR_LEFT.
        :ivar item_alignment_vertical: Vertical alignment of an item's text, default = :py:const:VERT_MID.
        :ivar item_outline_visible: Boolean for displaying the rectangle of an item, default = False.

        :ivar active_item_index: The index of the currently active list item. It differs from selected in that it is set by the program and not by the user, default = -1.
        :ivar item_active_color: The active list item for color, default = :py:const:BLUE.
        :ivar item_active_background_color: The active list item background color, default = :py:const:WHITE.
        :ivar item_selected: The index of the selected list item, default = -1.
        :ivar item_selected_color: The font color of a selected item, default = :py:const:BLUE.
        :ivar item_selected_background_color: The selected list item background color, default = :py:const:WHITE.


    """
    def __init__(self, tag_name, screen_rect, x, y, width, height):
        Widget.__init__(self, tag_name, screen_rect, x, y, width, height)
        self.list = []
        self.outline_visible = True

        self.item_height = 25
        self.item_indent = 2
        self.item_alignment_horizontal = HOR_LEFT
        self.item_alignment_vertical = VERT_MID
        self.item_outline_visible = False

        self.active_item_index = -1
        self.item_active_color = BLUE
        self.item_active_background_color = WHITE

        self.item_selected = -1
        self.item_selected_color = BLUE
        self.item_selected_background_color = WHITE

        self.__items_max = (self.height - 2 * self.item_indent) / self.item_height  # Maximum number
        self.items_start = 0  # Index of self.lift that is the first item displayed in the ItemList


    def set_item_alignment(self, horizontal, vertical):
        """ Sets the alignment of the text of an item within the item's rectangle """
        self.item_alignment_horizontal = horizontal
        self.item_alignment_vertical = vertical

    def draw(self):
        """ Draws the item list on screen """
        self.screen.fill(self.background_color, self.rect)
        if self.outline_visible:
            pygame.draw.rect(self.screen, self.outline_color, self.rect, 1)
        pygame.display.update(self.rect)
        # Do not draw items when there are none
        if self.list is None:
            return
        # Populate the ItemList with items
        item_nr = 0
        while item_nr + self.items_start < len(self.list) and item_nr < self.__items_max:
            item_text = self.list[item_nr + self.items_start]                           # Get item text from list
            item_x_pos = self.x_pos + self.item_indent                                  # x position of item
            item_width = self.width - 2 * self.item_indent                              # Maximum item width
            item_y_pos = self.y_pos + self.item_indent + (self.item_height * item_nr)   # y position of item
            list_item = LabelText("lbl_item_" + str(item_nr), self.screen, item_x_pos, item_y_pos, item_width, self.item_height, item_text) # Create label
            list_item.font_color = self.font_color
            list_item.outline_visible = self.item_outline_visible
            if item_nr + self.items_start == self.active_item_index:  # Give active item designated colour
                list_item.font_color = self.item_active_color
            list_item.set_alignment(self.item_alignment_horizontal, self.item_alignment_vertical)
            list_item.draw()  # Draw item on screen
            item_nr += 1

    def clicked_item(self, x_pos, y_pos):
        """ Determines which item, if any, was clicked.

            :param x_pos: The click's horizontal position
            :param y_pos: The click's vertical position

            :return: The index of the selected list item
        """
        x_pos = x_pos - self.x_pos
        y_pos = y_pos - self.y_pos
        if x_pos < 0 or x_pos > self.width or y_pos < 0:  # Check whether the click was outside the control
            return None
        if y_pos > self.height or self.items_start + (y_pos + 2) / self.item_height >= len(
                self.list):  # Check whether no item was clicked
            return None
        self.item_selected = (self.items_start + (y_pos + 2)/self.item_height)
        return self.item_selected

    def item_active_get(self):
        """ :return: active item text """
        return self.list[self.active_item_index]

    def item_selected_get(self):
        """ :return: selected item's text """
        return self.list[self.item_selected]

    def on_click(self, x_pos, y_pos):
        """ Relays click action to a list item.
        :param x_pos: The horizontal click position.
        :param y_pos: The vertical click position.

        :return: return the ListItem's tag_name.
        """
        self.__clicked_item(x_pos, y_pos)
        return self.tag_name

    def show_next_items(self):
        """ Shows next page of items. """
        if self.items_start + self.__items_max < len(self.list):
            self.items_start += self.__items_max
            self.draw()

    def show_prev_items(self):
        """ Shows previous page of items. """
        if self.items_start - self.__items_max >= 0:
            self.items_start -= self.__items_max
            self.draw()


class Screen(object):
    """ Basic screen used for displaying widgets. This type of screen should be used for the entire program.

        :param screen_rect: The screen's rectangle where the screen is drawn on

        :ivar components: Dictionary holding the screen's widgets with a tag_name as key and the widget as value
        :ivar color: The screen's background color, default = :py:const:BLACK
    """
    def __init__(self, screen_rect):
        self.screen = screen_rect
        self.components = {} # Interface dictionary
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
            value.draw()
        pygame.display.flip()

    def on_click(self, x, y):
        """ Determines which component was clicked and fires it's click function in turn.

            :param x: The horizontal click position.
            :param y: The vertical click position.

            :return: The tag_name of the clicked component.
        """
        for key, value in self.components.items():
            if isinstance(value, ButtonIcon) or isinstance(value, ButtonText) or isinstance(value, Switch):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    value.on_click(x, y)
                    return key
            if isinstance(value, ItemList):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <=y <= value.y_pos + value.height:
                    value.clicked_item(x, y)
                    return key

    def on_swipe(self, x, y, swipe_type):
        """ Relays swipe to ItemList components for next(up)/previous(down) swipes for ItemLists.

            :param x: The horizontal start position of the swipe move.
            :param y: The vertical start position of the swipe move.
            :param swipe_type: The type of swipe movement done.
        """
        for key, value in self.components.items():
            if isinstance(value, ItemList):
                if value.x_pos <= x <= value.x_pos + value.width and value.y_pos <= y <= value.y_pos + value.height:
                    if swipe_type == SWIPE_UP:
                        value.show_next_items()
                    if swipe_type == SWIPE_DOWN:
                        value.show_prev_items()


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
        self.event_loop() # Start the loop capturing user input
        return self.return_object

    def close(self):
        """ Closes event loop and returns the window's return object """
        self.close_screen = True
        return self.return_object

    def __draw_window(self):
        """ Draws window border and title """
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
        self.screen.blit(image, (title_rect.centerx-font_width /2, title_rect.centery-font_height/2))

    def __get_swipe_type(self):
        """ Determines the kind of gesture.

            :return: The type of gesture [:py:const:SWIPE_CLICK, :py:const:SWIPE_DOWN, :py:const:SWIPE_UP, :py:const:SWIPE_LEFT, :py:const:SWIPE_RIGHT]
        """
        x, y = pygame.mouse.get_rel()  # Register mouse movement since last call

        if abs(x) <= MIN_SWIPE:
            if abs(y) <= MIN_SWIPE:
                if abs(x) < MAX_CLICK and abs(y) < MAX_CLICK:
                    return SWIPE_CLICK      # Not a swipe but a tap (click)
                else:
                    return -1      # No idea what the user did
            elif y > MIN_SWIPE:    # Down swipe
                return SWIPE_DOWN
            elif y < -MIN_SWIPE:   # Up swipe
                return SWIPE_UP
        elif abs(y) <= MIN_SWIPE:
            if x > MIN_SWIPE:      # Left swipe
                return SWIPE_LEFT
            elif x < -MIN_SWIPE:   # Right swipe
                return SWIPE_RIGHT
        return SWIPE_CLICK		   # Tap

    def event_loop(self):
        """ The window's event loop """
        while not self.close_screen:
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:        # Gesture start
                    mouse_down_time = pygame.time.get_ticks()   # Start timer to detect long mouse clicks
                    mouse_down_pos = pygame.mouse.get_pos()     # Get click position (= start position for swipe)
                    pygame.mouse.get_rel()                      # Start tracking mouse movement

                if event.type == pygame.MOUSEBUTTONUP:      # Gesture end
                    swipe_type = self.__get_swipe_type()    # Determines the kind of gesture used

                    if swipe_type == SWIPE_CLICK:      # Fire click function
                        self.action(self.on_click(mouse_down_pos[0], mouse_down_pos[1]))

                    # Relay vertical swiping to active screen controls
                    if swipe_type == SWIPE_UP or swipe_type == SWIPE_DOWN:
                        self.on_swipe(mouse_down_pos[0], mouse_down_pos[1], swipe_type)

                # Possibility to close modal window with 'Esc' key
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.return_object = None
                    self.close_screen = True

    def action(self, tag_name):
        """ Virtual function for event-related execution. """
        pass


class Screens(object):
    """ Manages screens of type Screen.
        Handles screen switching, clicking and swiping and mpd status updating.

        :ivar screen_list: List containing all screen objects.
        :ivar current_index: Points to current screen in screen_list.
        :ivar mouse_down_pos: Mouse position on mouse down.
    """
    def __init__(self):
        self.screen_list = []   #
        self.current_index = 0
        self.mouse_down_pos = pygame.mouse.get_pos()  # Initialize mouse position

    def show(self):
        """ Show the current screen """
        self.screen_list[self.current_index].show()

    def add_screen(self, screen):
        """ Adds screen to list """
        self.screen_list.append(screen)

    def swipe_type_get(self):
        """ Determines the kind of gesture.

            :return: The type of swipe [:py:const:SWIPE_CLICK, :py:const:SWIPE_DOWN, :py:const:SWIPE_UP, :py:const:SWIPE_LEFT, :py:const:SWIPE_RIGHT]
        """
        x, y = pygame.mouse.get_rel()  # Register mouse movement since last call
        if abs(x) <= MIN_SWIPE:
            if abs(y) <= MIN_SWIPE:
                if abs(x) < MAX_CLICK and abs(y) < MAX_CLICK:
                    return SWIPE_CLICK  # Not a swipe but a tap (click)
                else:
                    return -1  # No idea what the user did
            elif y > MIN_SWIPE:  # Down swipe
                return SWIPE_DOWN
            elif y < -MIN_SWIPE:  # Up swipe
                return SWIPE_UP

        elif abs(y) <= MIN_SWIPE:
            if x > MIN_SWIPE:  # Left swipe
                return SWIPE_LEFT
            elif x < -MIN_SWIPE:  # Right swipe
                return SWIPE_RIGHT
        return SWIPE_CLICK  # Tap

    def process_mouse_event(self, event_type):
        """ Processes mouse events. """
        if event_type == pygame.MOUSEBUTTONDOWN:  # Gesture start
            mouse_down_time = pygame.time.get_ticks()  # Start timer to detect long mouse clicks
            self.mouse_down_pos = pygame.mouse.get_pos()  # Get click position (= start position for swipe)
            pygame.mouse.get_rel()  # Start tracking mouse movement
        elif event_type == pygame.MOUSEBUTTONUP:  # Gesture end
            swipe_type = self.swipe_type_get()  # Determines the kind of gesture used
            # Start mouse related event functions
            if swipe_type == SWIPE_CLICK:  # Fire click function
                x = self.mouse_down_pos[0]
                y = self.mouse_down_pos[1]
                ret_value = self.screen_list[self.current_index].on_click(x, y)  # Relay tap/click to active screen
                # If the screen requests a screen switch
                if ret_value >= 0 and ret_value < len(self.screen_list):
                    self.current_index = ret_value
                    self.show()
            # Switch screens with horizontal swiping
            if swipe_type == SWIPE_LEFT and self.current_index - 1 >= 0:
                self.current_index -= 1
                self.show()
            if swipe_type == SWIPE_RIGHT and self.current_index + 1 < len(self.screen_list):
                self.current_index += 1
                self.show()
            # Relay vertical swiping to active screen controls
            if swipe_type == SWIPE_UP or swipe_type == SWIPE_DOWN:
                x = self.mouse_down_pos[0]
                y = self.mouse_down_pos[1]
                self.screen_list[self.current_index].on_swipe(x, y, swipe_type)
