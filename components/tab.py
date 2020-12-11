import enum

import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

class TabMode(enum.Enum):
    NONE    = 0
    EMPTY   = 0
    TWO_D   = 1
    THREE_D = 2

class Tab(tk.Button):

    __mode = TabMode.NONE
    __mode_selector = None

    __draw_callback = None

    def __init__(self, parent, select, draw):
        super().__init__(parent,
            text = "Tab",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)
        self.__draw_callback = draw

    def switch_mode(self, mode):
        self.__mode = mode
        self.__draw_callback()

    def get_mode(self):
        return self.__mode
