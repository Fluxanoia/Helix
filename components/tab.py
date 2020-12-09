import enum

import tkinter as tk

import numpy as np

from utils.theme import Theme
from utils.fonts import FontManager
from utils.maths import updateBounds

class TabMode(enum.Enum):
    NONE    = 0
    TWO_D   = 1
    THREE_D = 2

class Tab(tk.Button):

    __select_callback = None
    __draw_callback = None

    __plots = []

    __mode = TabMode.NONE
    __mode_selector = None

    def __init__(self, parent, select, draw):
        super().__init__(parent,
            text = "Tab",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

        self.__select_callback = select
        self.__draw_callback = draw

        self.__mode_selector = tk.Frame(width = 480, height = 240)
        Theme.getInstance().configureTabModeSelector(self.__mode_selector)

        sub_frame = tk.Frame(self.__mode_selector, width = 240)
        Theme.getInstance().configureTabModeSelector(sub_frame)
        button_2d = tk.Button(sub_frame, text = "2D", 
            command = lambda : self.switch_mode(TabMode.TWO_D))
        button_3d = tk.Button(sub_frame, text = "3D", 
            command = lambda : self.switch_mode(TabMode.THREE_D))
        Theme.getInstance().configureTabModeSelectorButton(button_2d)
        Theme.getInstance().configureTabModeSelectorButton(button_3d)
        FontManager.getInstance().configureText(button_2d)
        FontManager.getInstance().configureText(button_3d)
        button_2d.pack(side = tk.LEFT)
        button_3d.pack(side = tk.RIGHT)

        label_top = tk.Label(self.__mode_selector, 
            text = "Pick a plotting mode for this tab:")
        label_bottom = tk.Label(self.__mode_selector, 
            text = "You can't change it once you pick (yet)!")
        Theme.getInstance().configureTabModeSelectorLabel(label_top)
        Theme.getInstance().configureTabModeSelectorLabel(label_bottom)
        FontManager.getInstance().configureText(label_top)
        FontManager.getInstance().configureText(label_bottom)
        label_top.pack()
        sub_frame.pack(ipadx = 20, ipady = 20)
        label_bottom.pack()

        # ex = tk.Button(self, text = "x")
        # ex.pack(side = tk.LEFT, fill = tk.Y)

    def switch_mode(self, mode):
        self.__mode = mode
        self.__draw_callback()

    def set_plots(self, plots):
        self.__plots = plots

    def draw(self, a2d, a3d):
        output = { }

        asymps = []
        g_min = None
        g_max = None

        if self.__mode == TabMode.NONE:
            output["widget"] = self.__mode_selector

        if self.__mode == TabMode.TWO_D:
            for p in self.__plots:
                free_vars = p.getFreeVariables()
                if len(free_vars) == 1:
                    plot = p.getPlot2D(-5, 5, 101)
                    for i in range(len(plot["x"])):
                        a2d.plot(plot["x"][i], plot["y"][i])
                    asymps.append(plot["asymptotes"])
                    g_min, g_max = updateBounds(g_min, g_max, plot["min"])
                    g_min, g_max = updateBounds(g_min, g_max, plot["max"])
            asymp = list(set().union(*asymps))
            if len(asymp) > 0:
                a2d.vlines(asymp, g_min, g_max, 'r', 'dashed')
            output["axes"] = a2d

        if self.__mode == TabMode.THREE_D:
            for p in self.__plots:
                free_vars = p.getFreeVariables()
                if len(free_vars) == 2:
                    plot = p.getPlot3D(-5, 5, -5, 5, 31)
                    for i in range(len(plot["x"])):
                        a3d.scatter(plot["x"][i], plot["y"][i], plot["z"][i])
                    asymps.append(plot["asymptotes"])
                    g_min, g_max = updateBounds(g_min, g_max, plot["min"])
                    g_min, g_max = updateBounds(g_min, g_max, plot["max"])
            asymp = list(set().union(*asymps))
            for a in asymp:
                x = np.linspace(a[0], a[0], 2)
                y = np.linspace(a[1], a[1], 2)
                z = np.linspace(g_min, g_max, 2)
                a3d.plot3D(x, y, z, c = 'r', linestyle = 'dashed')
            output["axes"] = a3d

        return output

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
