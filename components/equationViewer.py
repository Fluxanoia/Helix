import enum

import tkinter as tk
from utils.parsing import Dimension

from utils.theme import Theme
from utils.images import ImageManager
from utils.fonts import FontManager
from utils.plotting import HelixPlot

class ViewMode(enum.Enum):
    NONE    = 0
    EMPTY   = 1
    TWO_D   = 2
    THREE_D = 3

class EquationViewer(tk.Frame):

    __mode = ViewMode.NONE

    __plots = []

    __view_rect = [-10, -10, 20, 20]
    __elev = 30
    __azim = -60
    __view_cuboid = [-10, -10, -10, 20, 20, 20]

    __drag_pos = None
    __drag_scale_3d = 800

    __width = None
    __frame = None
    __widget = None
    __mode_selector = None
    __empty_message = None
    __plot = None

    def __init__(self, parent, width):
        super().__init__(parent)
        Theme.getInstance().configureViewer(self)

        self.__width = width

        self.__constructViewFrame(parent)
        self.__constructModeSelector()
        self.__constructEmptyMessage()

        self.place(relx = width, relwidth = 1 - width, relheight = 1)

        self.__draw()

    def __constructViewFrame(self, parent):
        self.__frame = tk.Frame(parent)
        Theme.getInstance().configureViewer(self.__frame)
        self.__frame.place(relx = self.__width,
            rely = 0,
            relwidth = 1 - self.__width,
            relheight = 1)
        self.__plot = HelixPlot(self.__frame,
            lambda e : self.drag_start(e),
            lambda e, w, h : self.drag(e, w, h),
            lambda e : self.zoom(e))

    def __constructModeSelector(self):
        self.__mode_selector = tk.Frame(self.__frame)
        Theme.getInstance().configureViewer(self.__mode_selector)

        sub_frame = tk.Frame(self.__mode_selector, width = 240)
        Theme.getInstance().configureViewer(sub_frame)
        button_2d = tk.Button(sub_frame, text = "2D",
            command = lambda : self.__modeSwitcher(ViewMode.TWO_D))
        button_3d = tk.Button(sub_frame, text = "3D",
            command = lambda : self.__modeSwitcher(ViewMode.THREE_D))
        Theme.getInstance().configureViewerButton(button_2d)
        Theme.getInstance().configureViewerButton(button_3d)
        FontManager.getInstance().configureText(button_2d)
        FontManager.getInstance().configureText(button_3d)
        button_2d.pack(side = tk.LEFT)
        button_3d.pack(side = tk.RIGHT)

        label_top = tk.Label(self.__mode_selector,
            text = "Pick a plotting mode for this tab:")
        label_bottom = tk.Label(self.__mode_selector,
            text = "You can't change it once you pick (yet)!")
        Theme.getInstance().configureViewerText(label_top)
        Theme.getInstance().configureViewerText(label_bottom)
        FontManager.getInstance().configureText(label_top)
        FontManager.getInstance().configureText(label_bottom)
        label_top.pack()
        sub_frame.pack(ipadx = 20, ipady = 20)
        label_bottom.pack()

    def __constructEmptyMessage(self):
        self.__empty_message = tk.Label(self.__frame,
            text = "Create an entry on the left to plot something!")
        Theme.getInstance().configureViewerText(self.__empty_message)
        FontManager.getInstance().configureText(self.__empty_message)

    def __modeSwitcher(self, mode):
        self.__mode = mode
        self.__draw()

    def plot(self, plots):
        self.__plots = plots
        self.__draw()

    def __draw_plot2d(self):
        self.__plot.set_dim(Dimension.TWO_D)
        self.__plot.remove_plots()
        plots = list(filter(lambda p : p.has_dim() and p.get_dim() == self.__mode.value, \
            self.__plots))
        self.__plot.add_plots_2d(plots)
        self.__plot.redraw()

    def __draw_plot3d(self):
        self.__plot.set_dim(Dimension.THREE_D)
        self.__plot.remove_plots()
        plots = list(filter(lambda p : p.has_dim() and p.get_dim() == self.__mode.value, \
            self.__plots))
        self.__plot.add_plots_3d(plots)
        self.__plot.redraw()

    def __draw(self):
        mode = ViewMode.EMPTY if self.__mode in [ViewMode.TWO_D, ViewMode.THREE_D] \
            and len(self.__plots) == 0 else self.__mode

        no_mode = (mode == ViewMode.NONE) \
            and (not self.__widget == self.__mode_selector)
        no_plot = (mode == ViewMode.EMPTY) \
            and (not self.__widget == self.__empty_message)
        plot2d = mode == ViewMode.TWO_D
        plot3d = mode == ViewMode.THREE_D

        if any([no_mode, no_plot, plot2d, plot3d]) and self.__widget is not None:
            self.__widget.pack_forget()

        if no_mode: self.__widget = self.__mode_selector
        if no_plot: self.__widget = self.__empty_message
        if plot2d: self.__draw_plot2d()
        if plot3d: self.__draw_plot3d()
        if plot2d or plot3d: self.__widget = self.__plot.widget()

        if any([no_mode, no_plot, plot2d, plot3d]):
            self.__widget.pack(fill = tk.BOTH, expand = True)

    def drag_start(self, e):
        self.__drag_pos = (e.x, e.y)

    def drag(self, e, w, h):
        if self.__mode not in [ViewMode.TWO_D, ViewMode.THREE_D]:
            return
        if self.__mode == ViewMode.TWO_D:
            self.__view_rect[0] += (self.__drag_pos[0] - e.x) \
                * (self.__view_rect[2] / w)
            self.__view_rect[1] += (e.y - self.__drag_pos[1]) \
                * (self.__view_rect[3] / h)
            self.__drag_pos = (e.x, e.y)
            return self.get_lims()
        if self.__mode == ViewMode.THREE_D:
            self.__azim += (self.__drag_pos[0] - e.x) / (self.__drag_scale_3d / w)
            self.__elev += (e.y - self.__drag_pos[1]) / (self.__drag_scale_3d / h)
            self.__drag_pos = (e.x, e.y)
            return (self.__elev, self.__azim)

    def zoom(self, e):
        if self.__mode not in [ViewMode.TWO_D, ViewMode.THREE_D]:
            return
        if self.__mode == ViewMode.TWO_D:
            lw = max(self.__view_rect[2:4])
            sd = (0.05 * lw) * (1 if e.num == 5 or e.delta < 0 else -1)
            self.__view_rect[0] -= sd
            self.__view_rect[1] -= sd
            self.__view_rect[2] += 2 * sd
            self.__view_rect[3] += 2 * sd
        if self.__mode == ViewMode.THREE_D:
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
        if self.__mode not in [ViewMode.TWO_D, ViewMode.THREE_D]:
            return None
        if self.__mode is ViewMode.TWO_D:
            return ((self.get_xmin_2d(), self.get_xmax_2d()), \
                (self.get_ymin_2d(), self.get_ymax_2d()))
        if self.__mode is ViewMode.THREE_D:
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
