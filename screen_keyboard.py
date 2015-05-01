"""
=======================================================
**screen_keyboard.py**: On-screen keyboard
=======================================================
"""
__author__ = 'Mark Zwart'

from settings import *
from interface_widgets import *


""" Special button icons

    :ivar
"""
ICO_SHIFT = RESOURCES + "shift_48x32.png"
ICO_BACKSPACE = RESOURCES + "backspace_48x32.png"
ICO_ENTER = RESOURCES + "enter_48x32.png"
ICO_LETTERS = RESOURCES + "letters_48x32.png"
ICO_SYMBOLS = RESOURCES + "symbols_48x32.png"

class KeyboardBase(ScreenModal):
    """ The base class of a keyboard, should not be instantiated.

        :param screen_rect: The display's rectangle where the keyboard is drawn on.
        :param caption: The title displayed at the top of the screen.
        :param text: The text that will be edited with the keyboard, default = "".
    """
    def __init__(self, screen_rect, caption, text=""):
        ScreenModal.__init__(self, screen_rect, caption)
        self.text = text
        # Edit box
        edit_box = LabelText("lbl_edit_box", screen_rect, 5, 30, 310, 25, text)
        edit_box.background_color = WHITE
        edit_box.font_color = BLACK
        edit_box.set_alignment(HOR_LEFT, VERT_MID, 5)
        self.add_component(edit_box)

    def __add_row_buttons(self, list_symbols, x, y):
        """ Adds a list of symbol keys starting at x on y """
        button_width = 32
        for letter in list_symbols:
            btn_name = "btn_symbol_" + letter
            btn = ButtonText(btn_name, self.screen, x, y, button_width, letter)
            self.add_component(btn)
            x += button_width

    def set_text(self, text):
        """ Sets the edit box's text.

            :param text: Text that needs to be edited using the keyboard
        """
        self.text = text
        self.components["lbl_edit_box"].caption = text


class KeyboardLetters(KeyboardBase):
    """ Displays keyboard for letters.
    """
    def __init__(self, screen_rect, caption, text=""):
        KeyboardBase.__init__(self, screen_rect, caption, text)

        self.shift_state = False

        y_row = 65
        y_row_increment = 45
        first_row = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        self.__add_row_buttons(first_row, 0, y_row)
        second_row = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
        y_row += y_row_increment
        self.__add_row_buttons(second_row, 17, y_row)
        third_row = ["z", "x", "c", "v", "b", "n", "m"]
        y_row += y_row_increment
        self.__add_row_buttons(third_row, 49, y_row)
        self.add_component(ButtonIcon("btn_shift", screen_rect, ICO_SHIFT, 3, y_row))
        self.add_component(ButtonIcon("btn_backspace", screen_rect, ICO_BACKSPACE, 271, y_row))

        y_row += y_row_increment
        self.add_component(ButtonText("btn_symbol_comma", screen_rect, 50, y_row, 32, ","))
        self.add_component(ButtonText("btn_symbol_space", screen_rect, 82, y_row, 159, " "))
        self.add_component(ButtonText("btn_symbol_point", screen_rect, 241, y_row, 32, "."))
        self.add_component(ButtonIcon("btn_enter", screen_rect, ICO_ENTER, 271, y_row))
        self.add_component(ButtonIcon("btn_symbols", screen_rect, ICO_SYMBOLS, 4, y_row))

    def __letters_shift(self):
        """ Sets button values to lower- or uppercase depending on the shift state. """
        for key, value in self.components.items():
            if value.tag_name[:11] == "btn_symbol_":
                if not self.shift_state:
                    new_letter = value.caption.upper()
                else:
                    new_letter = value.caption.lower()
                value.caption = new_letter
        self.shift_state = not self.shift_state
        self.show()

    def on_click(self, x, y):
        tag_name = super(KeyboardLetters, self).on_click(x, y)

        if tag_name is None:
            return

        if tag_name == "btn_shift":
            self.__letters_shift()
        elif tag_name[:11] == "btn_symbol_":  # If keyboard symbol is pressed add it to the text
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            if self.shift_state:
                self.shift_state = False
        elif tag_name == "btn_backspace":  # Remove last character of the text
            current_value = self.components["lbl_edit_box"].caption
            self.components["lbl_edit_box"].caption = current_value[:len(current_value)-1]
            self.components["lbl_edit_box"].draw()
        self.text = self.components["lbl_edit_box"].caption
        self.return_object = self.components["lbl_edit_box"].caption

        if tag_name == "btn_symbols":
            self.return_object = "symbols"  # Switch to numbers/symbols keyboard
            self.close()
        elif tag_name == "btn_enter":
            self.return_object = "enter"  # Confirms current text value
            self.close()


class KeyboardSymbols(KeyboardBase):
    """ Displays keyboard for numbers and symbols.
    """
    def __init__(self, screen_rect, caption, text=""):
        KeyboardBase.__init__(self, screen_rect, caption, text)

        y_row = 65
        y_row_increment = 45
        first_row = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.__add_row_buttons(first_row, 0, y_row)

        y_row += y_row_increment
        second_row = ["-", "+", "=" "/",  "(", ")", "%","$", "#", "\""]
        self.__add_row_buttons(second_row, 0, y_row)

        y_row += y_row_increment
        third_row = [":", ";", ".", ",", "?", "!", "'", "*", "_"]
        self.__add_row_buttons(third_row, 0, y_row)
        self.add_component(ButtonIcon("btn_backspace", screen_rect, ICO_BACKSPACE, 271, y_row))

        y_row += y_row_increment
        self.add_component(ButtonIcon("btn_enter", screen_rect, ICO_ENTER, 271, y_row))
        self.add_component(ButtonIcon("btn_symbol_letters", screen_rect, ICO_LETTERS, 0, y_row))
        self.add_component(ButtonText("btn_symbol_ampersand", screen_rect, 50, y_row, 32, "&"))
        self.add_component(ButtonText("btn_symbol_space", screen_rect, 82, y_row, 159, " "))
        self.add_component(ButtonText("btn_symbol_at", screen_rect, 241, y_row, 32, "@"))

    def on_click(self, x, y):
        tag_name = super(KeyboardSymbols, self).on_click(x, y)

        if tag_name is None:
            return

        if tag_name[:11] == "btn_symbol_":  # If keyboard symbol is pressed add it to the text
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
        elif tag_name == "btn_backspace":  # Remove last character of the text
            current_value = self.components["lbl_edit_box"].caption
            self.components["lbl_edit_box"].caption = current_value[:len(current_value)-1]
            self.components["lbl_edit_box"].draw()
        self.return_object = self.components["lbl_edit_box"].caption
        self.text = self.components["lbl_edit_box"].caption  # Ensure text = to the edit box

        if tag_name == "btn_letters":
            self.return_object = "letters"  # Switch to letters keyboard
            self.close()
        if tag_name == "btn_enter":
            self.return_object = "enter"  # Confirms current text value
            self.close()


class Keyboard():
    """ Called keyboard class that displays a text edit field with a
        letter or symbol keyboard.

        :param screen_rect: The display's rectangle where the keyboard is drawn on.
        :param caption: The title displayed at the top of the screen.
        :param text: The text that will be edited with the keyboard, default = "".
    """
    def __init__(self, screen_rect, caption, text=""):
        self.text = text
        self.text_original = text
        self.selected = "letters"
        self.keyboard_letters = KeyboardLetters(screen_rect, caption, text)
        self.keyboard_symbols = KeyboardSymbols(screen_rect, caption, text)

    def show(self):
        """ Loops until enter, cancel or escape on the keyboard is pressed.

            :return: The text as it was edited when return was pressed, or the original text in case of a cancellation.
        """
        value = ""
        while value != "enter" and value != "cancel":
            # Switch between the different keyboards (letter or number/symbol)
            if self.selected == "letters":
                self.keyboard_letters.set_text(self.text)
                value = self.keyboard_letters.show()
                self.text = self.keyboard_letters.text
                if value == "symbols":
                    self.selected = value
                    self.show()
            elif self.selected == "symbols":
                self.keyboard_symbols.set_text(self.text)
                value = self.keyboard_symbols.show()
                self.text = self.keyboard_symbols.text
                if value == "letters":
                    self.selected = value
        if value == "enter":
            return self.text  # When the user pressed enter the entered text value is returned
        elif value == "cancel":
            return self.text_original  # When the user chose to cancel the original text value is returned

