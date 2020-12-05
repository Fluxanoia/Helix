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

    __free_vars = []
    __variable_info = {}
    __variable_selector = None

    __tab_bar = None
    __tabs = []
    __selected_tab = None
    __tab_add_button = None

    __canvas = None

    def __init__(self, parent, width):
        super().__init__(parent)
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

        self.__variable_selector = tk.Frame(self)
        Theme.getInstance().configureVariableSelector(self.__variable_selector)
        text = tk.Label(self.__variable_selector, text = "Variables")
        Theme.getInstance().configureVariableSelectorText(text)
        text.pack(padx = 5, pady = 5)
        self.__variable_selector.pack(side = tk.RIGHT, anchor = tk.NE, fill = tk.Y)

        self.__figure = plt.figure(0, clear = True)
        self.__axes2d = Axes(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer2D")
        self.__axes3d = Axes3D(self.__figure, (0.1, 0.1, 0.8, 0.8), label = "Viewer3D")
        Theme.getInstance().configureFigure(self.__figure)
        Theme.getInstance().configurePlot2D(self.__axes2d)
        Theme.getInstance().configurePlot3D(self.__axes3d)

        self.__select(self.__tabs[0])

        self.__canvas = FigureCanvasTkAgg(self.__figure, master = self)
        self.__canvas.mpl_connect('button_press_event', self.__focus)
        self.__canvas.draw()
        self.__canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = 1)

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

    def __draw(self):
        self.__axes2d.clear()
        self.__axes3d.clear()
        self.__figure.clf()
        ax = self.__selected_tab.draw(self.__axes2d, self.__axes3d)
        if not (ax is None or ax in self.__figure.get_axes()):
            self.__figure.clf()
            self.__figure.add_axes(ax)
        if not self.__canvas is None:
            self.__canvas.draw()

    def __select(self, t):
        self.__selected_tab = t
        for tab in self.__tabs:
            if tab == t:
                tab.configure(relief = tk.SUNKEN)
            else:
                tab.configure(relief = tk.RAISED)
        self.__draw()

    def __variable_check(self, var):
        if self.__variable_info[var][0].get():
            self.__selected_tab.addAxis(var)
        else:
            self.__selected_tab.removeAxis(var)
        self.__draw()

    def plot(self, plots):
        self.__free_vars = set()
        for p in plots:
            self.__free_vars = self.__free_vars.union(set(p.getFreeVariables()))
        self.__free_vars = list(self.__free_vars)
        self.__free_vars.sort(key = str)

        repack = False
        for free_var in self.__free_vars:
            exists = False
            for key in self.__variable_info:
                exists = free_var == key
                if exists: break
            if not exists:
                var = tk.BooleanVar()
                self.__variable_info[free_var] = (var,
                    tk.Checkbutton(self.__variable_selector,
                        text = str(free_var),
                        variable = var,
                        onvalue = True,
                        offvalue = False,
                        command =
                            lambda fv = free_var: self.__variable_check(fv)))
                Theme.getInstance().configureVariableSelectorCheckbox(
                    self.__variable_info[free_var][1])
                repack = True

        to_remove = [k for k in self.__variable_info
            if not k in self.__free_vars]
        for k in to_remove:
            self.__variable_info[k][1].pack_forget()
            self.__variable_info.pop(k)
            repack = True

        if repack:
            keys = list(self.__variable_info.keys())
            keys.sort(key = str)
            for k in self.__variable_info:
                self.__variable_info[k][1].pack_forget()
            for k in keys:
                self.__variable_info[k][1].pack(side = tk.TOP, anchor = tk.NW, fill = tk.X)

        for tab in self.__tabs:
            tab.plot(plots, self.__free_vars)

        self.__draw()
