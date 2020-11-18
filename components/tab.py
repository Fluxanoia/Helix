import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

class Tab(tk.Button):

    def __init__(self, parent):
        super().__init__(parent,
            text = "Empty",
            bg = Theme.getInstance().getShade(1),
            activebackground = Theme.getInstance().getShade(3),
            font = FontManager.getInstance().getTextFont())
