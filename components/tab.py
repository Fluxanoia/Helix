import enum

import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

class TabMode(enum.Enum):
    NONE    = 0
    EMPTY   = 1
    TWO_D   = 2
    THREE_D = 3

class Tab(tk.Button):

    __mode = TabMode.NONE
    __mode_selector = None

    __plots = []

    __elev = 30
    __azim = -60
    __drag_pos = None
    __drag_scale = 20

    __draw = None

    def __init__(self, parent, select, draw):
        super().__init__(parent,
            text = "Tab",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

        self.__draw = draw

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)

    def drag(self, e):
        self.__azim += (self.__drag_pos[0] - e.x) / self.__drag_scale
        self.__elev += (e.y - self.__drag_pos[1]) / self.__drag_scale
        self.__drag_pos = (e.x, e.y)
        self.__draw()

    def switch_mode(self, mode):
        self.__mode = mode

    def get_mode(self):
        if not self.__mode == TabMode.NONE \
            and len(self.__plots) == 0:
            return TabMode.EMPTY
        return self.__mode

    def set_plots(self, plots):
        if not self.__mode in [TabMode.TWO_D, TabMode.THREE_D]:
            self.__plots = []
            return

        valid_plots = []
        for p in plots:
            if len(p.get_blocks()) == 1 and \
                len(p.get_variables()) + 1 == self.__mode.value:
                valid_plots.append(p.get_blocks()[0])
        self.__plots = valid_plots

    def get_plots(self):
        return self.__plots

    def get_elev(self):
        return self.__elev

    def get_azim(self):
        return self.__azim
