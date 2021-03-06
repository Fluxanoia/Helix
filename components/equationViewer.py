import tkinter as tk

from utils.theme import Theme
from utils.fonts import FontManager
from utils.maths import Dimension, PlotType
from components.plot import HelixPlot

class EquationViewer(tk.Frame):

    DIM_KEY = "view_dimension"
    RECT_KEY = "view_rect"
    ELEV_KEY = "view_elev"
    AZIM_KEY = "view_azim"
    CUBOID_KEY = "view_cuboid"

    def __init__(self, parent, width):
        super().__init__(parent)
        Theme.get_instance().configure_viewer(self)

        self.__width = width

        self.__mode = Dimension.TWO_D

        self.__raw_plots = []
        self.__plots = []

        self.__view_rect = [-10, -10, 20, 20]
        self.__elev = 30
        self.__azim = -60
        self.__view_cuboid = [-10, -10, -10, 20, 20, 20]

        self.__drag_pos = None
        self.__drag_scale_3d = 800

        self.__constructViewFrame(parent)
        self.__constructDimensionButtons()

        self.place(relx = width, relwidth = 1 - width, relheight = 1)

        self.__draw()
    def __constructViewFrame(self, parent):
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
    def __constructDimensionButtons(self):
        self.__2d_button = tk.Button(self.__frame, text = "2D",
            command = lambda : self.__mode_switcher(Dimension.TWO_D))
        self.__3d_button = tk.Button(self.__frame, text = "3D",
            command = lambda : self.__mode_switcher(Dimension.THREE_D))
        Theme.get_instance().configure_viewer_button(self.__2d_button)
        Theme.get_instance().configure_viewer_button(self.__3d_button)
        FontManager.get_instance().configure_text(self.__2d_button)
        FontManager.get_instance().configure_text(self.__3d_button)
        size = 40
        self.__2d_button.place(x = 10, y = 10, w = size, h = size)
        self.__3d_button.place(x = 10, y = size + 20, w = size, h = size)

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
    def plot(self, plots):
        self.__raw_plots = plots
        self.__process_plots()
        self.__draw()
    def __draw(self):
        self.__plot.set_plots(self.__plots, self.__mode)
        self.__plot.redraw()

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)
    def drag(self, e, w, h):
        if self.__mode == Dimension.TWO_D:
            self.__view_rect[0] += (self.__drag_pos[0] - e.x) \
                * (self.__view_rect[2] / w)
            self.__view_rect[1] += (e.y - self.__drag_pos[1]) \
                * (self.__view_rect[3] / h)
            self.__drag_pos = (e.x, e.y)
            return self.get_lims()
        if self.__mode == Dimension.THREE_D:
            self.__azim += (self.__drag_pos[0] - e.x) / (self.__drag_scale_3d / w)
            self.__elev += (e.y - self.__drag_pos[1]) / (self.__drag_scale_3d / h)
            self.__drag_pos = (e.x, e.y)
            return (self.__elev, self.__azim)
    def zoom(self, e):
        if self.__mode == Dimension.TWO_D:
            lw = max(self.__view_rect[2:4])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_rect[0] -= sd
            self.__view_rect[1] -= sd
            self.__view_rect[2] += 2 * sd
            self.__view_rect[3] += 2 * sd
        if self.__mode == Dimension.THREE_D:
            lw = max(self.__view_cuboid[3:6])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_cuboid[0] -= sd
            self.__view_cuboid[1] -= sd
            self.__view_cuboid[2] -= sd
            self.__view_cuboid[3] += 2 * sd
            self.__view_cuboid[4] += 2 * sd
            self.__view_cuboid[5] += 2 * sd
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
