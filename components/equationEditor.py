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
    __add_button_height = 0.05

    def __init__(self, parent, width):
        super().__init__(parent, self.__entryConfig)
        Theme.getInstance().configureEditor(self)
        Theme.getInstance().configureEditor(self.getCanvas())
        Theme.getInstance().configureEditor(self.getInnerFrame())

        self.place(relwidth = width,
            relheight = 1 - self.__add_button_height)

        self.__entry_button = tk.Button(parent,
            text = "+",
            command = self.__addEntry)
        Theme.getInstance().configureEditorButton(self.__entry_button)
        FontManager.getInstance().configureText(self.__entry_button)
        self.__entry_button.place(
            rely = 1 - self.__add_button_height,
            relwidth = width,
            relheight = self.__add_button_height)

    def __addEntry(self):
        self.__entries.append(Equation(
            self.getInnerFrame(),
            self.__entries.remove))
        self.__entries[-1].configure(width = self.__entry_width)


    def __entryConfig(self, width):
        self.__entry_width = width
        for e in self.__entries:
            e.configure(width = self.__entry_width)
