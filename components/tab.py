import tkinter as tk

import numpy as np

from utils.theme import Theme
from utils.fonts import FontManager

class Tab(tk.Button):

    def __init__(self, parent, select):
        super().__init__(parent,
            text = "Empty",
            command = lambda : select(self))
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)

    def draw(self, a2d, a3d):
        a2d.set_visible(True)
        # a3d.set_visible(True)
        x, y = np.meshgrid(np.linspace(-6, 6, 30), np.linspace(-6, 6, 30))
        z = np.cos(np.sqrt(x ** 2 + y ** 2))
        a2d.plot(x, z)
        a3d.plot_wireframe(x, y, z)
