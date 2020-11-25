import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

class Tab(tk.Button):

    __plots = []

    def __init__(self, parent, select):
        super().__init__(parent,
            text = "Empty",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

    def plot(self, plots):
        self.__plots = plots

    def draw(self, a2d, _a3d):
        a2d.clear()
        a2d.set_visible(True)
        for p in self.__plots:
            if p.getDimensionality() == 2:
                plot = p.getPlot2D([ (i - 50) / 10 for i in range(101) ])
                for i in range(len(plot[0])):
                    a2d.plot(plot[0][i], plot[1][i])
                if len(plot[3]) > 0:
                    a2d.vlines(plot[3], plot[4], plot[5], 'r', 'dashed')
        return a2d

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
