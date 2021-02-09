import tkinter as tk

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.parsing import Parsed
from utils.delay import DelayTracker

class Equation(tk.Frame):

    # Callback
    __update_fun = None
    __remove_func = None

    # Main Widgets
    __entry = None
    __label = None
    __inner = None
    div = None
    # Button Widgets
    __colour_button = None
    __lock_button = None
    __hide_button = None
    __remove_button = None

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

        self.__inner = tk.Frame(self, bg = parent["bg"],
            padx = self.__frame_pad, pady = self.__frame_pad,
            height = self.__button_size * self.__button_count \
                + self.__spacing * (self.__button_count - 1) + self.__frame_pad * 2)
        self.__inner.pack(anchor = tk.CENTER, fill = tk.BOTH, expand = True)

        self.__entry_var = tk.StringVar()
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self.__inner, textvariable = self.__entry_var)
        FontManager.getInstance().configureText(self.__entry)
        self.__entry.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            relwidth = 1)

        self.__label = tk.Label(self.__inner, text = "")
        FontManager.getInstance().configureText(self.__label)
        self.__label.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            y = self.__spacing,
            rely = 0.25,
            relwidth = 1)

        self.__colour_button = self.__create_button(lambda : None, "colour.png")
        self.__lock_button = self.__create_button(lambda : None, "lock.png")
        self.__hide_button = self.__create_button(lambda : None, "hide.png")
        self.__remove_button = self.__create_button(self.__remove, "remove.png")

        buttons = [self.__colour_button, self.__lock_button, \
            self.__hide_button, self.__remove_button]
        for i in range(len(buttons)):
            buttons[i].place(y = (self.__button_size + self.__spacing) * i,
                w = self.__button_size, h = self.__button_size)

        self.pack(fill = tk.BOTH, expand = True)

    def __create_button(self, command, img_path):
        return tk.Button(self.__inner,
            command = command,
            image = ImageManager.getInstance().getImage(
                img_path,
                self.__button_size,
                self.__button_size))

    def config_width(self, w):
        self.__inner.configure(width = w)

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
        self.__update_fun()

    def __remove(self):
        self.pack_forget()
        self.__remove_func(self)

    def label(self, text):
        self.__label.config(text = text)

    def get_text(self):
        return self.__entry.get()

    def get_parsed(self):
        return self.__parsed
