import math
from abc import ABC, abstractmethod

import numpy as np
import numpy.ma as ma

from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import sympy as sy
from sympy.plotting.plot import _matplotlib_list, check_arguments, \
    LineOver1DRangeSeries, SurfaceOver2DRangeSeries, \
    Parametric2DLineSeries, Parametric3DLineSeries, ParametricSurfaceSeries, \
    ContourSeries
from sympy.plotting.plot_implicit import ImplicitSeries
from sympy.core.relational import (Equality, GreaterThan, LessThan, Relational)
from sympy.logic.boolalg import BooleanFunction

from utils.parsing import Parser
from utils.maths import PlotType
from utils.override import overrides

class HelixSeries(ABC):

    def __init__(self, plot):
        self._plot = plot
        self._data = []
        self._series = None
        self._min_x = None
        self._max_x = None
        self._min_y = None
        self._max_y = None
        self._min_z = None
        self._max_z = None
        self._point_density = 2.5

    @abstractmethod
    def draw(self, axis, xlim, ylim, zlim): pass

    def _expand_data(self, xlim, ylim, zlim):
        if self.__unbounded():
            self._generate_data(xlim, ylim, zlim)
            self._min_x, self._max_x = xlim
            self._min_y, self._max_y = ylim
            self._min_z, self._max_z = zlim
        else:
            if xlim[0] < self._min_x:
                self._generate_data((xlim[0], self._min_x), self.__y(), self.__z())
                self._min_x = xlim[0]
            if xlim[1] > self._max_x:
                self._generate_data((self._max_x, xlim[1]), self.__y(), self.__z())
                self._max_x = xlim[1]
            if ylim[0] < self._min_y:
                self._generate_data(self.__x(), (ylim[0], self._min_y), self.__z())
                self._min_y = ylim[0]
            if ylim[1] > self._max_y:
                self._generate_data(self.__x(), (self._max_y, ylim[1]), self.__z())
                self._max_y = ylim[1]
            if zlim[0] < self._min_z:
                self._generate_data(self.__x(), self.__y(), (zlim[0], self._min_z))
                self._min_z = zlim[0]
            if zlim[1] > self._max_z:
                self._generate_data(self.__x(), self.__y(), (self._max_z, zlim[1]))
                self._max_z = zlim[1]
    def _generate_data(self, xlim, ylim, zlim): pass

    def __x(self): return (self._min_x, self._max_x)
    def __y(self): return (self._min_y, self._max_y)
    def __z(self): return (self._min_z, self._max_z)
    def _dx(self, xlim): return xlim != self.__x()
    def _dy(self, ylim): return ylim != self.__y()
    def _dz(self, zlim): return zlim != self.__z()
    def __unbounded(self): return any([x is None for x in self.__x() + self.__y() + self.__z()])

    def get_plot(self): return self._plot

    def _expand_mesh(self, xlim, ylim):
        self._series.start_x, self._series.end_x = xlim
        self._series.start_y, self._series.end_y = ylim
        if self.__unbounded():
            self._series.nb_of_points_x = math.ceil((xlim[1] - xlim[0]) * self._point_density)
            self._series.nb_of_points_y = math.ceil((ylim[1] - ylim[0]) * self._point_density)
            self._data = self._series.get_meshes()
        else:
            prepend_x = xlim[0] < self._min_x
            append_x = xlim[1] > self._max_x
            prepend_y = ylim[0] < self._min_y
            append_y = ylim[1] > self._max_y
            assert len([x for x in [prepend_x, append_x, prepend_y, append_y] if x]) == 1
            if prepend_x or append_x:
                self._series.nb_of_points_x = math.ceil((xlim[1] - xlim[0]) * self._point_density)
                self._series.nb_of_points_y = len(self._data[1])
                x, y, z = self._series.get_meshes()
                if prepend_x:
                    x = np.concatenate((x, self._data[0]), axis = 1)
                    y = np.concatenate((y, self._data[1]), axis = 1)
                    z = ma.concatenate((z, self._data[2]), axis = 1)
                if append_x:
                    x = np.concatenate((self._data[0], x), axis = 1)
                    y = np.concatenate((self._data[1], y), axis = 1)
                    z = ma.concatenate((self._data[2], z), axis = 1)
            if prepend_y or append_y:
                self._series.nb_of_points_x = len(self._data[0][0])
                self._series.nb_of_points_y = math.ceil((ylim[1] - ylim[0]) * self._point_density)
                x, y, z = self._series.get_meshes()
                if prepend_y:
                    x = np.concatenate((x, self._data[0]), axis = 0)
                    y = np.concatenate((y, self._data[1]), axis = 0)
                    z = ma.concatenate((z, self._data[2]), axis = 0)
                if append_y:
                    x = np.concatenate((self._data[0], x), axis = 0)
                    y = np.concatenate((self._data[1], y), axis = 0)
                    z = ma.concatenate((self._data[2], z), axis = 0)
            self._data = (x, y, z)
    def _get_mesh(self, xlim, ylim):
        x1, x2 = (0, len(self._data[0][0]) - 1)
        y1, y2 = (0, len(self._data[1]) - 1)
        while self._data[0][0][x1] < xlim[0]: x1 += 1
        while self._data[0][0][x2] >= xlim[1]: x2 -= 1
        while self._data[1][y1][0] < ylim[0]: y1 += 1
        while self._data[1][y2][0] >= ylim[1]: y2 -= 1
        x2 += 1
        y2 += 1
        return (self._data[0][y1:y2, x1:x2], self._data[1][y1:y2, x1:x2],
            self._data[2][y1:y2, x1:x2])

    @staticmethod
    def generate_series(plot):
        pt = plot.get_plot_type()
        if pt == PlotType.LINE_2D:
            return Line2DPlot(plot)
        elif pt == PlotType.PARAMETRIC_2D:
            return Parametric2DPlot(plot)
        elif pt == PlotType.IMPLICIT_2D:
            return Implicit2DPlot(plot)
        elif pt == PlotType.SURFACE:
            return SurfacePlot(plot)
        elif pt == PlotType.PARAMETRIC_3D:
            return Parametric3DLinePlot(plot)
        elif pt == PlotType.PARAMETRIC_SURFACE:
            return ParametricSurfacePlot(plot)
        elif pt == PlotType.CONTOUR:
            return ContourPlot(plot)
        raise ValueError("Unexpected plot type.")

class Line2DPlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        check = check_arguments([self._plot.get_body()], 1, 1)[0]
        self._series = LineOver1DRangeSeries(*check)

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim):
            self._series.start, self._series.end = xlim
            self._data.extend(self._series.get_segments())

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        self._expand_data(xlim, ylim, zlim)
        axis.add_collection(LineCollection(self._data, colors = self._plot.get_colour()))

class Parametric2DPlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        # TODO parametric, body should = (expr1, expr2)
        self._series = Parametric2DLineSeries(*(check_arguments(self._plot.get_body(), 2, 1)[0]))

    def draw(self, axis, xlim, ylim, zlim):
        # TODO parametric, fix range
        self._series.start = xlim[0]
        self._series.end = xlim[1]
        axis.add_collection(LineCollection(self._series.get_segments(),
            colors = self._plot.get_colour()))

class Implicit2DPlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)

        expr = self._plot.get_body()

        self._arg_list = []
        if isinstance(expr, BooleanFunction):
            def arg_expand(bool_expr):
                for arg in bool_expr.args:
                    if isinstance(arg, BooleanFunction):
                        arg_expand(arg)
                    elif isinstance(arg, Relational):
                        self._arg_list.append(arg)
            arg_expand(expr)

        has_equality = False
        if any(isinstance(e, (Equality, GreaterThan, LessThan)) for e in self._arg_list):
            has_equality = True
        elif not isinstance(expr, Relational):
            expr = sy.Eq(expr, 0)
            has_equality = True
        elif isinstance(expr, (Equality, GreaterThan, LessThan)):
            has_equality = True

        parser = Parser.get_instance()
        x = (parser.get_symbol_x(), -10, 10)
        y = (parser.get_symbol_y(), -10, 10)
        self._series = ImplicitSeries(expr, x, y, has_equality,
            True, 0, 300, self._plot.get_colour())

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim) or self._dy(ylim):
            self._series.start_x, self._series.end_x = xlim
            self._series.start_y, self._series.end_y = ylim
            self._data.extend(_matplotlib_list(self._series.get_raster()[0]))

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        self._expand_data(xlim, ylim, zlim)
        axis.fill(*self._data, facecolor = self._plot.get_colour())

class SurfacePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        check = check_arguments([self._plot.get_body()], 1, 2)[0]
        self._series = SurfaceOver2DRangeSeries(*check)
        self.__contours = ContourPlot(plot, True)

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim) or self._dy(ylim): self._expand_mesh(xlim, ylim)

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        self._expand_data(xlim, ylim, zlim)
        if self._plot.get_equation().is_contoured():
            self.__contours.draw(axis, xlim, ylim, zlim)
        else:
            axis.plot_surface(*self._get_mesh(xlim, ylim), color = self._plot.get_colour(),
                rstride = 1, cstride = 1, linewidth = 0.1)

class Parametric3DLinePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        # TODO parametric, body should be (expr1, expr2, expr3)
        check = check_arguments(self._plot.get_body(), 3, 1)[0]
        self._series = Parametric3DLineSeries(*check)

    def draw(self, axis, xlim, ylim, zlim):
        # TODO parametric, fix range
        self._series.start = xlim[0]
        self._series.end = xlim[1]
        axis.add_collection(Line3DCollection(self._series.get_segments(),
            colors = self._plot.get_colour()))

class ParametricSurfacePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        # TODO parametric, body should be (expr1, expr2, expr3)
        check = check_arguments(self._plot.get_body(), 3, 2)[0]
        self._series = ParametricSurfaceSeries(*check)
        self.__contours = ContourPlot(plot, True)

    def draw(self, axis, xlim, ylim, zlim):
        # TODO parametric, fix range
        self._series.start_u = xlim[0]
        self._series.end_u = xlim[1]
        self._series.start_v = ylim[0]
        self._series.end_v = ylim[1]
        if self._plot.get_equation().is_contoured():
            self.__contours.draw(axis, xlim, ylim, zlim)
        else:
            axis.plot_surface(*self._series.get_meshes(), color = self._plot.get_colour(),
                rstride = 1, cstride = 1, linewidth = 0.1)

class ContourPlot(HelixSeries):

    def __init__(self, plot, colour_shift = False):
        super().__init__(plot)
        self.__colour_shift = colour_shift
        self._series = ContourSeries(*(check_arguments([self._plot.get_body()], 1, 2)[0]))

    def draw(self, axis, xlim, ylim, zlim):
        self._series.start_x = xlim[0]
        self._series.end_x = xlim[1]
        self._series.start_y = ylim[0]
        self._series.end_y = ylim[1]
        c = self._plot.get_colour()
        if self.__colour_shift:
            r, g, b = c
            factor = 0.5
            if r + g + b / 3 < 0.5:
                r += (1 - r) * factor
                g += (1 - g) * factor
                b += (1 - b) * factor
            else:
                r *= factor
                g *= factor
                b *= factor
            c = (r, g, b)
        axis.contour(*self._series.get_meshes(), colors = [c])
