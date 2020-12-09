import tkinter as tk

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes, Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.theme import Theme
from utils.images import ImageManager
from utils.fonts import FontManager

from components.tab import Tab

mpl.use('tkAgg')

class EquationViewer(tk.Frame):

    __bar_height = 0.05
    __width = None

    __figure = None
    __axes2d = None
    __axes3d = None
    __widget = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    __canvas = None

    def __init__(self, parent, width):
        super().__init__(parent)
        Theme.getInstance().configureViewer(self)

        self.__width = width

        self.__figure = plt.figure(0, clear = True)
        self.__axes2d = Axes(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer2D")
        self.__axes3d = Axes3D(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer3D")
        Theme.getInstance().configureFigure(self.__figure)
        Theme.getInstance().configurePlot2D(self.__axes2d)
        Theme.getInstance().configurePlot3D(self.__axes3d)

        self.__canvas = FigureCanvasTkAgg(self.__figure, master = self)
        self.__canvas.mpl_connect('button_press_event', self.__focus)
        self.__canvas.draw()
        self.__canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)

        self.__tab_bar = tk.Frame(self)
        Theme.getInstance().configureTabBar(self.__tab_bar)
        self.__tab_bar.place(relwidth = 1 - self.__bar_height,
            relheight = self.__bar_height)

        self.__tab_add_button = tk.Button(self,
            command = self.__addTab,
            image = ImageManager.getInstance().getImage(
                "plus.png", 32, 32))
        Theme.getInstance().configureTabButton(self.__tab_add_button)
        FontManager.getInstance().configureText(self.__tab_add_button)
        self.__tab_add_button.place(relx = 1 - self.__bar_height,
            relwidth = self.__bar_height,
            relheight = self.__bar_height)

        self.__addTab()
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
        self.__tabs.append(Tab(self.__tab_bar, self.__select, self.__draw))
        self.__tabs[-1].pack(side = tk.LEFT, fill = tk.Y)

    def __draw(self):
        self.__axes2d.clear()
        self.__axes3d.clear()
        self.__figure.clf()

        element = self.__selected_tab.draw(self.__axes2d, self.__axes3d)
        if ("axes" in element) and (not element["axes"] in self.__figure.get_axes()):
            if not self.__widget is None: self.__widget.place_forget()
            self.__figure.clf()
            self.__figure.add_axes(element["axes"])
        if ("widget" in element) and (not self.__widget == element["widget"]):
            if not self.__widget is None: self.__widget.place_forget()
            self.__widget = element["widget"]
            self.__widget.place(anchor = tk.CENTER,
                relx = self.__width + (1 - self.__width) / 2,
                rely = 0.5)

        if not self.__canvas is None: self.__canvas.draw()

    def __select(self, t):
        if self.__selected_tab is not None:
            self.__selected_tab.configure(relief = tk.RAISED)
        self.__selected_tab = t
        self.__selected_tab.configure(relief = tk.SUNKEN)
        self.__draw()

    def plot(self, plots):
        for tab in self.__tabs: tab.set_plots(plots)
        self.__draw()
