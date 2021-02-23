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

    # Entry
    __entry = None
    __entry_var = None
    __debounce_id = None
    __debounce_delay = 500

    # Readout
    __readout = None
    __readout_wrapper = None

    # Colour
    __colour_window_open = False
    __colour_button = None
    __colour_window = None
    __colour_window_active = True
    __red = None
    __green = None
    __blue = None

    # Locking
    __locked = False
    __lock_button = None

    # Hiding
    __hidden = False
    __hide_button = None

    # Removing
    __remove_button = None

    # Placement
    __inner = None
    __button_size = 24
    __frame_pad = 8
    __spacing = 8
    div = None

    # Parsing
    __plottable = False
    __parsed = None

    def __init__(self, parent, update_fun, remove_func):
        super().__init__(parent)

        self.__update_fun = update_fun
        self.__remove_func = remove_func

        self.__inner = tk.Frame(self, bg = Theme.get_instance().getEditorBody(),
            padx = self.__frame_pad, pady = self.__frame_pad,
            height = self.__frame_pad * 2 + 170)
        self.__inner.pack(anchor = tk.CENTER, fill = tk.BOTH, expand = True)

        self.__entry_var = tk.StringVar()
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self.__inner, textvariable = self.__entry_var)
        FontManager.get_instance().configureText(self.__entry)
        self.__entry.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            relwidth = 1)

        self.__readout_wrapper = tk.Frame(self.__inner)
        self.__readout = tk.Text(self.__readout_wrapper)
        FontManager.get_instance().configureText(self.__readout)
        Theme.get_instance().configureEditorReadout(self.__readout)
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
        self.__construct_lock()
        self.__construct_hide()
        self.__construct_remove()
        self.__place_buttons()

        self.pack(fill = tk.BOTH, expand = True)

    def __construct_colour(self):
        theme = Theme.get_instance()

        def __close_colour_window():
            self.__colour_window_open = False
            self.__colour_window.place_forget()
            self.__update()

        def close_func(_e):
            if self.__colour_window_open: __close_colour_window()

        def enter(_e):
            self.__colour_window.unbind_all("<ButtonPress-1>")

        def leave(_e):
            self.__colour_window.bind_all("<ButtonPress-1>", close_func)

        self.__colour_window = tk.Frame(self.__inner,
            bg = theme.getEditorBody(),
            padx = 10, pady = 10,
            highlightthickness = 3,
            highlightcolor = theme.getEditorDivider())
        self.__colour_window.bind('<Enter>', enter)
        self.__colour_window.bind('<Leave>', leave)
        leave(None)

        def update(_v):
            self.__colour_button.configure(image = ImageManager.get_instance().getColour(
                self.__red.get(), self.__green.get(), self.__blue.get(),
                self.__button_size,
                self.__button_size))

        args = {
            "from_" : 0,
            "to" : 255,
            "command" : update,
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

        def button_func():
            if not self.__colour_window_open:
                self.__colour_window.place(relx = 0.2)
                self.__colour_window.focus_set()
                self.__colour_window_open = True

        self.__colour_button = self.__create_button(button_func, "colour.png")
        self.__colour_button.configure(image = ImageManager.get_instance().getColour(
                self.__red.get(), self.__green.get(), self.__blue.get(),
                self.__button_size,
                self.__button_size))
    def __construct_lock(self):
        def lock():
            self.__entry.config(state = tk.NORMAL if self.__locked else tk.DISABLED)
            self.__locked = not self.__locked
            self.__lock_button.config(relief = tk.SUNKEN if self.__locked else tk.RAISED)

        self.__lock_button = self.__create_button(lock, "lock.png")
    def __construct_hide(self):
        def hide():
            self.__hidden = not self.__hidden
            self.__update()
            self.__hide_button.config(relief = tk.SUNKEN if self.__hidden else tk.RAISED)

        self.__hide_button = self.__create_button(hide, "hide.png")
    def __construct_remove(self):
        def remove(self):
            self.pack_forget()
            self.__remove_func(self)

        self.__remove_button = self.__create_button(lambda s = self : remove(s), "remove.png")
    def __create_button(self, command, img_path):
        return tk.Button(self.__inner,
            command = command,
            image = ImageManager.get_instance().getImage(
                img_path,
                self.__button_size,
                self.__button_size))

    def __place_buttons(self):
        buttons = []
        if self.__plottable:
            buttons.append(self.__colour_button)
            buttons.append(self.__hide_button)
        elif self.__colour_window_open:
            self.__colour_window_open = False
            self.__colour_window.place_forget()
        buttons.extend([self.__lock_button, self.__remove_button])
        for i in range(len(buttons)):
            buttons[i].place(y = (self.__button_size + self.__spacing) * i,
                w = self.__button_size, h = self.__button_size)
    def __debounce_update(self, *_args):
        if self.__debounce_id is not None:
            DelayTracker.get_instance().endDelay(self, self.__debounce_id)
        self.__debounce_id = self.after(self.__debounce_delay, self.__update)
        DelayTracker.get_instance().addDelay(self, self.__debounce_id)
    def __update(self, *_args):
        DelayTracker.get_instance().removeDelay(self, self.__debounce_id)
        self.__debounce_id = None
        self.__parsed = Parsed(self.get_text())
        self.__parsed.set_equation(self)
        self.__parsed.set_colour((self.__red.get() / 255.0,
            self.__green.get() / 255.0, self.__blue.get() / 255.0))
        self.__update_fun()
    def set_width(self, w):
        self.__inner.configure(width = w)

    def force_text(self, text):
        self.__entry.delete(0, tk.END)
        self.__entry.insert(0, text)
    def label(self, text):
        self.__readout.config(state = tk.NORMAL)
        self.__readout.delete(1.0, tk.END)
        self.__readout.insert(tk.END, text)
        self.__readout.config(state = tk.DISABLED)

    def set_plottable(self, b):
        self.__plottable = b
        self.__place_buttons()
    def is_plottable(self):
        return self.__plottable
    def is_hidden(self):
        return self.__hidden
    def get_text(self):
        return self.__entry.get()
    def get_parsed(self):
        return self.__parsed
