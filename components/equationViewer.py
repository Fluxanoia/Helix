import tkinter as tk

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes, Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sympy.plotting.plot import Plot, plot, plot3d, unset_show
import sympy as sy

from utils.theme import Theme
from utils.images import ImageManager
from utils.fonts import FontManager

from components.tab import Tab, TabMode

mpl.use('tkAgg')

class EquationViewer(tk.Frame):

    __bar_height = 0.05
    __width = None

    __plot = None
    __figure = None

    __frame = None
    __widget = None
    __canvas = None
    __mode_selector = None
    __empty_message = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    def __init__(self, parent, width):
        super().__init__(parent)
        Theme.getInstance().configureViewer(self)

        self.__width = width

        self.__frame = tk.Frame(parent)
        Theme.getInstance().configureViewer(self.__frame)
        self.__frame.place(relx = self.__width,
            rely = self.__bar_height,
            relwidth = 1 - self.__width,
            relheight = 1 - self.__bar_height)

        self.__constructTabBar()
        self.__constructModeSelector()
        self.__constructEmptyMessage()

        self.place(relx = width,
            relwidth = 1 - width,
            relheight = 1)

        self.__draw()

    def __constructTabBar(self):
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

    def __constructModeSelector(self):
        self.__mode_selector = tk.Frame(self.__frame)
        Theme.getInstance().configureViewer(self.__mode_selector)

        sub_frame = tk.Frame(self.__mode_selector, width = 240)
        Theme.getInstance().configureViewer(sub_frame)
        button_2d = tk.Button(sub_frame, text = "2D",
            command = lambda : self.__selected_tab.switch_mode(TabMode.TWO_D))
        button_3d = tk.Button(sub_frame, text = "3D",
            command = lambda : self.__selected_tab.switch_mode(TabMode.THREE_D))
        Theme.getInstance().configureViewerButton(button_2d)
        Theme.getInstance().configureViewerButton(button_3d)
        FontManager.getInstance().configureText(button_2d)
        FontManager.getInstance().configureText(button_3d)
        button_2d.pack(side = tk.LEFT)
        button_3d.pack(side = tk.RIGHT)

        label_top = tk.Label(self.__mode_selector,
            text = "Pick a plotting mode for this tab:")
        label_bottom = tk.Label(self.__mode_selector,
            text = "You can't change it once you pick (yet)!")
        Theme.getInstance().configureViewerText(label_top)
        Theme.getInstance().configureViewerText(label_bottom)
        FontManager.getInstance().configureText(label_top)
        FontManager.getInstance().configureText(label_bottom)
        label_top.pack()
        sub_frame.pack(ipadx = 20, ipady = 20)
        label_bottom.pack()

    def __constructEmptyMessage(self):
        self.__empty_message = tk.Label(self.__frame,
            text = "Create an entry on the left to plot something!")
        Theme.getInstance().configureViewerText(self.__empty_message)
        FontManager.getInstance().configureText(self.__empty_message)

    def __addTab(self):
        self.__tabs.append(Tab(self.__tab_bar, self.__select, self.__draw))
        self.__tabs[-1].pack(side = tk.LEFT, fill = tk.Y)

    def __draw(self):
        mode = self.__selected_tab.get_mode()

        if mode == TabMode.NONE and not self.__widget == self.__mode_selector:
            if self.__widget is not None: self.__widget.pack_forget()
            self.__mode_selector.pack(fill = tk.BOTH, expand = True)
            self.__widget = self.__mode_selector
            return

        if mode == TabMode.EMPTY and not self.__widget == self.__empty_message:
            if self.__widget is not None: self.__widget.pack_forget()
            self.__empty_message.pack(fill = tk.BOTH, expand = True)
            self.__widget = self.__empty_message
            return

        if mode == TabMode.TWO_D or mode == TabMode.THREE_D:
            if self.__widget is not None: self.__widget.pack_forget()

            self.__plot = Plot(backend = 'matplotlib')

            if mode == TabMode.TWO_D:
                x = sy.symbols('x')
                self.__plot.extend(plot(x**2, show = False))
            elif mode == TabMode.THREE_D:
                x, y = sy.symbols('x y')
                self.__plot.extend(plot3d(x*y, (x, -5, 5), (y, -5, 5), show = False))

            self.__plot._backend = self.__plot.backend(self.__plot)
            self.__plot._backend.process_series()

            self.__figure = self.__plot._backend.fig
            Theme.getInstance().configureFigure(self.__figure)
            for a in self.__figure.axes:
                Theme.getInstance().configurePlot2D(a)

            self.__canvas = FigureCanvasTkAgg(self.__figure, master = self.__frame)
            self.__canvas.mpl_connect('button_press_event',
                lambda e : self.__canvas.get_tk_widget().focus_set())
            self.__canvas.draw()

            self.__widget = self.__canvas.get_tk_widget()
            self.__widget.pack(fill = tk.BOTH, expand = True)
            return

    def __select(self, t):
        if self.__selected_tab is not None:
            self.__selected_tab.configure(relief = tk.RAISED)
        self.__selected_tab = t
        self.__selected_tab.configure(relief = tk.SUNKEN)
        self.__draw()

    def plot(self, plots):
        for tab in self.__tabs: tab.set_plots(plots)
        self.__draw()
