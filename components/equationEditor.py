from tkinter import Button

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

    def __init__(self, parent, width, **args):
        super().__init__(parent, self.__entryConfig, **args)

        self.place(relwidth = width, 
            relheight = 1 - self.__add_button_buffer)

        self.__entry_button = Button(parent,
            text = "+",
            font = FontManager.getInstance().getTextFont(),
            command = self.__addEntry)
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
