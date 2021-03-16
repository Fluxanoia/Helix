import enum

import tkinter as tk

from utils.images import ImageManager
from utils.parsing import Parser, Parsed
from utils.delay import DelayTracker
from utils.theme import Theme
from utils.maths import PlotType

from components.tooltip import Tooltip

class EquationLabelType(enum.Enum):
    NONE = 0,
    VALUE = 1,
    ERROR = 2

class EquationValue(tk.Frame):

    HEIGHT = 38

    def __init__(self, parent, command):
        theme = Theme.get_instance()
        super().__init__(parent, bg = theme.get_body_colour(), height = EquationValue.HEIGHT)

        self.__symbol = Parser.T

        self.__label = tk.Label(self, text = str(self.__symbol))
        self.__to = tk.Label(self, text = "to")
        theme.configure_label(self.__label)
        theme.configure_label(self.__to)

        self.__entry_var_l = tk.StringVar()
        self.__entry_var_r = tk.StringVar()
        self.__entry_var_l.set("-1")
        self.__entry_var_r.set("1")
        self.__entry_var_l.trace('w', command)
        self.__entry_var_r.trace('w', command)
        self.__entry_l = tk.Entry(self, textvariable = self.__entry_var_l)
        self.__entry_r = tk.Entry(self, textvariable = self.__entry_var_r)
        theme.configure_entry(self.__entry_l)
        theme.configure_entry(self.__entry_r)

        self.__label.place(relx = 0, relwidth = 0.15)
        self.__entry_l.place(relx = 0.15, relwidth = 0.35)
        self.__to.place(relx = 0.5, relwidth = 0.15)
        self.__entry_r.place(relx = 0.65, relwidth = 0.35)

    def set_data(self, name, lb, ub):
        self.__symbol = name
        self.__label.configure(text = str(name))
        self.__entry_var_l.set(str(lb))
        self.__entry_var_r.set(str(ub))

    def get_symbol(self):
        return self.__symbol
    def get_dict(self):
        l = self.__entry_var_l.get()
        r = self.__entry_var_r.get()
        l, r = Parser.get_instance().parse_number((l, r))
        if any(map(lambda n : n is None, [l, r])):
            return None
        else:
            l = float(l)
            r = float(r)
            if l > r: l, r = r, l
            return { self.__symbol : (l, r) }

class Equation(tk.Frame):

    TEXT_KEY = "text"
    COLOUR_KEY = "colour"
    LOCK_KEY = "locked"
    HIDE_KEY = "hidden"
    CONTOUR_KEY = "contoured"

    __counter = 0

    def __init__(self, parent, update_func, replot_func, remove_func, settings = None):
        super().__init__(parent)

        if settings is None: settings = {}

        self.__update_func = update_func
        self.__replot_func = replot_func
        self.__remove_func = remove_func

        self.__debounce_update_id = None
        self.__debounce_replot_id = None
        self.__debounce_delay = 500

        self.div = None

        self.__plottable = False
        self.__cancel_plot = False
        self.__parsed = Parsed("")

        self.__min_height = 38
        self.__button_size = 24
        self.__button_count = 0
        self.__frame_pad = 8
        self.__spacing = 8

        theme = Theme.get_instance()

        self.__inner = tk.Frame(self, bg = theme.get_body_colour(),
            padx = self.__frame_pad, pady = self.__frame_pad)
        self.__inner.pack(anchor = tk.CENTER, fill = tk.BOTH, expand = True)

        self.__entry_var = tk.StringVar()
        self.__entry_var.set(settings.get(Equation.TEXT_KEY, ""))
        self.__entry_var.trace('w', self.__debounce_update)
        self.__entry = tk.Entry(self.__inner, textvariable = self.__entry_var)
        theme.configure_entry(self.__entry)
        self.__entry.place(x = self.__button_size + self.__spacing,
            w = -(self.__button_size + self.__spacing),
            relwidth = 1)

        self.__content_wrapper = tk.Frame(self.__inner,
            bg = theme.get_body_colour())

        self.__readout_active = False
        self.__readout_height = 32 + 2 * self.__spacing
        self.__readout_type = EquationLabelType.NONE
        self.__readout = tk.Label(self.__content_wrapper,
            bg = theme.get_body_colour(),
            image = ImageManager.get_instance().get_image(
                "info.png",
                self.__readout_height,
                self.__readout_height))
        self.__readout_tooltip = Tooltip(self.__readout)

        self.__value_1 = EquationValue(self.__content_wrapper, self.__debounce_replot)
        self.__value_2 = EquationValue(self.__content_wrapper, self.__debounce_replot)
        self.__values = (self.__value_1, self.__value_2)
        self.__value_count = 0
        self.__value_height = EquationValue.HEIGHT
        self.__parametric_limits = {}

        self.__content_wrapper.place(x = self.__button_size + self.__spacing,
            y = self.__min_height + self.__spacing,
            w = -(self.__button_size + self.__spacing), h = -(self.__min_height + self.__spacing),
            relwidth = 1, relheight = 1)

        self.__colour_window_open = False
        self.__colour_window_active = True
        self.__locked = False
        self.__hidden = False
        self.__contoured = False

        self.__r = self.__red = None
        self.__g = self.__green = None
        self.__b = self.__blue = None
        self.__colour_frame = None
        self.__colour_window = None

        self.__construct_colour(settings)
        self.__construct_lock(settings)
        self.__construct_hide(settings)
        self.__construct_contour(settings)
        self.__construct_remove()
        self.__place_buttons()

        self.pack(fill = tk.BOTH, expand = True)

    def __construct_colour(self, settings):
        theme = Theme.get_instance()

        def create_colour_frame():
            self.__colour_frame = tk.Frame(self.__colour_window)
            theme.configure_colour_window(self.__colour_frame)

            args = {
                "from_" : 0,
                "to" : 255,
                "command" : self.__colour_update,
                "orient" : tk.HORIZONTAL,
                "bg" : theme.get_body_colour(),
                "length" : 120
            }
            title = tk.Label(self.__colour_window, text = "Paint Selection")
            theme.configure_scale(title)
            title.pack()
            self.__red = tk.Scale(self.__colour_window, args)
            self.__green = tk.Scale(self.__colour_window, args)
            self.__blue = tk.Scale(self.__colour_window, args)
            for w in [self.__red, self.__green, self.__blue]:
                theme.configure_scale(w)
                w.pack()
            self.__red.set(self.__r)
            self.__green.set(self.__g)
            self.__blue.set(self.__b)

            self.__colour_frame.pack(fill = tk.BOTH, expand = True)

        def open_window(_e = None):
            if not self.__colour_window_open:
                self.__colour_window_open = True

                def enter(_e = None):
                    self.__colour_window.unbind_all("<ButtonPress-1>")
                def leave(_e = None):
                    self.__colour_window.bind_all("<ButtonPress-1>", self.__close_colour_window)

                x, y, _, _ = self.bbox()
                x += self.winfo_rootx() + 50
                y += self.winfo_rooty() + 50
                self.__colour_window = tk.Toplevel(self,
                    padx = 10, pady = 10, highlightthickness = 3)
                theme.configure_colour_window(self.__colour_window)
                self.__colour_window.wm_overrideredirect(1)
                self.__colour_window.wm_geometry("+%d+%d" % (x, y))
                self.__colour_window.bind('<Enter>', enter)
                self.__colour_window.bind('<Leave>', leave)
                create_colour_frame()
                leave()
                try:
                    self.__colour_window.tk.call("::tk::unsupported::MacWindowStyle",
                        "style", self.__colour_window._w, "help", "noActivates")
                except tk.TclError:
                    pass

        colours = theme.get_plot_colours()
        colour = settings.get(Equation.COLOUR_KEY, None)
        if colour is None:
            colour = colours[Equation.__counter]
            Equation.__counter += 1
            Equation.__counter %= len(colours)
        else:
            colour = tuple(map(int, colour.split(" ")))
        self.__r, self.__g, self.__b = colour

        self.__colour_button = self.__create_button(open_window, None)
        self.__colour_update()
    def __construct_lock(self, settings):
        on, off = ("lock", "unlock")
        def lock():
            self.__entry.config(state = tk.NORMAL if self.__locked else tk.DISABLED)
            self.__locked = not self.__locked
            self.__lock_button.config(
                image = self.__get_button_image(on if self.__locked else off),
                relief = tk.SUNKEN if self.__locked else tk.RAISED)
        self.__lock_button = self.__create_button(lock, off)
        if bool(settings.get(Equation.LOCK_KEY, False)): lock()
    def __construct_hide(self, settings):
        on, off = ("hidden", "hide")
        def hide():
            self.__hidden = not self.__hidden
            self.__hide_button.config(
                image = self.__get_button_image(on if self.__hidden else off),
                relief = tk.SUNKEN if self.__hidden else tk.RAISED)
            self.__replot()
        self.__hide_button = self.__create_button(hide, off)
        if bool(settings.get(Equation.HIDE_KEY, False)): hide()
    def __construct_contour(self, settings):
        on, off = ("contour", "surface")
        def contour():
            self.__contoured = not self.__contoured
            self.__contour_button.config(
                image = self.__get_button_image(on if self.__contoured else off),
                relief = tk.SUNKEN if self.__contoured else tk.RAISED)
            self.__replot()
        self.__contour_button = self.__create_button(contour, off)
        if bool(settings.get(Equation.CONTOUR_KEY, False)): contour()
    def __construct_remove(self):
        def remove(self):
            self.pack_forget()
            self.__remove_func(self)
        self.__remove_button = self.__create_button(lambda s = self : remove(s), "remove")
    def __create_button(self, command, path):
        button = tk.Button(self.__inner, command = command)
        if path is not None: button.configure(image = self.__get_button_image(path))
        Theme.get_instance().configure_button(button)
        return button
    def __get_button_image(self, path):
        return ImageManager.get_instance().get_image(path + ".png", self.__button_size,
            self.__button_size)

    def __close_colour_window(self, *_args):
        if self.__colour_window_open:
            self.__colour_window_open = False
            w = self.__colour_window
            self.__colour_window = None
            self.__colour_frame = None
            self.__red = self.__green = self.__blue = None
            w.destroy()
            self.__replot()
    def __colour_update(self, *_args):
        if not any(map(lambda w : w is None, (self.__red, self.__green, self.__blue))):
            self.__r = self.__red.get()
            self.__g = self.__green.get()
            self.__b = self.__blue.get()
        self.__colour_button.configure(image = ImageManager.get_instance().get_colour(
            self.__r, self.__g, self.__b, self.__button_size, self.__button_size))

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
        if self.__debounce_update_id is not None:
            DelayTracker.get_instance().end_delay(self, self.__debounce_update_id)
        self.__debounce_update_id = self.after(self.__debounce_delay, self.__update)
        DelayTracker.get_instance().add_delay(self, self.__debounce_update_id)
    def __debounce_replot(self, *_args):
        if self.__debounce_replot_id is not None:
            DelayTracker.get_instance().end_delay(self, self.__debounce_replot_id)
        self.__debounce_replot_id = self.after(self.__debounce_delay, self.__replot)
        DelayTracker.get_instance().add_delay(self, self.__debounce_replot_id)

    def __generic_updates(self):
        b = self.__parsed.get_binding()
        if b is not None and b.get_plot_type() in PlotType.parametric():
            self.__value_count = len(b.get_tuv_symbols())
        else:
            self.__value_count = 0
        self.__cancel_plot = False
        for i in range(self.__value_count):
            if self.__values[i].get_dict() is None:
                self.__cancel_plot = True
                break
        self.__parsed.set_colour((self.__r / 255.0, self.__g / 255.0, self.__b / 255.0))
    def __update(self, *_args):
        DelayTracker.get_instance().remove_delay(self, self.__debounce_update_id)
        self.__debounce_update_id = None
        self.__parsed = Parsed(self.get_text())
        self.__parsed.set_equation(self)
        self.__generic_updates()
        self.__update_func(self)
    def __replot(self, *_args):
        self.__generic_updates()
        self.__replot_func()
    def set_width(self, w):
        self.__inner.configure(width = w)

    def label(self, t, text):
        self.__readout_type = t
        self.__readout_tooltip.set_text(text)

    def __place_buttons(self):
        buttons = []
        plot_buttons = self.__plottable and not self.__cancel_plot
        if plot_buttons:
            buttons.append(self.__colour_button)
            buttons.append(self.__hide_button)
        else:
            self.__colour_button.place_forget()
            self.__hide_button.place_forget()
            self.__close_colour_window()
        buttons.append(self.__lock_button)
        if plot_buttons and self.get_parsed().get_binding().get_plot_type() in \
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
        for v in self.__values: v.pack_forget()
        self.__readout.pack_forget()

        b = self.__parsed.get_binding()
        if self.__plottable and b.get_plot_type() in PlotType.parametric():
            tuv = b.get_tuv_symbols()
            for i, x in enumerate(sorted(list(tuv), key = str)):
                if self.__values[i].get_symbol() != x:
                    self.__values[i].set_data(x, *self.__parametric_limits.get(x, (-1, 1)))
                self.__values[i].pack(fill = tk.X, expand = True)
            if self.__cancel_plot:
                self.label(EquationLabelType.ERROR, "Invalid parametric limits.")
            else:
                for i in range(self.__value_count):
                    self.__parametric_limits.update(self.__values[i].get_dict())
            b.set_parametric_limits(self.__parametric_limits)

        if self.__readout_active: self.__readout.pack()
    def __set_height(self):
        buttons = (self.__button_size + self.__spacing) * self.__button_count - self.__spacing

        content = self.__min_height + self.__spacing
        content += self.__value_height * self.__value_count
        if self.__readout_active:
            content += self.__readout_height

        h = max(content, buttons)
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
    def has_cancelled_plot(self):
        return self.__cancel_plot
    def is_hidden(self):
        return self.__hidden
    def is_contoured(self):
        return self.__contoured
    def get_text(self):
        return self.__entry.get()
    def get_parsed(self):
        return self.__parsed
