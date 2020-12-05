import tkinter as tk

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.parsing import Parsed
from utils.delay import DelayTracker

from components.plot import Plot

class Equation(tk.Frame):

    # Callback
    __add_func = None
    __remove_func = None

    # Main Widgets
    __entry = None
    __label = None
    # Button Widgets
    __colour_button = None
    __lock_button = None
    __hide_button = None
    __remove_button = None

    # Entry tracker
    __entry_var = None
    __debounce_id = None
    __debounce_delay = 250

    # Button Alignments
    __leftButtons = []
    __rightButtons = []
    # Placement
    __button_size = 32
    __paddingx = 0.02
    __paddingy = 0.04
    __bar_width = 0.1

    # Parsing
    __parsed = None
    __plot = None

    def __init__(self, parent, add_func, remove_func):
        super().__init__(parent, bg = parent["bg"], height = 110)

        self.__add_func = add_func
        self.__remove_func = remove_func

        self.__entry_var = tk.StringVar()
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self, textvariable = self.__entry_var)
        FontManager.getInstance().configureText(self.__entry)
        self.__entry.place(relx = self.__paddingx,
            rely = self.__paddingy,
            relwidth = 1 - self.__paddingx * 2)

        self.__label = tk.Label(self, text = "")
        FontManager.getInstance().configureText(self.__label)
        self.__label.place(relx = self.__paddingx,
            rely = self.__paddingy * 2 + 0.25,
            relwidth = 1 - self.__paddingx * 2)

        self.__colour_button = self.__createButton(lambda : None, "colour.png")
        self.__lock_button = self.__createButton(lambda : None, "lock.png")
        self.__hide_button = self.__createButton(lambda : None, "hide.png")
        self.__remove_button = self.__createButton(self.__remove, "remove.png")

        self.__leftButtons = [self.__colour_button, self.__lock_button, self.__hide_button]
        self.__rightButtons = [self.__remove_button]
        self.__placeButtons()

        self.pack(fill = tk.BOTH, expand = True)

    def __createButton(self, command, img_path):
        return tk.Button(self,
            command = command,
            image = ImageManager.getInstance().getImage(
                img_path,
                self.__button_size,
                self.__button_size))

    def __placeButtons(self):
        for i in range(len(self.__leftButtons)):
            self.__placeButtonLeft(self.__leftButtons[i], i)
        for i in range(len(self.__rightButtons)):
            self.__placeButtonRight(self.__rightButtons[i], i)

    def __placeButtonLeft(self, button, count):
        button.place(anchor = tk.SW,
            x = self.__button_size * count,
            relx = self.__paddingx * (count + 1),
            rely = 1 - self.__paddingy,
            w = self.__button_size,
            h = self.__button_size)

    def __placeButtonRight(self, button, count = 0):
        button.place(anchor = tk.SE,
            x = self.__button_size * count,
            relx = 1 - self.__paddingx * (count + 1),
            rely = 1 - self.__paddingy,
            w = self.__button_size,
            h = self.__button_size)

    def __debounce_update(self, *_args):
        if self.__debounce_id is not None:
            DelayTracker.getInstance().endDelay(self, self.__debounce_id)
        self.__debounce_id = self.after(self.__debounce_delay, self.__update)
        DelayTracker.getInstance().addDelay(self, self.__debounce_id)

    def __update(self, *_args):
        DelayTracker.getInstance().removeDelay(self, self.__debounce_id)
        self.__debounce_id = None

        self.__plot = None
        self.__parsed = Parsed(self.getText())
        blocks = self.__parsed.getBlocks()
        if self.__parsed.hasError():
            self.label(self.__parsed.getError())
        elif len(blocks) == 0:
            self.label("")
        elif len(blocks) == 1:
            free_vars = len(self.__parsed.getVariables())
            if free_vars == 0:
                self.label(self.__parsed.getValue())
            else:
                self.__plot = Plot(blocks[0], list(self.__parsed.getVariables()))
                self.label(str(self.__parsed.getVariables()))
                self.__add_func()
        elif len(blocks) == 2:
            self.label("...")

    def __remove(self):
        self.pack_forget()
        self.__remove_func(self)

    def label(self, text):
        self.__label.config(text = text)

    def getText(self):
        return self.__entry.get()

    def getPlot(self):
        return self.__plot
