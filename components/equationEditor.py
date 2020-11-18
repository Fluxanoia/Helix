import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager

from components.equation import Equation
from components.scrollableFrame import ScrollableFrame

class EquationEditor(ScrollableFrame):

    # Entries
    __entry_width = None
    __entry_button = None
    __entries = []

    # Placement
    __add_button_buffer = 0.05

    def __init__(self, parent, width):
        super().__init__(parent, 
            self.__entryConfig,
            borderwidth = 0,
            highlightthickness = 0)
        self.getCanvas().configure(bg = Theme.getInstance().getShade(2))
        self.getInnerFrame().configure(bg = Theme.getInstance().getShade(2))

        self.place(relwidth = width,
            relheight = 1 - self.__add_button_buffer)

        self.__entry_button = tk.Button(parent,
            text = "+",
            bg = Theme.getInstance().getShade(1),
            activebackground = Theme.getInstance().getShade(3),
            font = FontManager.getInstance().getTextFont(),
            command = self.__addEntry,
            borderwidth = 0,
            highlightthickness = 0)
        self.__entry_button.place(
            rely = 1 - self.__add_button_buffer,
            relwidth = width,
            relheight = self.__add_button_buffer)

    def __addEntry(self):
        self.__entries.append(Equation(
            self.getInnerFrame(),
            self.__entries.remove))
        self.__entries[-1].configure(width = self.__entry_width)


    def __entryConfig(self, width):
        self.__entry_width = width
        for e in self.__entries:
            e.configure(width = self.__entry_width)
