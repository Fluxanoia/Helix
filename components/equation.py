import enum

import tkinter as tk

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.parsing import Parsed
from utils.delay import DelayTracker
from utils.theme import Theme
from utils.maths import PlotType

from components.tooltip import Tooltip

class EquationLabelType(enum.Enum):
    NONE = 0,
    VALUE = 1,
    ERROR = 2

class Equation(tk.Frame):

    TEXT_KEY = "text"
    COLOUR_KEY = "colour"
    LOCK_KEY = "locked"
    HIDE_KEY = "hidden"
    CONTOUR_KEY = "contoured"

    __counter = 0

    def __init__(self, parent, update_fun, remove_func, settings = None):
        super().__init__(parent)

        if settings is None: settings = {}

        self.__update_fun = update_fun
        self.__remove_func = remove_func

        self.__debounce_id = None
        self.__debounce_delay = 500

        self.div = None

        self.__plottable = False
        self.__parsed = Parsed("")

        self.__min_height = 28
        self.__button_size = 24
        self.__button_count = 0
        self.__frame_pad = 8
        self.__spacing = 8

        theme = Theme.get_instance()

        self.__inner = tk.Frame(self, bg = theme.get_editor_body_colour(),
            padx = self.__frame_pad, pady = self.__frame_pad)
        self.__inner.pack(anchor = tk.CENTER, fill = tk.BOTH, expand = True)

        self.__entry_var = tk.StringVar()
        self.__entry_var.set(settings.get(Equation.TEXT_KEY, ""))
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self.__inner, textvariable = self.__entry_var)
        FontManager.get_instance().configure_text(self.__entry)
        self.__entry.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            relwidth = 1)

        self.__content_wrapper = tk.Frame(self.__inner,
            bg = theme.get_editor_body_colour())

        self.__readout_active = False
        self.__readout_height = 32
        self.__readout_type = EquationLabelType.NONE
        self.__readout = tk.Label(self.__content_wrapper,
            bg = theme.get_editor_body_colour(),
            image = ImageManager.get_instance().get_image(
                "info.png",
                self.__readout_height,
                self.__readout_height))
        self.__readout_tooltip = Tooltip(self.__readout)

        self.__content_wrapper.place(x = self.__button_size + self.__spacing,
            y = self.__min_height + self.__spacing,
            w = -(self.__button_size + self.__spacing), h = -(self.__min_height + self.__spacing),
            relwidth = 1, relheight = 1)

        self.__colour_window_open = False
        self.__colour_window_active = True
        self.__locked = False
        self.__hidden = False
        self.__contoured = False

        self.__construct_colour(settings)
        self.__construct_lock(settings)
        self.__construct_hide(settings)
        self.__construct_contour(settings)
        self.__construct_remove()
        self.__place_buttons()

        self.pack(fill = tk.BOTH, expand = True)

    def __construct_colour(self, settings):
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
            bg = theme.get_editor_body_colour(),
            padx = 10, pady = 10,
            highlightthickness = 3,
            highlightcolor = theme.get_editor_divider_colour())
        self.__colour_window.bind('<Enter>', enter)
        self.__colour_window.bind('<Leave>', leave)
        leave(None)

        def update(_v):
            self.__colour_button.configure(image = ImageManager.get_instance().get_colour(
                self.__red.get(), self.__green.get(), self.__blue.get(),
                self.__button_size,
                self.__button_size))

        args = {
            "from_" : 0,
            "to" : 255,
            "command" : update,
            "orient" : tk.HORIZONTAL,
            "bg" : theme.get_editor_body_colour(),
            "length" : 120
            }
        title = tk.Label(self.__colour_window,
            text = "Paint Selection")
        theme.configure_editor_scale(title)
        title.pack()
        self.__red = tk.Scale(self.__colour_window, args)
        theme.configure_editor_scale(self.__red)
        self.__red.pack()
        self.__green = tk.Scale(self.__colour_window, args)
        theme.configure_editor_scale(self.__green)
        self.__green.pack()
        self.__blue = tk.Scale(self.__colour_window, args)
        theme.configure_editor_scale(self.__blue)
        self.__blue.pack()

        colours = theme.get_plot_colours()
        colour = settings.get(Equation.COLOUR_KEY, None)
        if colour is None:
            colour = colours[Equation.__counter]
            Equation.__counter += 1
            Equation.__counter %= len(colours)
        else:
            colour = list(map(int, colour.split(" ")))
        self.__red.set(colour[0])
        self.__green.set(colour[1])
        self.__blue.set(colour[2])

        def button_func():
            if not self.__colour_window_open:
                self.__colour_window.place(relx = 0.2)
                self.__colour_window.focus_set()
                self.__colour_window_open = True

        self.__colour_button = self.__create_button(button_func, "colour.png")
        update(None)
    def __construct_lock(self, settings):
        def lock():
            self.__entry.config(state = tk.NORMAL if self.__locked else tk.DISABLED)
            self.__locked = not self.__locked
            self.__lock_button.config(relief = tk.SUNKEN if self.__locked else tk.RAISED)
        self.__lock_button = self.__create_button(lock, "lock.png")
        if bool(settings.get(Equation.LOCK_KEY, False)): lock()
    def __construct_hide(self, settings):
        def hide():
            self.__hidden = not self.__hidden
            self.__update()
            self.__hide_button.config(relief = tk.SUNKEN if self.__hidden else tk.RAISED)
        self.__hide_button = self.__create_button(hide, "hide.png")
        if bool(settings.get(Equation.HIDE_KEY, False)): hide()
    def __construct_contour(self, settings):
        def contour():
            self.__contoured = not self.__contoured
            self.__update()
            self.__contour_button.config(relief = tk.SUNKEN if self.__contoured else tk.RAISED)
        self.__contour_button = self.__create_button(contour, "contour.png")
        if bool(settings.get(Equation.CONTOUR_KEY, False)): contour()
    def __construct_remove(self):
        def remove(self):
            self.pack_forget()
            self.__remove_func(self)
        self.__remove_button = self.__create_button(lambda s = self : remove(s), "remove.png")
    def __create_button(self, command, img_path):
        return tk.Button(self.__inner,
            command = command,
            image = ImageManager.get_instance().get_image(
                img_path,
                self.__button_size,
                self.__button_size))

    def get_settings(self):
        settings = {}
        settings[Equation.TEXT_KEY] = self.get_text()
        settings[Equation.COLOUR_KEY] = str(self.__red.get()) + " " \
            + str(self.__green.get()) + " " + str(self.__blue.get())
        settings[Equation.LOCK_KEY] = int(self.__locked)
        settings[Equation.HIDE_KEY] = int(self.__hidden)
        settings[Equation.CONTOUR_KEY] = int(self.__contoured)
        return settings

    def __debounce_update(self, *_args):
        if self.__debounce_id is not None:
            DelayTracker.get_instance().end_delay(self, self.__debounce_id)
        self.__debounce_id = self.after(self.__debounce_delay, self.__update)
        DelayTracker.get_instance().add_delay(self, self.__debounce_id)
    def update(self):
        DelayTracker.get_instance().remove_delay(self, self.__debounce_id)
        self.__debounce_id = None
        self.__parsed = Parsed(self.get_text())
        self.__parsed.set_equation(self)
        self.__parsed.set_colour((self.__red.get() / 255.0,
            self.__green.get() / 255.0, self.__blue.get() / 255.0))
    def __update(self, *_args):
        self.update()
        self.__update_fun(self)
    def set_width(self, w):
        self.__inner.configure(width = w)

    def force_text(self, text):
        self.__entry.delete(0, tk.END)
        self.__entry.insert(0, text)
    def label(self, t, text):
        self.__readout_type = t
        self.__readout_tooltip.set_text(text)

    def __place_buttons(self):
        buttons = []
        if self.__plottable:
            buttons.append(self.__colour_button)
            buttons.append(self.__hide_button)
        else:
            self.__colour_button.place_forget()
            self.__hide_button.place_forget()
            if self.__colour_window_open:
                self.__colour_window_open = False
                self.__colour_window.place_forget()
        buttons.append(self.__lock_button)
        if self.__plottable and self.get_parsed().get_binding().get_plot_type() in \
            [PlotType.SURFACE, PlotType.PARAMETRIC_SURFACE]:
            buttons.append(self.__contour_button)
        else:
            self.__contour_button.place_forget()
        buttons.append(self.__remove_button)
        self.__button_count = len(buttons)
        for i in range(self.__button_count):
            buttons[i].place(y = (self.__button_size + self.__spacing) * i,
                w = self.__button_size, h = self.__button_size)
    def __place_content(self):
        if self.__readout_active:
            self.__readout.pack(fill = tk.BOTH, expand = True)
        else:
            self.__readout.pack_forget()
    def __set_height(self):
        buttons = (self.__button_size + self.__spacing) * self.__button_count - self.__spacing
        content = 0
        if self.__readout_active: content += self.__readout_height
        h = max(self.__min_height + self.__spacing + content, buttons)
        self.__inner.configure(height = self.__frame_pad * 2 + h)
    def set_state(self, plottable):
        self.__plottable = plottable

        self.__readout_active = self.__readout_type is not EquationLabelType.NONE
        if self.__readout_active:
            path = ""
            if self.__readout_type is EquationLabelType.VALUE: path = "info"
            if self.__readout_type is EquationLabelType.ERROR: path = "error"
            self.__readout.configure(image = ImageManager.get_instance().get_image(
                    path + ".png",
                    self.__readout_height,
                    self.__readout_height))

        self.__place_buttons()
        self.__place_content()
        self.__set_height()

    def is_plottable(self):
        return self.__plottable
    def is_hidden(self):
        return self.__hidden
    def is_contoured(self):
        return self.__contoured
    def get_text(self):
        return self.__entry.get()
    def get_parsed(self):
        return self.__parsed
