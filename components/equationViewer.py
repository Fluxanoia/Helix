import tkinter as tk
from utils.parsing import Dimension

from utils.theme import Theme
from utils.images import ImageManager
from utils.fonts import FontManager
from utils.plotting import HelixPlot

from components.tab import Tab, TabMode

class EquationViewer(tk.Frame):

    __bar_height = 0.05
    __width = None

    __frame = None
    __widget = None
    __mode_selector = None
    __empty_message = None
    __plot = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    def __init__(self, parent, width):
        super().__init__(parent)
        Theme.getInstance().configureViewer(self)

        self.__width = width

        self.__constructViewFrame(parent)
        self.__constructTabBar()
        self.__constructModeSelector()
        self.__constructEmptyMessage()

        self.place(relx = width, relwidth = 1 - width, relheight = 1)

        self.__draw()

    def __constructViewFrame(self, parent):
        self.__frame = tk.Frame(parent)
        Theme.getInstance().configureViewer(self.__frame)
        self.__frame.place(relx = self.__width,
            rely = self.__bar_height,
            relwidth = 1 - self.__width,
            relheight = 1 - self.__bar_height)
        self.__plot = HelixPlot(self.__frame,
            lambda e : self.__selected_tab.drag_start(e),
            lambda e, w, h : self.__selected_tab.drag(e, w, h),
            lambda e : self.__selected_tab.zoom(e))

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
        self.__modeSwitcher(TabMode.TWO_D)

    def __modeSwitcher(self, mode):
        self.__selected_tab.switch_mode(mode)
        self.__draw()

    def __constructModeSelector(self):
        self.__mode_selector = tk.Frame(self.__frame)
        Theme.getInstance().configureViewer(self.__mode_selector)

        sub_frame = tk.Frame(self.__mode_selector, width = 240)
        Theme.getInstance().configureViewer(sub_frame)
        button_2d = tk.Button(sub_frame, text = "2D",
            command = lambda : self.__modeSwitcher(TabMode.TWO_D))
        button_3d = tk.Button(sub_frame, text = "3D",
            command = lambda : self.__modeSwitcher(TabMode.THREE_D))
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
        self.__tabs.append(Tab(self.__tab_bar, self.__select))
        self.__tabs[-1].pack(side = tk.LEFT, fill = tk.Y)

    def __select(self, t):
        if self.__selected_tab is not None:
            self.__selected_tab.configure(relief = tk.RAISED)
        self.__selected_tab = t
        self.__selected_tab.configure(relief = tk.SUNKEN)
        self.__draw()

    def __draw(self):
        mode = self.__selected_tab.get_mode()

        none = mode == TabMode.NONE and not self.__widget == self.__mode_selector
        empty = mode == TabMode.EMPTY and not self.__widget == self.__empty_message
        plot2d = mode == TabMode.TWO_D
        plot3d = mode == TabMode.THREE_D

        if any([none, empty, plot2d, plot3d]) and self.__widget is not None:
            self.__widget.pack_forget()

        if none: self.__widget = self.__mode_selector
        if empty: self.__widget = self.__empty_message
        if plot2d:
            self.__plot.set_dim(Dimension.TWO_D)
            self.__plot.remove_plots()
            self.__plot.add_plots_2d(self.__selected_tab.get_plots())
            self.__plot.redraw()
        if plot3d:
            self.__plot.set_dim(Dimension.THREE_D)
            self.__plot.remove_plots()
            self.__plot.add_plots_3d(self.__selected_tab.get_plots())
            self.__plot.redraw()
        if plot2d or plot3d: self.__widget = self.__plot.widget()

        if any([none, empty, plot2d, plot3d]):
            self.__widget.pack(fill = tk.BOTH, expand = True)

    def plot(self, plots):
        for tab in self.__tabs: tab.set_plots(plots)
        self.__draw()
