from settings import *
from interface_widgets import *
__author__ = 'mark'

# Special button icons
ICO_SHIFT = "shift_48x32.png"
ICO_BACKSPACE = "backspace_48x32.png"
ICO_ENTER = "enter_48x32.png"
ICO_LETTERS = "letters_48x32.png"
ICO_SYMBOLS = "symbols_48x32.png"

class KeyboardBase(ScreenModal):
    def __init__(self, screen_rect, caption, text=""):
        ScreenModal.__init__(self, screen_rect, caption)
        self.text = text

        # Edit box
        edit_box = LabelText("lbl_edit_box", screen_rect, 5, 30, 310, 25, text)
        edit_box.background_color = WHITE
        edit_box.font_color = BLACK
        edit_box.set_alignment(HOR_LEFT, VERT_MID, 5)
        self.add_component(edit_box)

    def add_row_buttons(self, list_symbols, x, y):
        button_width = 32
        for letter in list_symbols:
            btn_name = "btn_symbol_" + letter
            btn = ButtonText(btn_name, self.screen, x, y, button_width, letter)
            self.add_component(btn)
            x += button_width

    def set_text(self, text):
        self.text = text
        self.components["lbl_edit_box"].caption = text


class KeyboardLetters(KeyboardBase):
    def __init__(self, screen_rect, caption, text=""):
        KeyboardBase.__init__(self, screen_rect, caption, text)

        self.shift_state = False

        y_row = 65
        y_row_increment = 45
        first_row = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        self.add_row_buttons(first_row, 0, y_row)
        second_row = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
        y_row += y_row_increment
        self.add_row_buttons(second_row, 17, y_row)
        third_row = ["z", "x", "c", "v", "b", "n", "m"]
        y_row += y_row_increment
        self.add_row_buttons(third_row, 49, y_row)
        self.add_component(ButtonIcon("btn_shift", screen_rect, ICO_SHIFT, 3, y_row))
        self.add_component(ButtonIcon("btn_backspace", screen_rect, ICO_BACKSPACE, 271, y_row))

        y_row += y_row_increment
        self.add_component(ButtonText("btn_comma", screen_rect, 50, y_row, 32,","))
        self.add_component(ButtonText("btn_space", screen_rect, 82, y_row, 159, " "))
        self.add_component(ButtonText("btn_point", screen_rect, 241, y_row, 32, "."))
        self.add_component(ButtonIcon("btn_enter", screen_rect, ICO_ENTER, 271, y_row))
        self.add_component(ButtonIcon("btn_symbols", screen_rect, ICO_SYMBOLS, 4, y_row))

    def on_click(self, x, y):
        tag_name = super(KeyboardLetters, self).on_click(x, y)

        if tag_name is None:
            return

        if tag_name == "btn_shift":
            for key, value in self.components.items():
                if value.tag_name[:11] == "btn_symbol_":
                    if not self.shift_state:
                        new_letter = value.caption.upper()
                    else:
                        new_letter = value.caption.lower()
                    value.caption = new_letter
            self.shift_state = not self.shift_state
            self.show()
        elif tag_name[:11] == "btn_symbol_":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.text = self.components["lbl_edit_box"].caption
            if self.shift_state:
                self.shift_state = False
        elif tag_name == "btn_comma" or tag_name == "btn_point" or tag_name == "btn_space":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.text = self.components["lbl_edit_box"].caption
        elif tag_name == "btn_backspace":
            current_value = self.components["lbl_edit_box"].caption
            self.components["lbl_edit_box"].caption = current_value[:len(current_value)-1]
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        self.text = self.components["lbl_edit_box"].caption

        if tag_name == "btn_symbols":
            self.return_object = "symbols"
            self.close()
        elif tag_name == "btn_enter":
            self.return_object = "enter"
            self.close()


class KeyboardSymbols(KeyboardBase):
    def __init__(self, screen_rect, caption, text=""):
        KeyboardBase.__init__(self, screen_rect, caption, text)

        y_row = 65
        y_row_increment = 45
        first_row = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
        self.add_row_buttons(first_row, 0, y_row)

        y_row += y_row_increment
        second_row = ["-", "+", "=" "/",  "(", ")", "%","$", "#", "\""]
        self.add_row_buttons(second_row, 0, y_row)

        y_row += y_row_increment
        third_row = [":", ";", ".", ",", "?", "!", "'", "*", "_"]
        self.add_row_buttons(third_row, 0, y_row)
        self.add_component(ButtonIcon("btn_backspace", screen_rect, ICO_BACKSPACE, 271, y_row))

        y_row += y_row_increment
        self.add_component(ButtonIcon("btn_enter", screen_rect, ICO_ENTER, 271, y_row))
        self.add_component(ButtonIcon("btn_letters", screen_rect, ICO_LETTERS, 0, y_row))
        self.add_component(ButtonText("btn_ampersand", screen_rect, 50, y_row, 32,"&"))
        self.add_component(ButtonText("btn_space", screen_rect, 82, y_row, 159, " "))
        self.add_component(ButtonText("btn_at", screen_rect, 241, y_row, 32,"@"))

    def on_click(self, x, y):
        tag_name = super(KeyboardSymbols, self).on_click(x, y)

        if tag_name is None:
            return

        if tag_name[:11] == "btn_symbol_":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        elif tag_name == "btn_space":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        elif tag_name == "btn_backspace":
            current_value = self.components["lbl_edit_box"].caption
            self.components["lbl_edit_box"].caption = current_value[:len(current_value)-1]
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        self.text = self.components["lbl_edit_box"].caption

        if tag_name == "btn_letters":
            self.return_object = "letters"
            self.close()
        if tag_name == "btn_enter":
            self.return_object = "enter"
            self.close()


class Keyboard():
    def __init__(self, screen_rect, caption, text=""):
        self.text = text
        self.text_original = text
        self.selected = "letters"
        self.keyboard_letters = KeyboardLetters(screen_rect, caption, text)
        self.keyboard_symbols = KeyboardSymbols(screen_rect, caption, text)

    def show(self):
        value = ""
        while value != "enter" and value != "cancel":
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
            return self.text
        elif value == "cancel":
            return self.text_original

    def on_click(self, x, y):
        tag_name = super(Keyboard, self).on_click(x, y)
        if tag_name[:11] == "btn_symbol_":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        elif tag_name == "btn_space":
            self.components["lbl_edit_box"].caption += self.components[tag_name].caption
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        elif tag_name == "btn_backspace":
            current_value = self.components["lbl_edit_box"].caption
            self.components["lbl_edit_box"].caption = current_value[:len(current_value)-1]
            self.components["lbl_edit_box"].draw()
            self.return_object = self.components["lbl_edit_box"].caption
        elif self.selected == "symbols":
            self.keyboard_symbols.on_click(x, y)

