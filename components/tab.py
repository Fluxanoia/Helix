import tkinter as tk

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

    def draw(self, a2d, _a3d):
        a2d.clear()
        a2d.set_visible(True)

        asymps = []
        g_ymin = None
        g_ymax = None
        for p in self.__plots:
            if p.getDimensionality() == 2:
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

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
