import matplotlib as mpl
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sympy import Expr, sympify
from sympy.plotting.plot import _matplotlib_list, check_arguments, \
    LineOver1DRangeSeries

from utils.theme import Theme

class HelixPlot(FigureCanvasTkAgg):

    __figure = mpl.figure.Figure()
    __axis = None

    __data = []

    __is_lambda = lambda f : lambda *x : all(getattr(i, f, True) for i in x)
    __is_real = __is_lambda('is_real')
    __is_finite = __is_lambda('is_finite')

    __xlim = (-10, 10)
    __ylim = (-10, 10)

    def __init__(self, parent, press_func, drag_func):
        super().__init__(self.__figure, master = parent)
        Theme.getInstance().configureFigure(self.__figure)

        def presser(e):
            self.get_tk_widget().focus_set()
            press_func(e)

        def dragger(e):
            x, y = drag_func(e)
            self.set_limits(x, y)

        self.get_tk_widget().bind("<ButtonPress-1>", presser)
        self.get_tk_widget().bind("<B1-Motion>", dragger)

    def widget(self):
        return self.get_tk_widget()

    def set_limits(self, xlim, ylim):
        if not (self.__is_real(xlim) and self.__is_real(ylim)):
            raise ValueError("Non-real limits in HelixPlot.")
        if not (self.__is_finite(xlim) and self.__is_finite(ylim)):
            raise ValueError("Infinite limits in HelixPlot.")
        self.__xlim = xlim
        self.__ylim = ylim
        self.redraw()

    def remove_plots(self):
        self.__data = []
        self.redraw()

    def set_plots(self, exprs):
        self.__data = []
        self.add_plots(exprs)

    def add_plots(self, exprs):
        if self.__axis is None:
            self.__axis = mpl.axes.Axes(self.__figure, (0, 0, 1, 1))
            Theme.getInstance().configurePlot2D(self.__axis)
            self.__figure.add_axes(self.__axis)
        if isinstance(self.__axis, Axes3D):
            raise ValueError("Cannot mix 2D and 3D in HelixPlot.")

        exprs = list(map(sympify, exprs))
        free = set()
        for a in filter(lambda a : isinstance(a, Expr), exprs):
            free |= a.free_symbols
            if len(free) > 1:
                raise ValueError("Too many free variables in HelixPlot.add_plot")
        self.__data.extend([(expr, LineOver1DRangeSeries(*expr)) \
            for expr in check_arguments(exprs, 1, 1)])

        self.redraw()
        # create plots, add to data
        # dimension checks, axis swaps
        # labels and colors ?

    def redraw(self):
        if self.__axis is not None: self.__axis.clear()

        for (_e, s) in self.__data:
            if s.is_2Dline:
                s.start = self.__xlim[0]
                s.end = self.__xlim[1]
                collection = mpl.collections.LineCollection(s.get_segments())
                self.__axis.add_collection(collection)
            elif s.is_contour:
                self.__axis.contour(*s.get_meshes())
            elif s.is_3Dline:
                collection = Line3DCollection(s.get_segments())
                self.__axis.add_collection(collection)
                x, y, z = s.get_points()
            elif s.is_3Dsurface:
                x, y, z = s.get_meshes()
                collection = self.__axis.plot_surface(x, y, z,
                    rstride = 1, cstride = 1, linewidth = 0.1)
            elif s.is_implicit:
                points = s.get_raster()
                if len(points) == 2:
                    x, y = _matplotlib_list(points[0])
                    self.__axis.fill(x, y, facecolor = s.line_color, edgecolor = 'None')
                else:
                    colormap = mpl.colors.ListedColormap(["white", s.line_color])
                    xarray, yarray, zarray, plot_type = points
                    if plot_type == 'contour':
                        self.__axis.contour(xarray, yarray, zarray, cmap = colormap)
                    else:
                        self.__axis.contourf(xarray, yarray, zarray, cmap = colormap)
            else: raise NotImplementedError("Unimplemented plot type in HelixPlot")

        if self.__axis is not None:
            self.__axis.spines['left'].set_position('center')
            self.__axis.spines['bottom'].set_position('center')
            self.__axis.set_xlim(self.__xlim)
            self.__axis.set_ylim(self.__ylim)
        self.draw()
