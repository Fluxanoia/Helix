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

    __view_rect = [-10, -10, 20, 20]

    __elev = 30
    __azim = -60
    __view_cuboid = [-10, -10, -10, 20, 20, 20]

    __drag_pos = None
    __drag_scale_3d = 20


    def __init__(self, parent, select):
        super().__init__(parent,
            text = "Tab",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)

    def drag(self, e, w, h):
        if not self.__mode in [TabMode.TWO_D, TabMode.THREE_D]: return
        if self.__mode == TabMode.TWO_D:
            self.__view_rect[0] += (self.__drag_pos[0] - e.x) \
                * (self.__view_rect[2] / w)
            self.__view_rect[1] += (e.y - self.__drag_pos[1]) \
                * (self.__view_rect[3] / h)
            self.__drag_pos = (e.x, e.y)
            return self.get_lims()
        if self.__mode == TabMode.THREE_D:
            self.__azim += (self.__drag_pos[0] - e.x) / (self.__drag_scale_3d / w)
            self.__elev += (e.y - self.__drag_pos[1]) / (self.__drag_scale_3d / h)
            self.__drag_pos = (e.x, e.y)
            return (self.get_elev(), self.get_azim())

    def zoom(self, e):
        if not self.__mode in [TabMode.TWO_D, TabMode.THREE_D]: return
        if self.__mode == TabMode.TWO_D:
            lw = max(self.__view_rect[2:4])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_rect[0] -= sd
            self.__view_rect[1] -= sd
            self.__view_rect[2] += 2 * sd
            self.__view_rect[3] += 2 * sd
        if self.__mode == TabMode.THREE_D:
            lw = max(self.__view_cuboid[3:6])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_cuboid[0] -= sd
            self.__view_cuboid[1] -= sd
            self.__view_cuboid[2] -= sd
            self.__view_cuboid[3] += 2 * sd
            self.__view_cuboid[4] += 2 * sd
            self.__view_cuboid[5] += 2 * sd
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

    def get_xmin_2d(self): return self.__view_rect[0]
    def get_xmax_2d(self): return self.__view_rect[0] + self.__view_rect[2]
    def get_ymin_2d(self): return self.__view_rect[1]
    def get_ymax_2d(self): return self.__view_rect[1] + self.__view_rect[3]

    def get_xmin_3d(self): return self.__view_cuboid[0]
    def get_xmax_3d(self): return self.__view_cuboid[0] + self.__view_cuboid[3]
    def get_ymin_3d(self): return self.__view_cuboid[1]
    def get_ymax_3d(self): return self.__view_cuboid[1] + self.__view_cuboid[4]
    def get_zmin_3d(self): return self.__view_cuboid[2]
    def get_zmax_3d(self): return self.__view_cuboid[2] + self.__view_cuboid[5]

    def get_lims(self):
        if not self.__mode in [TabMode.TWO_D, TabMode.THREE_D]: return None
        if self.__mode is TabMode.TWO_D:
            return ((self.get_xmin_2d(), self.get_xmax_2d()), \
                (self.get_ymin_2d(), self.get_ymax_2d()))
        if self.__mode is TabMode.THREE_D:
            return ((self.get_xmin_3d(), self.get_xmax_3d()), \
                (self.get_ymin_3d(), self.get_ymax_3d()), \
                (self.get_zmin_3d(), self.get_zmax_3d()))
