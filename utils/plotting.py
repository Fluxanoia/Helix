import matplotlib as mpl
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from sympy.plotting.plot import _matplotlib_list, check_arguments, \
    LineOver1DRangeSeries, SurfaceOver2DRangeSeries

from utils.theme import Theme
from utils.parsing import Dimension

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
            check = check_arguments([p.get_blocks()[0]], 1, 1)[0]
            self.__data.append((check, LineOver1DRangeSeries(*check, line_color = p.colour)))

    def add_plots_3d(self, parsed):
        if self.__dim is not Dimension.THREE_D:
            raise ValueError("Incorrect plot dimension.")
        for p in parsed:
            check = check_arguments([p.get_blocks()[0]], 1, 2)[0]
            self.__data.append((check, SurfaceOver2DRangeSeries(*check, surface_color = p.colour)))

    def redraw(self):
        if self.__dim is None: return

        self.__axis.clear()

        for (_e, s) in self.__data:
            if not s.is_3D:
                s.start = self.__xlim[0]
                s.end = self.__xlim[1]
            else:
                s.start_x = self.__xlim[0]
                s.end_x = self.__xlim[1]
                s.start_y = self.__ylim[0]
                s.end_y = self.__ylim[1]

            if s.is_2Dline:
                collection = mpl.collections.LineCollection(s.get_segments(),
                    colors = s.line_color)
                self.__axis.add_collection(collection)
            elif s.is_contour:
                self.__axis.contour(*s.get_meshes())
            elif s.is_3Dline:
                collection = Line3DCollection(s.get_segments())
                self.__axis.add_collection(collection)
                x, y, z = s.get_points()
            elif s.is_3Dsurface:
                x, y, z = s.get_meshes()
                self.__axis.plot_surface(x, y, z, color = s.surface_color,
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
