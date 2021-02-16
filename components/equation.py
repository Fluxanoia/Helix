import random

import tkinter as tk

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.parsing import Parsed
from utils.delay import DelayTracker
from utils.theme import Theme

class Equation(tk.Frame):

    # Callback
    __update_fun = None
    __remove_func = None

    # Main Widgets
    __inner = None
    __entry = None
    __readout = None
    __readout_wrapper = None
    div = None
    # Button Widgets
    __lock_button = None
    __hide_button = None
    __remove_button = None

    # Colour
    __colour_active = False
    __colour_button = None
    __colour_window = None
    __red = None
    __green = None
    __blue = None

    # Entry tracker
    __entry_var = None
    __debounce_id = None
    __debounce_delay = 500

    # Button Alignments
    __leftButtons = []
    __rightButtons = []
    # Placement
    __button_size = 24
    __button_count = 4

    __frame_pad = 8
    __spacing = 8

    # Parsing
    __parsed = None

    def __init__(self, parent, update_fun, remove_func):
        super().__init__(parent)

        self.__update_fun = update_fun
        self.__remove_func = remove_func

        self.__inner = tk.Frame(self, bg = Theme.getInstance().getEditorBody(),
            padx = self.__frame_pad, pady = self.__frame_pad,
            height = self.__button_size * self.__button_count \
                + self.__spacing * (self.__button_count - 1) + self.__frame_pad * 2 + 50)
        self.__inner.pack(anchor = tk.CENTER, fill = tk.BOTH, expand = True)

        self.__entry_var = tk.StringVar()
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self.__inner, textvariable = self.__entry_var)
        FontManager.getInstance().configureText(self.__entry)
        self.__entry.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            relwidth = 1)

        self.__readout_wrapper = tk.Frame(self.__inner)
        self.__readout = tk.Text(self.__readout_wrapper)
        FontManager.getInstance().configureText(self.__readout)
        Theme.getInstance().configureEditorReadout(self.__readout)
        self.__readout.config(state = tk.DISABLED)
        self.__readout.pack(fill = tk.BOTH, expand = True)
        self.__readout_wrapper.place(x = self.__button_size + self.__spacing,
            y = self.__spacing,
            w = -(self.__button_size + self.__spacing),
            h = -self.__spacing,
            rely = 0.2,
            relwidth = 1,
            relheight = 0.8)

        self.__construct_colour()
        self.__lock_button = self.__create_button(lambda : None, "lock.png")
        self.__hide_button = self.__create_button(lambda : None, "hide.png")
        self.__remove_button = self.__create_button(self.__remove, "remove.png")

        buttons = [self.__colour_button, self.__lock_button, \
            self.__hide_button, self.__remove_button]
        for i in range(len(buttons)):
            buttons[i].place(y = (self.__button_size + self.__spacing) * i,
                w = self.__button_size, h = self.__button_size)

        self.pack(fill = tk.BOTH, expand = True)

    def __construct_colour(self):
        theme = Theme.getInstance()

        self.__colour_window = tk.Frame(self.__inner,
            bg = theme.getEditorBody(),
            padx = 10, pady = 10,
            highlightthickness = 5,
            highlightcolor = theme.getEditorDivider())
        args = {
            "from_" : 0,
            "to" : 255,
            "command" : self.__colour_update,
            "orient" : tk.HORIZONTAL,
            "bg" : theme.getEditorBody(),
            "length" : 120
            }
        title = tk.Label(self.__colour_window,
            text = "Paint Selection")
        theme.configureEditorScale(title)
        title.pack()
        self.__red = tk.Scale(self.__colour_window, args)
        theme.configureEditorScale(self.__red)
        self.__red.pack()
        self.__green = tk.Scale(self.__colour_window, args)
        theme.configureEditorScale(self.__green)
        self.__green.pack()
        self.__blue = tk.Scale(self.__colour_window, args)
        theme.configureEditorScale(self.__blue)
        self.__blue.pack()

        self.__red.set(random.randint(0, 255))
        self.__green.set(random.randint(0, 255))
        self.__blue.set(random.randint(0, 255))

        def func(self):
            if self.__colour_active:
                self.__colour_window.place_forget()
                self.__update()
            else:
                self.__colour_window.place(relx = 0.2)
            self.__colour_active = not self.__colour_active

        self.__colour_button = self.__create_button(lambda s = self : func(s), "colour.png")
        self.__colour_button.configure(image = ImageManager.getInstance().getColour(
                self.__red.get(), self.__green.get(), self.__blue.get(),
                self.__button_size,
                self.__button_size))

    def __create_button(self, command, img_path):
        return tk.Button(self.__inner,
            command = command,
            image = ImageManager.getInstance().getImage(
                img_path,
                self.__button_size,
                self.__button_size))

    def config_width(self, w):
        self.__inner.configure(width = w)

    def __colour_update(self, _v):
        self.__colour_button.configure(image = ImageManager.getInstance().getColour(
                self.__red.get(), self.__green.get(), self.__blue.get(),
                self.__button_size,
                self.__button_size))

    def __debounce_update(self, *_args):
        if self.__debounce_id is not None:
            DelayTracker.getInstance().endDelay(self, self.__debounce_id)
        self.__debounce_id = self.after(self.__debounce_delay, self.__update)
        DelayTracker.getInstance().addDelay(self, self.__debounce_id)

    def force_text(self, text):
        self.__entry.delete(0, tk.END)
        self.__entry.insert(0, text)

    def __update(self, *_args):
        DelayTracker.getInstance().removeDelay(self, self.__debounce_id)
        self.__debounce_id = None
        self.__parsed = Parsed(self.get_text())
        self.__parsed.colour = (self.__red.get() / 255.0, self.__green.get() / 255.0,
            self.__blue.get() / 255.0)
        self.__update_fun()

    def __remove(self):
        self.pack_forget()
        self.__remove_func(self)

    def label(self, text):
        self.__readout.config(state = tk.NORMAL)
        self.__readout.delete(1.0, tk.END)
        self.__readout.insert(tk.END, text)
        self.__readout.config(state = tk.DISABLED)

    def get_text(self):
        return self.__entry.get()

    def get_parsed(self):
        return self.__parsed
