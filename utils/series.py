from abc import ABC, abstractmethod

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

class HelixSeries(ABC):

    def __init__(self, plot):
        self._plot = plot
        self._series = None
        self._data = []
        self._min_x = None
        self._max_x = None
        self._min_y = None
        self._max_y = None

    @abstractmethod
    def draw(self, axis, xlim, ylim, zlim):
        pass

    def _unbounded(self):
        return any([x is None for x in [self._min_x, self._max_x, self._min_y, self._max_y]])

    def get_plot(self):
        return self._plot

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

    def draw(self, axis, xlim, ylim, zlim):
        self._series.start = xlim[0]
        self._series.end = xlim[1]
        axis.add_collection(LineCollection(self._series.get_segments(),
            colors = self._plot.get_colour()))

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

    def __generate_area(self, x1, x2, y1, y2):
        self._series.start_x = x1
        self._series.end_x = x2
        self._series.start_y = y1
        self._series.end_y = y2
        self._data.extend(_matplotlib_list(self._series.get_raster()[0]))
    def draw(self, axis, xlim, ylim, zlim):
        if self._unbounded():
            self.__generate_area(*xlim, *ylim)
            self._min_x, self._max_x = xlim
            self._min_y, self._max_y = ylim
        else:
            if xlim[0] < self._min_x:
                self.__generate_area(xlim[0], self._min_x, self._min_y, self._max_y)
                self._min_x = xlim[0]
            if xlim[1] > self._max_x:
                self.__generate_area(self._max_x, xlim[1], self._min_y, self._max_y)
                self._max_x = xlim[1]
            if ylim[0] < self._min_y:
                self.__generate_area(self._min_x, self._max_x, ylim[0], self._min_y)
                self._min_y = ylim[0]
            if ylim[1] > self._max_y:
                self.__generate_area(self._min_x, self._max_x, self._max_y, ylim[1])
                self._max_y = ylim[1]
        axis.fill(*self._data, facecolor = self._plot.get_colour())

class SurfacePlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        check = check_arguments([self._plot.get_body()], 1, 2)[0]
        self._series = SurfaceOver2DRangeSeries(*check)

    def draw(self, axis, xlim, ylim, zlim):
        self._series.start_x = xlim[0]
        self._series.end_x = xlim[1]
        self._series.start_y = ylim[0]
        self._series.end_y = ylim[1]
        axis.plot_surface(*self._series.get_meshes(), color = self._plot.get_colour(),
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

    def draw(self, axis, xlim, ylim, zlim):
        # TODO parametric, fix range
        self._series.start_u = xlim[0]
        self._series.end_u = xlim[1]
        self._series.start_v = ylim[0]
        self._series.end_v = ylim[1]
        axis.plot_surface(*self._series.get_meshes(), color = self._plot.get_colour(),
            rstride = 1, cstride = 1, linewidth = 0.1)

class ContourPlot(HelixSeries):

    def __init__(self, plot):
        super().__init__(plot)
        self._series = ContourSeries(*(check_arguments([self._plot.get_body()], 1, 2)[0]))

    def draw(self, axis, xlim, ylim, zlim):
        self._series.start_x = xlim[0]
        self._series.end_x = xlim[1]
        self._series.start_y = ylim[0]
        self._series.end_y = ylim[1]
        axis.contour(*self._series.get_meshes(), colors = [self._plot.get_colour()])
