import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

class Tab(tk.Button):

    def __init__(self, parent):
        super().__init__(parent, text = "Empty")
        Theme.getInstance().configureTabButton(self)
        FontManager.getInstance().configureText(self)
