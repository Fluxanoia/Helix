import enum

import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import sympy as sy
from sympy.plotting.plot import _matplotlib_list, check_arguments, \
    LineOver1DRangeSeries, SurfaceOver2DRangeSeries, \
    Parametric2DLineSeries, Parametric3DLineSeries, ParametricSurfaceSeries, \
    ContourSeries
from sympy.plotting.plot_implicit import ImplicitSeries
from sympy.core.relational import (Equality, GreaterThan, LessThan, Relational)
from sympy.logic.boolalg import BooleanFunction

from utils.theme import Theme

class Dimension(enum.Enum):
    TWO_D   = 2
    THREE_D = 3

class PlotType(enum.Enum):
    LINE_2D = 0
    PARAMETRIC_2D = 1
    IMPLICIT_2D = 2
    SURFACE = 3
    PARAMETRIC_3D = 4
    PARAMETRIC_SURFACE = 5
    CONTOUR = 6

class HelixPlot(FigureCanvasTkAgg):

    __figure = mpl.figure.Figure()
    __axis2 = None
    __axis3 = None
    __axis = None

    __data = []

    __is_lambda = lambda f : lambda *x : all(getattr(i, f, True) for i in x)
    __is_real = __is_lambda('is_real')
    __is_finite = __is_lambda('is_finite')

    __xlim = (-10, 10)
    __ylim = (-10, 10)
    __zlim = (-10, 10)

    __elev = 30
    __azim = -60

    __dim = None

    __presser = None
    __dragger = None
    __zoomer = None

    def __init__(self, parent, press_func, drag_func, zoom_func):
        super().__init__(self.__figure, master = parent)
        Theme.getInstance().configureFigure(self.__figure)

        self.__axis2 = mpl.axes.Axes(self.__figure, (0, 0, 1, 1))
        Theme.getInstance().configurePlot2D(self.__axis2)

        self.__axis3 = Axes3D(self.__figure, (0, 0, 1, 1))
        Theme.getInstance().configurePlot3D(self.__axis3)

        self.__axis2.set_xlim(self.__xlim)
        self.__axis2.set_ylim(self.__ylim)
        self.__axis3.set_xlim(self.__xlim)
        self.__axis3.set_ylim(self.__ylim)
        self.__axis3.set_zlim(self.__zlim)

        def presser(e):
            self.get_tk_widget().focus_set()
            press_func(e)
        self.__presser = presser

        def dragger(e):
            self.widget().update()
            w = self.widget().winfo_width()
            h = self.widget().winfo_height()
            if self.__dim is Dimension.TWO_D:
                x, y = drag_func(e, w, h)
                self.set_limits(x, y)
            if self.__dim is Dimension.THREE_D:
                e, a = drag_func(e, w, h)
                self.set_view(e, a)
        self.__dragger = dragger

        def zoomer(e):
            if self.__dim is Dimension.TWO_D:
                x, y = zoom_func(e)
                self.set_limits(x, y)
            if self.__dim is Dimension.THREE_D:
                x, y, z = zoom_func(e)
                self.set_limits(x, y, z)
        self.__zoomer = zoomer

        self.get_tk_widget().bind("<ButtonPress-1>", self.__presser)
        self.get_tk_widget().bind("<B1-Motion>", self.__dragger)
        self.get_tk_widget().bind('<Enter>', self.__bind_scroll)
        self.get_tk_widget().bind('<Leave>', self.__unbind_scroll)

        self.draw()

    def widget(self):
        return self.get_tk_widget()

    def __bind_scroll(self, _event):
        self.get_tk_widget().bind_all("<MouseWheel>", self.__zoomer)
        self.get_tk_widget().bind_all("<Button-4>", self.__zoomer)
        self.get_tk_widget().bind_all("<Button-5>", self.__zoomer)

    def __unbind_scroll(self, _event):
        self.get_tk_widget().unbind_all("<MouseWheel>")
        self.get_tk_widget().unbind_all("<Button-4>")
        self.get_tk_widget().unbind_all("<Button-5>")

    # Plot Variables

    def set_limits(self, xlim, ylim, zlim = None):
        if not (self.__is_real(xlim) and self.__is_real(ylim)):
            raise ValueError("Non-real limits in HelixPlot.")
        if not (self.__is_finite(xlim) and self.__is_finite(ylim)):
            raise ValueError("Infinite limits in HelixPlot.")
        if zlim is not None:
            if not (self.__is_finite(zlim) and self.__is_finite(zlim)):
                raise ValueError("Infinite limits in HelixPlot.")
        self.__xlim = xlim
        self.__ylim = ylim
        self.__zlim = zlim
        self.redraw()

    def set_view(self, elev, azim):
        self.__elev = elev
        self.__azim = azim
        self.redraw()

    def set_dim(self, dim):
        if self.__dim == dim: return
        self.__dim = dim
        self.__figure.clf()
        self.__axis = None
        if self.__dim is Dimension.TWO_D:
            self.__axis = self.__axis2
        if self.__dim is Dimension.THREE_D:
            self.__axis = self.__axis3
        if self.__dim is not None:
            self.__figure.add_axes(self.__axis)

    # Plotting

    def remove_plots(self):
        self.__data = []
        if self.__dim is not None: self.__axis.clear()

    def add_plots_2d(self, parsed):
        if self.__dim is not Dimension.TWO_D:
            raise ValueError("Incorrect plot dimension.")

        for p in parsed:
            expr = p.get_blocks()[0]
            if p.get_plot_type() is PlotType.LINE_2D:
                check = check_arguments([expr], 1, 1)[0]
                self.__data.append(LineOver1DRangeSeries(*check, line_color = p.colour))
            elif p.get_plot_type() is PlotType.PARAMETRIC_2D:
                param = (p.get_blocks()[0], p.get_blocks()[1])
                check = check_arguments(param, 2, 1)[0]
                self.__data.append(Parametric2DLineSeries(*check, line_color = p.colour))
            elif p.get_plot_type() is PlotType.IMPLICIT_2D:
                arg_list = []
                if isinstance(expr, BooleanFunction):
                    def arg_expand(bool_expr):
                        for arg in bool_expr.args:
                            if isinstance(arg, BooleanFunction):
                                arg_expand(arg)
                            elif isinstance(arg, Relational):
                                arg_list.append(arg)
                    arg_expand(expr)

                has_equality = False
                if any(isinstance(e, (Equality, GreaterThan, LessThan)) for e in arg_list):
                    has_equality = True
                elif not isinstance(expr, Relational):
                    expr = sy.Eq(expr, 0)
                    has_equality = True
                elif isinstance(expr, (Equality, GreaterThan, LessThan)):
                    has_equality = True

                from utils.parsing import Parser
                parser = Parser.getInstance()
                x = (parser.get_symbol_x(), *self.__xlim)
                y = (parser.get_symbol_y(), *self.__ylim)
                self.__data.append(ImplicitSeries(expr, x, y, has_equality,
                    True, 0, 300, p.colour))
            else:
                raise ValueError("Incorrect parsed dimension.")

    def add_plots_3d(self, parsed):
        if self.__dim is not Dimension.THREE_D:
            raise ValueError("Incorrect plot dimension.")

        for p in parsed:
            expr = p.get_blocks()[0]
            if p.get_plot_type() is PlotType.SURFACE:
                check = check_arguments([expr], 1, 2)[0]
                self.__data.append(SurfaceOver2DRangeSeries(*check, surface_color = p.colour))
            elif p.get_plot_type() is PlotType.PARAMETRIC_3D:
                param = (p.get_blocks()[0], p.get_blocks()[1], p.get_blocks()[2])
                check = check_arguments(param, 3, 1)[0]
                self.__data.append(Parametric3DLineSeries(*check, line_color = p.colour))
            elif p.get_plot_type() is PlotType.PARAMETRIC_SURFACE:
                param = (p.get_blocks()[0], p.get_blocks()[1], p.get_blocks()[2])
                check = check_arguments(param, 3, 2)[0]
                self.__data.append(ParametricSurfaceSeries(*check, surface_color = p.colour))
            elif p.get_plot_type() is PlotType.CONTOUR:
                check = check_arguments([expr], 1, 2)[0]
                self.__data.append(ContourSeries(*check))
                self.__data[-1].line_color = p.colour
            else:
                raise ValueError("Incorrect parsed dimension.")

    def redraw(self):
        if self.__dim is None: return

        self.__axis.clear()

        for s in self.__data:
            if s.is_3D:
                s.start_x = self.__xlim[0]
                s.end_x = self.__xlim[1]
                s.start_y = self.__ylim[0]
                s.end_y = self.__ylim[1]
            else:
                s.start = self.__xlim[0]
                s.end = self.__xlim[1]

            if s.is_2Dline:
                self.__axis.add_collection(LineCollection(s.get_segments(),
                    colors = s.line_color))
            elif s.is_contour:
                colours = None if s.line_color is None else [s.line_color]
                self.__axis.contour(*s.get_meshes(), colors = colours)
            elif s.is_3Dline:
                self.__axis.add_collection(Line3DCollection(s.get_segments(),
                    colors = s.line_color))
            elif s.is_3Dsurface:
                x, y, z = s.get_meshes()
                self.__axis.plot_surface(x, y, z, color = s.surface_color,
                    rstride = 1, cstride = 1, linewidth = 0.1)
            elif s.is_implicit:
                points = s.get_raster()
                if len(points) == 2:
                    x, y = _matplotlib_list(points[0])
                    self.__axis.fill(x, y, facecolor = s.line_color)
                else:
                    colormap = mpl.colors.ListedColormap(["white", s.line_color])
                    xarray, yarray, zarray, plot_type = points
                    if plot_type == 'contour':
                        self.__axis.contour(xarray, yarray, zarray, cmap = colormap)
                    else:
                        self.__axis.contourf(xarray, yarray, zarray, cmap = colormap)
            else:
                raise NotImplementedError("Unimplemented plot type in HelixPlot")

        if self.__dim is Dimension.TWO_D:
            self.__axis2.set_xlim(self.__xlim)
            self.__axis2.set_ylim(self.__ylim)
            self.__axis2.spines['left'].set_position('center')
            self.__axis2.spines['bottom'].set_position('center')

        if self.__dim is Dimension.THREE_D:
            self.__axis3.set_xlim(self.__xlim)
            self.__axis3.set_ylim(self.__ylim)
            self.__axis3.set_zlim(self.__zlim)
            self.__axis3.view_init(self.__elev, self.__azim)

            self.__axis3.set_xlabel('$x$', fontsize = 20)
            self.__axis3.set_ylabel('$y$', fontsize = 20)
            self.__axis3.set_zlabel('$z$', fontsize = 20)

        self.draw()
