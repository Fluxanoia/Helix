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

    def __init__(self, parent, update_fun, remove_func):
        super().__init__(parent, bg = parent["bg"], height = 110)

        self.__update_fun = update_fun
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

        self.__colour_button = self.__create_button(lambda : None, "colour.png")
        self.__lock_button = self.__create_button(lambda : None, "lock.png")
        self.__hide_button = self.__create_button(lambda : None, "hide.png")
        self.__remove_button = self.__create_button(self.__remove, "remove.png")

        self.__leftButtons = [self.__colour_button, self.__lock_button, self.__hide_button]
        self.__rightButtons = [self.__remove_button]
        self.__place_buttons()

        self.pack(fill = tk.BOTH, expand = True)

    def __create_button(self, command, img_path):
        return tk.Button(self,
            command = command,
            image = ImageManager.getInstance().getImage(
                img_path,
                self.__button_size,
                self.__button_size))

    def __place_buttons(self):
        for i in range(len(self.__leftButtons)):
            self.__place_button_left(self.__leftButtons[i], i)
        for i in range(len(self.__rightButtons)):
            self.__place_button_right(self.__rightButtons[i], i)

    def __place_button_left(self, button, count):
        button.place(anchor = tk.SW,
            x = self.__button_size * count,
            relx = self.__paddingx * (count + 1),
            rely = 1 - self.__paddingy,
            w = self.__button_size,
            h = self.__button_size)

    def __place_button_right(self, button, count = 0):
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

    def force_text(self, text):
        self.__entry.delete(0, tk.END)
        self.__entry.insert(0, text)

    def __update(self, *_args):
        DelayTracker.getInstance().removeDelay(self, self.__debounce_id)
        self.__debounce_id = None

        self.__parsed = Parsed(self.get_text())
        if self.__parsed.has_error():
            self.label(self.__parsed.get_error())
        elif self.__parsed.has_binding():
            self.label(str(self.__parsed.get_binding()[0]) \
                + " = " + str(self.__parsed.get_binding()[1]))
        elif len(self.__parsed.get_free_symbols()) > 0:
            self.label("Unbound variables.")
        else:
            self.label(str(self.__parsed.get_value()))

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
