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
    __view_rect = [-10, -10, 20, 20]

    __drag_pos = None
    __drag_scale_2d = 3
    __drag_scale_3d = 20

    __draw = None

    def __init__(self, parent, select):
        super().__init__(parent,
            text = "Tab",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)

    def drag(self, e):
        if not self.__mode in [TabMode.TWO_D, TabMode.THREE_D]: return
        if self.__mode == TabMode.TWO_D:
            self.__view_rect[0] += (self.__drag_pos[0] - e.x) \
                / (self.__view_rect[2] * self.__drag_scale_2d)
            self.__view_rect[1] += (e.y - self.__drag_pos[1]) \
                / (self.__view_rect[3] * self.__drag_scale_2d)
        if self.__mode == TabMode.THREE_D:
            self.__azim += (self.__drag_pos[0] - e.x) / self.__drag_scale_3d
            self.__elev += (e.y - self.__drag_pos[1]) / self.__drag_scale_3d
        self.__drag_pos = (e.x, e.y)
        return self.get_lims()

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

        self.__plots = list(map(lambda p : p.get_blocks()[0],
            filter(lambda p : p.has_dim() and p.get_dim() == self.__mode.value,
            plots)))

    def get_plots(self):
        return self.__plots

    def get_elev(self):
        return self.__elev

    def get_azim(self):
        return self.__azim

    def get_xmin(self): return self.__view_rect[0]
    def get_xmax(self): return self.__view_rect[0] + self.__view_rect[2]
    def get_ymin(self): return self.__view_rect[1]
    def get_ymax(self): return self.__view_rect[1] + self.__view_rect[3]
    def get_lims(self):
        return ((self.get_xmin(), self.get_xmax()), (self.get_ymin(), self.get_ymax()))
