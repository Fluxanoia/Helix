import tkinter as tk

import numpy as np

from utils.theme import Theme
from utils.fonts import FontManager
from utils.maths import updateBounds

class Tab(tk.Button):

    __plots = []

    __axes = []

    def __init__(self, parent, select):
        super().__init__(parent,
            text = "Empty",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

    def plot(self, plots, free_vars):
        self.__plots = plots
        for i in range(len(self.__axes)):
            if not self.__axes[i] in free_vars:
                self.__axes.pop(i)

    def addAxis(self, x):
        self.__axes.append(x)

    def removeAxis(self, x):
        self.__axes.remove(x)

    def draw(self, a2d, a3d):
        len_axes = len(self.__axes)
        if len_axes == 1:
            asymps = []
            g_ymin = None
            g_ymax = None
            for p in self.__plots:
                free_vars = p.getFreeVariables()
                if (len(free_vars) == 1) and (self.__axes[0] in free_vars):
                    xs, ys, asymp, ymin, ymax = p.getPlot2D(-5, 5, 101)
                    for i in range(len(xs)):
                        a2d.plot(xs[i], ys[i])
                    asymps.append(asymp)
                    g_ymin, g_ymax = updateBounds(g_ymin, g_ymax, ymin)
                    g_ymin, g_ymax = updateBounds(g_ymin, g_ymax, ymax)
            asymp = list(set().union(*asymps))
            if len(asymp) > 0:
                a2d.vlines(asymp, g_ymin, g_ymax, 'r', 'dashed')
            return a2d
        elif len_axes == 2:
            asymps = []
            g_zmin = None
            g_zmax = None
            for p in self.__plots:
                free_vars = p.getFreeVariables()
                if (len(free_vars) == 2) \
                    and (self.__axes[0] in free_vars) \
                    and (self.__axes[1] in free_vars):
                    xs, ys, zs, asymp, zmin, zmax = p.getPlot3D(-5, 5, -5, 5, 11)
                    for i in range(len(xs)):
                        a3d.scatter(xs[i], ys[i], zs[i])
                    asymps.append(asymp)
                    g_zmin, g_zmax = updateBounds(g_zmin, g_zmax, zmin)
                    g_zmin, g_zmax = updateBounds(g_zmin, g_zmax, zmax)
            asymp = list(set().union(*asymps))
            for a in asymp:
                x = np.linspace(a[0], a[0], 2)
                y = np.linspace(a[1], a[1], 2)
                z = np.linspace(g_zmin, g_zmax, 2)
                a3d.plot3D(x, y, z, c = 'r', linestyle = 'dashed')
            return a3d
        else:
            pass
        return None

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
