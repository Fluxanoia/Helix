import math
from abc import ABC, abstractmethod

import numpy as np
import numpy.ma as ma

from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection

import sympy as sy
from sympy.plotting.plot import _matplotlib_list, check_arguments, \
    LineOver1DRangeSeries, SurfaceOver2DRangeSeries, \
    Parametric2DLineSeries, Parametric3DLineSeries, ParametricSurfaceSeries
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
        self._is_parametric = False

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

    def __safe_get_mesh(self):
        x, y, z = self._series.get_meshes()
        nx = ny = "nb_of_points_"
        if self._is_parametric:
            nx += 'x'
            ny += 'y'
        else:
            nx += 'u'
            ny += 'v'
        if not x.shape:
            x = x.max() * ma.ones((getattr(self._series, ny), getattr(self._series, nx)))
        if not y.shape:
            y = y.max() * ma.ones((getattr(self._series, ny), getattr(self._series, nx)))
        if not z.shape:
            z = z.max() * ma.ones((getattr(self._series, ny), getattr(self._series, nx)))
        return x, y, z
    def _expand_mesh(self, xlim, ylim):
        sx, ex, nx = "start_", "end_", "nb_of_points_"
        if self._is_parametric:
            x, y = 'x', 'y'
        else:
            x, y = 'u', 'v'
        sy_, ey, ny = sx + y, ex + y, nx + y
        sx, ex, nx = sx + x, ex + x, nx + x

        setattr(self._series, sx, xlim[0])
        setattr(self._series, ex, xlim[1])
        setattr(self._series, sy_, ylim[0])
        setattr(self._series, ey, ylim[1])
        if self.__unbounded():
            setattr(self._series, nx, math.ceil((xlim[1] - xlim[0]) * self._point_density))
            setattr(self._series, ny, math.ceil((ylim[1] - ylim[0]) * self._point_density))
            self._data = self.__safe_get_mesh()
        else:
            prepend_x = xlim[0] < self._min_x
            append_x = xlim[1] > self._max_x
            prepend_y = ylim[0] < self._min_y
            append_y = ylim[1] > self._max_y
            assert len([x for x in [prepend_x, append_x, prepend_y, append_y] if x]) == 1
            if prepend_x or append_x:
                setattr(self._series, nx, math.ceil((xlim[1] - xlim[0]) * self._point_density))
                setattr(self._series, ny, len(self._data[1]))
                x, y, z = self.__safe_get_mesh()
                if prepend_x:
                    x = np.concatenate((x, self._data[0]), axis = 1)
                    y = np.concatenate((y, self._data[1]), axis = 1)
                    z = ma.concatenate((z, self._data[2]), axis = 1)
                if append_x:
                    x = np.concatenate((self._data[0], x), axis = 1)
                    y = np.concatenate((self._data[1], y), axis = 1)
                    z = ma.concatenate((self._data[2], z), axis = 1)
            if prepend_y or append_y:
                setattr(self._series, nx, len(self._data[0][0]))
                setattr(self._series, ny, math.ceil((ylim[1] - ylim[0]) * self._point_density))
                x, y, z = self.__safe_get_mesh()
                if prepend_y:
                    x = np.concatenate((x, self._data[0]), axis = 0)
                    y = np.concatenate((y, self._data[1]), axis = 0)
                    z = ma.concatenate((z, self._data[2]), axis = 0)
                if append_y:
                    x = np.concatenate((self._data[0], x), axis = 0)
                    y = np.concatenate((self._data[1], y), axis = 0)
                    z = ma.concatenate((self._data[2], z), axis = 0)
            self._data = (x, y, z)
    def _get_mesh(self, xlim, ylim, zlim):
        (x, y, z) = self._data

        xi = [i for i, v in enumerate(x[0]) if v >= xlim[0] and v <= xlim[1]]
        yi = [i for i, v in enumerate(y) if v[0] >= ylim[0] and v[0] <= ylim[1]]
        x = x[yi[0]:yi[-1], xi[0]:xi[-1]]
        y = y[yi[0]:yi[-1], xi[0]:xi[-1]]
        z = z[yi[0]:yi[-1], xi[0]:xi[-1]]

        diff = (zlim[1] - zlim[0]) / 5
        cond = (z >= zlim[0] - diff) & (z <= zlim[1] + diff)
        x = np.where(cond, x, np.nan)
        y = np.where(cond, y, np.nan)
        z = np.where(cond, z, np.nan)
        return (x, y, z)

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
        self._series = Parametric2DLineSeries(*(check_arguments(self._plot.get_body(), 2, 1)[0]))

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim):
            self._series.start, self._series.end = xlim
            self._data.extend(self._series.get_segments())

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        tlim = self._plot.get_parametric_limits()[self._series.var]
        self._expand_data(tlim, ylim, zlim)
        axis.add_collection(LineCollection(self._data,
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

        x = (Parser.X, -10, 10)
        y = (Parser.Y, -10, 10)
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
        self._series = SurfaceOver2DRangeSeries(*check_arguments([self._plot.get_body()], 1, 2)[0])

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim) or self._dy(ylim): self._expand_mesh(xlim, ylim)

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        self._expand_data(xlim, ylim, zlim)
        if self._plot.get_equation().is_contoured():
            axis.contour(*self._get_mesh(xlim, ylim, zlim), colors = [self._plot.get_colour()])
        else:
            axis.plot_surface(*self._get_mesh(xlim, ylim, zlim), color = self._plot.get_colour(),
                rstride = 1, cstride = 1, linewidth = 0.1)

class Parametric3DLinePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        self._series = Parametric3DLineSeries(*check_arguments(self._plot.get_body(), 3, 1)[0])

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim):
            self._series.start, self._series.end = xlim
            self._data.extend(self._series.get_segments())

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        tlim = self._plot.get_parametric_limits()[self._series.var]
        self._expand_data(tlim, ylim, zlim)
        axis.add_collection(Line3DCollection(self._data,
            colors = self._plot.get_colour()))

class ParametricSurfacePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        self._series = ParametricSurfaceSeries(*check_arguments(self._plot.get_body(), 3, 2)[0])

    @overrides
    def _generate_data(self, xlim, ylim, zlim):
        if self._dx(xlim) or self._dy(ylim): self._expand_mesh(xlim, ylim)

    @overrides
    def draw(self, axis, xlim, ylim, zlim):
        ulim = self._plot.get_parametric_limits()[self._series.var_u]
        vlim = self._plot.get_parametric_limits()[self._series.var_v]
        self._expand_data(ulim, vlim, zlim)
        if self._plot.get_equation().is_contoured():
            axis.contour(*self._get_mesh(xlim, ylim, zlim), colors = [self._plot.get_colour()])
        else:
            axis.plot_surface(*self._get_mesh(xlim, ylim, zlim), color = self._plot.get_colour(),
                rstride = 1, cstride = 1, linewidth = 0.1)
