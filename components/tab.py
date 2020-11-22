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
        if len(self.__plots) > 0:
            if self.__plots[0].getDimensionality() == 2:
                a2d.clear()
                a2d.set_visible(True)
                x = [ (i - 100) / 10 for i in range(201) ]
                a2d.plot(x, self.__plots[0].getPlot2D(x))
                return a2d
        return None

    # def __rotateAxis(self, _event):
    #     self.__axes.view_init(30, self.angle)
    #     self.angle += 10
    #     self.__update()
