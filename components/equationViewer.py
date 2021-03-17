import tkinter as tk

from utils.theme import Theme
from utils.images import ImageManager
from utils.parsing import Parser
from utils.maths import Dimension, PlotType
from components.plot import HelixPlot

class LimitValue(tk.Frame):

    def __init__(self, parent, name, v1, v2, connect = "to"):
        theme = Theme.get_instance()
        super().__init__(parent, bg = theme.get_body_colour(), width = 320, height = 50)

        self.__label = tk.Label(self, text = name)
        self.__to = tk.Label(self, text = connect, width = len(connect))
        theme.configure_label(self.__label)
        theme.configure_label(self.__to)

        self.__entry_var_l = tk.StringVar()
        self.__entry_var_r = tk.StringVar()
        self.__entry_var_l.set(str(v1))
        self.__entry_var_r.set(str(v2))
        self.__entry_l = tk.Entry(self, textvariable = self.__entry_var_l)
        self.__entry_r = tk.Entry(self, textvariable = self.__entry_var_r)
        theme.configure_entry(self.__entry_l)
        theme.configure_entry(self.__entry_r)

        self.__label.place(y = 10, relx = 0, relwidth = 0.2)
        self.__entry_l.place(y = 10, relx = 0.2, relwidth = 0.3)
        self.__to.place(y = 10, relx = 0.5, relwidth = 0.2)
        self.__entry_r.place(y = 10, relx = 0.7, relwidth = 0.3)

    def get_data(self):
        l = self.__entry_var_l.get()
        r = self.__entry_var_r.get()
        l, r = Parser.get_instance().parse_number((l, r))
        if any(map(lambda n : n is None, [l, r])):
            return None
        else:
            l = float(l)
            r = float(r)
            if l > r: l, r = r, l
            return (l, r)

class EquationViewer(tk.Frame):

    DIM_KEY = "view_dimension"
    RECT_KEY = "view_rect"
    ELEV_KEY = "view_elev"
    AZIM_KEY = "view_azim"
    CUBOID_KEY = "view_cuboid"

    def __init__(self, parent, width, change_func):
        super().__init__(parent)
        Theme.get_instance().configure_viewer(self)

        self.__width = width
        self.__change_func = change_func

        self.__mode = Dimension.TWO_D

        self.__raw_plots = []
        self.__plots = []

        self.__view_rect = [-10, -10, 20, 20]
        self.__elev = 30
        self.__azim = -60
        self.__view_cuboid = [-10, -10, -10, 20, 20, 20]

        self.__drag_pos = None
        self.__drag_scale_3d = 800

        self.__button_size = 40

        self.__limit_frame = None
        self.__limit_window = None
        self.__limit_window_open = False
        self.__limit_window_active = True
        self.__x, self.__y, self.__z, self.__a = None, None, None, None

        self.__construct_view_frame(parent)
        self.__construct_buttons()
        self.__construct_limits()

        self.place(relx = width, relwidth = 1 - width, relheight = 1)

        self.__draw()
    def __construct_view_frame(self, parent):
        self.__frame = tk.Frame(parent)
        Theme.get_instance().configure_viewer(self.__frame)
        self.__frame.place(relx = self.__width,
            rely = 0,
            relwidth = 1 - self.__width,
            relheight = 1)
        self.__plot = HelixPlot(self.__frame,
            lambda e : self.drag_start(e),
            lambda e, w, h : self.drag(e, w, h),
            lambda e : self.zoom(e))
        self.__plot.set_dim(self.__mode)
        self.__plot.widget().pack(fill = tk.BOTH, expand = True)
    def __construct_buttons(self):
        def home():
            if self.__mode is Dimension.TWO_D:
                self.__view_rect = [-10, -10, 20, 20]
            if self.__mode is Dimension.THREE_D:
                self.__elev = 30
                self.__azim = -60
                self.__view_cuboid = [-10, -10, -10, 20, 20, 20]
                self.__plot.set_view(self.__elev, self.__azim)
            self.__plot.set_limits(*self.get_lims())

        self.__2d_button = tk.Button(self.__frame, image = self.__get_button_image("2d"),
            command = lambda : self.__mode_switcher(Dimension.TWO_D))
        self.__3d_button = tk.Button(self.__frame, image = self.__get_button_image("3d"),
            command = lambda : self.__mode_switcher(Dimension.THREE_D))
        self.__home_button = tk.Button(self.__frame, image = self.__get_button_image("home"),
            command = home)
        theme = Theme.get_instance()
        theme.configure_button(self.__2d_button)
        theme.configure_button(self.__3d_button)
        theme.configure_button(self.__home_button)
        self.__2d_button.place(x = 10, y = 10,
            w = self.__button_size, h = self.__button_size)
        self.__3d_button.place(x = 10, y = self.__button_size + 20,
            w = self.__button_size, h = self.__button_size)
        self.__home_button.place(relx = 1,
            x = -(self.__button_size + 10), y = 10,
            w = self.__button_size, h = self.__button_size)
    def __construct_limits(self):
        theme = Theme.get_instance()

        def create_limit_frame():
            self.__limit_frame = tk.Frame(self.__limit_window)
            theme.configure_colour_window(self.__limit_frame)

            title = tk.Label(self.__limit_frame, text = "Setting the Limits")
            theme.configure_scale(title)
            title.pack()

            if self.__mode is Dimension.TWO_D:
                self.__x = LimitValue(self.__limit_frame,
                    "x", self.get_xmin_2d(), self.get_xmax_2d())
                self.__y = LimitValue(self.__limit_frame,
                    "y", self.get_ymin_2d(), self.get_ymax_2d())
            if self.__mode is Dimension.THREE_D:
                self.__x = LimitValue(self.__limit_frame,
                    "x", self.get_xmin_3d(), self.get_xmax_3d())
                self.__y = LimitValue(self.__limit_frame,
                    "y", self.get_ymin_3d(), self.get_ymax_3d())
                self.__z = LimitValue(self.__limit_frame,
                    "z", self.get_zmin_3d(), self.get_zmax_3d())
                self.__a = LimitValue(self.__limit_frame,
                    "elev.", self.__elev, self.__azim, connect = "azim.")
            for w in (self.__x, self.__y, self.__z, self.__a):
                if w is not None: w.pack(fill = tk.X, expand = True)

            def set_lims():
                x = self.__x.get_data() if self.__x is not None else None
                y = self.__y.get_data() if self.__y is not None else None
                z = self.__z.get_data() if self.__z is not None else None
                a = self.__a.get_data() if self.__a is not None else None

                if any(map(lambda d : d is None, (x, y, z, a))):
                    self.__view_rect = [x[0], y[0], x[1] - x[0], y[1] - y[0]]
                else:
                    self.__view_cuboid = [x[0], y[0], z[0], x[1] - x[0], y[1] - y[0], z[1] - z[0]]
                    self.__elev, self.__azim = a
                    self.__plot.set_view(self.__elev, self.__azim)
                self.__plot.set_limits(*self.get_lims())

            button = tk.Button(self.__limit_frame, text = "Set", command = set_lims)
            theme.configure_button(button)
            button.pack()

            self.__limit_frame.pack(fill = tk.BOTH, expand = True)

        def open_window(_e = None):
            if not self.__limit_window_open:
                self.__limit_window_open = True

                def enter(_e = None):
                    self.__limit_window.unbind_all("<ButtonPress-1>")
                def leave(_e = None):
                    self.__limit_window.bind_all("<ButtonPress-1>", self.__close_limit_window)

                x, y, _, _ = self.bbox()
                x += self.__limit_button.winfo_rootx() - 250
                y += self.__limit_button.winfo_rooty() + 50
                self.__limit_window = tk.Toplevel(self,
                    padx = 10, pady = 10, highlightthickness = 3)
                theme.configure_colour_window(self.__limit_window)
                self.__limit_window.wm_overrideredirect(1)
                self.__limit_window.wm_geometry("+%d+%d" % (x, y))
                self.__limit_window.bind('<Enter>', enter)
                self.__limit_window.bind('<Leave>', leave)
                create_limit_frame()
                leave()
                try:
                    self.__limit_window.tk.call("::tk::unsupported::MacWindowStyle",
                        "style", self.__limit_window._w, "help", "noActivates")
                except tk.TclError:
                    pass

        self.__limit_button = tk.Button(self.__frame, image = self.__get_button_image("limits"),
            command = open_window)
        theme.configure_button(self.__limit_button)
        self.__limit_button.place(relx = 1,
            x = -(self.__button_size + 10), y = self.__button_size + 20,
            w = self.__button_size, h = self.__button_size)
    def __get_button_image(self, path):
        return ImageManager.get_instance().get_image(path + ".png",
            self.__button_size, self.__button_size)

    def __close_limit_window(self, *_args):
        if self.__limit_window_open:
            self.__limit_window_open = False
            w = self.__limit_window
            self.__limit_window = None
            self.__limit_frame = None
            self.__x, self.__y, self.__z, self.__a = None, None, None, None
            w.destroy()

    def set_settings(self, settings):
        self.__view_rect = list(map(float, settings[EquationViewer.RECT_KEY].split(" ")))
        self.__elev = float(settings[EquationViewer.ELEV_KEY])
        self.__azim = float(settings[EquationViewer.AZIM_KEY])
        self.__view_cuboid = list(map(float, settings[EquationViewer.CUBOID_KEY].split(" ")))
        self.__mode_switcher(Dimension(int(settings[EquationViewer.DIM_KEY])))
        self.__plot.set_view(self.__elev, self.__azim)
    def add_settings(self, settings):
        settings[EquationViewer.DIM_KEY] = self.__mode.value
        settings[EquationViewer.RECT_KEY] = " ".join(map(str, self.__view_rect))
        settings[EquationViewer.ELEV_KEY] = str(self.__elev)
        settings[EquationViewer.AZIM_KEY] = str(self.__azim)
        settings[EquationViewer.CUBOID_KEY] = " ".join(map(str, self.__view_cuboid))
        return settings

    def __mode_switcher(self, mode):
        self.__mode = mode
        self.__plot.set_dim(mode)
        self.__plot.set_limits(*self.get_lims())
        self.__process_plots()
        self.__draw()
    def __process_plots(self):
        self.__plots = list(filter(lambda p : isinstance(p.get_plot_type(), PlotType) and \
            PlotType.get_dim(p.get_plot_type()) is self.__mode, self.__raw_plots))
        self.__change_func()
    def plot(self, plots):
        self.__raw_plots = plots
        self.__process_plots()
        self.__draw()
    def __draw(self):
        self.__plot.set_plots(self.__plots, self.__mode)
        self.__plot.redraw()

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)
        self.__change_func()
    def drag(self, e, w, h):
        self.__change_func()
        if self.__mode is Dimension.TWO_D:
            self.__view_rect[0] += (self.__drag_pos[0] - e.x) \
                * (self.__view_rect[2] / w)
            self.__view_rect[1] += (e.y - self.__drag_pos[1]) \
                * (self.__view_rect[3] / h)
            self.__drag_pos = (e.x, e.y)
            return self.get_lims()
        if self.__mode is Dimension.THREE_D:
            self.__azim += (self.__drag_pos[0] - e.x) / (self.__drag_scale_3d / w)
            self.__elev += (e.y - self.__drag_pos[1]) / (self.__drag_scale_3d / h)
            self.__drag_pos = (e.x, e.y)
            return (self.__elev, self.__azim)
    def zoom(self, e):
        if self.__mode is Dimension.TWO_D:
            lw = max(self.__view_rect[2:4])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_rect[0] -= sd
            self.__view_rect[1] -= sd
            self.__view_rect[2] += 2 * sd
            self.__view_rect[3] += 2 * sd
        if self.__mode is Dimension.THREE_D:
            lw = max(self.__view_cuboid[3:6])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_cuboid[0] -= sd
            self.__view_cuboid[1] -= sd
            self.__view_cuboid[2] -= sd
            self.__view_cuboid[3] += 2 * sd
            self.__view_cuboid[4] += 2 * sd
            self.__view_cuboid[5] += 2 * sd
        self.__change_func()
        return self.get_lims()

    def get_lims(self):
        if self.__mode not in [Dimension.TWO_D, Dimension.THREE_D]:
            return None
        if self.__mode is Dimension.TWO_D:
            return ((self.get_xmin_2d(), self.get_xmax_2d()), \
                (self.get_ymin_2d(), self.get_ymax_2d()))
        if self.__mode is Dimension.THREE_D:
            return ((self.get_xmin_3d(), self.get_xmax_3d()), \
                (self.get_ymin_3d(), self.get_ymax_3d()), \
                (self.get_zmin_3d(), self.get_zmax_3d()))
    def get_xmin_2d(self): return self.__view_rect[0]
    def get_xmax_2d(self): return self.__view_rect[0] + self.__view_rect[2]
    def get_ymin_2d(self): return self.__view_rect[1]
    def get_ymax_2d(self): return self.__view_rect[1] + self.__view_rect[3]
    def get_xmin_3d(self): return self.__view_cuboid[0]
    def get_xmax_3d(self): return self.__view_cuboid[0] + self.__view_cuboid[3]
    def get_ymin_3d(self): return self.__view_cuboid[1]
    def get_ymax_3d(self): return self.__view_cuboid[1] + self.__view_cuboid[4]
    def get_zmin_3d(self): return self.__view_cuboid[2]
    def get_zmax_3d(self): return self.__view_cuboid[2] + self.__view_cuboid[5]
