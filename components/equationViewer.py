import tkinter as tk

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes, Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.theme import Theme
from utils.fonts import FontManager

from components.tab import Tab

mpl.use('tkAgg')

class EquationViewer(tk.Frame):

    __bar_height = 30

    __figure = None
    __axes2d = None
    __axes3d = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    __canvas = None

    def __init__(self, parent, width):
        super().__init__(parent,
            borderwidth = 0,
            highlightthickness = 0)
        Theme.getInstance().configureViewer(self)

        self.__tab_bar = tk.Frame(self,
            height = self.__bar_height)
        Theme.getInstance().configureTabBar(self.__tab_bar)
        self.__tab_add_button = tk.Button(self.__tab_bar,
            text = "+",
            command = self.__addTab,
            width = 3)
        Theme.getInstance().configureTabButton(self.__tab_add_button)
        FontManager.getInstance().configureText(self.__tab_add_button)
        self.__tab_bar.pack(side = tk.TOP, fill = tk.X)
        self.__addTab()

        self.__figure = plt.figure(0, clear = True)
        self.__axes2d = Axes(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer2D")
        self.__axes3d = Axes3D(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer3D")
        Theme.getInstance().configureFigure(self.__figure)
        Theme.getInstance().configurePlot2D(self.__axes2d)
        Theme.getInstance().configurePlot3D(self.__axes3d)
        self.__figure.add_axes(self.__axes2d)
        self.__figure.add_axes(self.__axes3d)
        self.__canvas = FigureCanvasTkAgg(self.__figure,
            master = self)
        self.__canvas.mpl_connect('button_press_event', self.__focus)
        self.__canvas.draw()
        self.__canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

        self.__select(self.__tabs[0])

        # self.__canvas.mpl_connect("key_press_event", self.__rotateAxis)

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

        tab = Tab(self.__tab_bar, self.__select)

        self.__tabs.append(tab)
        for t in self.__tabs:
            t.pack(side = tk.LEFT, fill = tk.NONE)
        self.__tab_add_button.pack(side = tk.LEFT, fill = tk.Y)

    def __select(self, t):
        self.__axes2d.clear()
        self.__axes2d.set_visible(False)
        self.__axes3d.clear()
        self.__axes3d.set_visible(False)
        for tab in self.__tabs:
            if tab == t:
                tab.configure(relief = tk.SUNKEN)
            else:
                tab.configure(relief = tk.RAISED)
        t.draw(self.__axes2d, self.__axes3d)

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
