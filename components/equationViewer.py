from tkinter import Frame, TOP, BOTH

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

mpl.use('tkAgg')

class EquationViewer(Frame):

    __figure = None
    __axes = None

    __canvas = None
    __toolbar = None

    def __init__(self, parent, width, **args):
        super().__init__(parent, args)

        self.__figure = plt.figure()
        self.__axes = Axes3D(self.__figure)

        self.__figure.patch.set_facecolor(self['bg'])
        self.__axes.set_facecolor(self['bg'])

        self.angle = 0
        x, y = np.meshgrid(np.linspace(-6, 6, 30), np.linspace(-6, 6, 30))
        z = np.cos(np.sqrt(x ** 2 + y ** 2))
        #self.__axes.plot_wireframe(x, y, z)

        self.__canvas = FigureCanvasTkAgg(self.__figure,
            master = self)
        self.__canvas.draw()
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self, pack_toolbar = False)
        self.__toolbar.update()

        self.__canvas.mpl_connect("key_press_event", self.__rotateAxis)
        self.__canvas.mpl_connect('button_press_event', self.__focus)

        # self.__toolbar.pack(side = BOTTOM, fill = X)
        self.__canvas.get_tk_widget().pack(side = TOP, fill = BOTH, expand = 1)

        self.place(relx = width,
            relwidth = 1 - width,
            relheight = 1)

    def __focus(self, _event):
        self.__canvas.get_tk_widget().focus_set()

    def __update(self):
        plt.draw()

    def __rotateAxis(self, _event):
        self.__axes.view_init(30, self.angle)
        self.angle += 10
        self.__update()
