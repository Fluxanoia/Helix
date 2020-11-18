import tkinter as tk

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from utils.theme import Theme
from utils.fonts import FontManager

from components.tab import Tab

mpl.use('tkAgg')

class EquationViewer(tk.Frame):

    __bar_height = 30

    __figure = None
    __axes = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    __canvas = None
    __toolbar = None

    def __init__(self, parent, width):
        super().__init__(parent,
            borderwidth = 0,
            highlightthickness = 0)
        self.bg = Theme.getInstance().getShade(0)

        self.__tab_bar = tk.Frame(self,
            bg = Theme.getInstance().getShade(1),
            height = self.__bar_height,
            borderwidth = 0,
            highlightthickness = 0)
        self.__tab_add_button = tk.Button(self.__tab_bar,
            text = "+",
            bg = Theme.getInstance().getShade(1),
            activebackground = Theme.getInstance().getShade(3),
            font = FontManager.getInstance().getTextFont(),
            command = self.__addTab,
            width = 3)
        self.__tab_bar.pack(side = tk.TOP, fill = tk.X)
        self.__addTab()
        # self.__select()

        self.__figure = plt.figure()
        self.__axes = Axes3D(self.__figure)

        self.__figure.patch.set_facecolor(self.bg)
        self.__axes.set_facecolor(self.bg)

        self.angle = 0
        x, y = np.meshgrid(np.linspace(-6, 6, 30), np.linspace(-6, 6, 30))
        z = np.cos(np.sqrt(x ** 2 + y ** 2))
        # self.__axes.plot_wireframe(x, y, z)

        self.__canvas = FigureCanvasTkAgg(self.__figure,
            master = self)
        self.__canvas.draw()
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self, pack_toolbar = False)
        self.__toolbar.update()

        self.__canvas.mpl_connect("key_press_event", self.__rotateAxis)
        self.__canvas.mpl_connect('button_press_event', self.__focus)

        self.__toolbar.pack(side = tk.BOTTOM, fill = tk.X)
        self.__canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

        self.place(relx = width,
            relwidth = 1 - width,
            relheight = 1)

    def __focus(self, _event):
        self.__canvas.get_tk_widget().focus_set()

    def __update(self):
        plt.draw()

    def __addTab(self):
        for t in self.__tabs:
            t.pack_forget()
        self.__tab_add_button.pack_forget()

        tab = Tab(self.__tab_bar)

        self.__tabs.append(tab)
        for t in self.__tabs:
            t.pack(side = tk.LEFT, fill = tk.NONE)
        self.__tab_add_button.pack(side = tk.LEFT, fill = tk.Y)

    def __rotateAxis(self, _event):
        self.__axes.view_init(30, self.angle)
        self.angle += 10
        self.__update()
