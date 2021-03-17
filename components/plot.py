import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.axes3d import Axes3D

from utils.theme import Theme
from utils.delay import DelayTracker
from utils.maths import Dimension
from utils.series import HelixSeries

class HelixPlot(FigureCanvasTkAgg):

    def __init__(self, parent, press_func, drag_func, zoom_func):
        super().__init__(mpl.figure.Figure(), master = parent)

        self.__axis = None

        self.__data = []

        self.__xlim = (-10, 10)
        self.__ylim = (-10, 10)
        self.__zlim = (-10, 10)

        self.__elev = 30
        self.__azim = -60

        self.__debounce_id = None
        self.__debounce_delay = 300

        self.__dim = None

        self.__figure = self.figure
        Theme.get_instance().configure_figure(self.__figure)

        self.__axis2 = mpl.axes.Axes(self.__figure, (0, 0, 1, 1))
        Theme.get_instance().configure_plot_2d(self.__axis2)

        self.__axis3 = Axes3D(self.__figure, (0, 0, 1, 1))
        Theme.get_instance().configure_plot_3d(self.__axis3)

        self.__axis2.set_xlim(self.__xlim)
        self.__axis2.set_ylim(self.__ylim)
        self.__axis3.set_xlim(self.__xlim)
        self.__axis3.set_ylim(self.__ylim)
        self.__axis3.set_zlim(self.__zlim)

        def presser(e):
            self.widget().focus_set()
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

        self.widget().bind("<ButtonPress-1>", self.__presser)
        self.widget().bind("<B1-Motion>", self.__dragger)
        self.widget().bind('<Enter>', self.__bind_scroll)
        self.widget().bind('<Leave>', self.__unbind_scroll)

        self.draw()

    def widget(self):
        return self.get_tk_widget()
    def __bind_scroll(self, _event):
        self.widget().bind_all("<MouseWheel>", self.__zoomer)
        self.widget().bind_all("<Button-4>", self.__zoomer)
        self.widget().bind_all("<Button-5>", self.__zoomer)
    def __unbind_scroll(self, _event):
        self.widget().unbind_all("<MouseWheel>")
        self.widget().unbind_all("<Button-4>")
        self.widget().unbind_all("<Button-5>")

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
        self.__limit_plot()
    def set_limits(self, xlim, ylim, zlim = None):
        self.__xlim = xlim
        self.__ylim = ylim
        if not zlim is None: self.__zlim = zlim
        self.redraw(False)
        self.__debounce_redraw()
    def set_view(self, elev, azim):
        self.__elev = elev
        self.__azim = azim
        self.redraw(False)
        self.__debounce_redraw()
    def set_plots(self, plots, dim):
        if self.__dim is not dim:
            raise ValueError("Incorrect plot dimension.")
        input_sigs = list(map(lambda s : s.get_signature(), plots))
        to_remove = [d for d in self.__data if d.get_signature() not in input_sigs]
        self.__data = [d for d in self.__data if not d in to_remove]
        current_sigs = list(map(lambda s : s.get_signature(), self.__data))
        plots = [p for p in plots if p.get_signature() not in current_sigs]
        for p in plots:
            self.__data.extend([HelixSeries.generate_series(p) for p in p.split()])
        # existing_plots = list(map(lambda d : d.get_plot(), self.__data))
        # to_remove = [p for p in self.__data if not p.get_plot() in plots]
        # self.__data = [d for d in self.__data if not d in to_remove]
        # plots = [p for p in plots if not p in existing_plots]
        # self.__data.extend([HelixSeries.generate_series(p) for p in plots])

    def __debounce_redraw(self):
        if self.__debounce_id is not None:
            DelayTracker.get_instance().end_delay(self.widget(), self.__debounce_id)
        self.__debounce_id = self.widget().after(self.__debounce_delay, self.redraw)
        DelayTracker.get_instance().add_delay(self.widget(), self.__debounce_id)
    def redraw(self, replot = True):
        if self.__dim is None: return
        if replot:
            DelayTracker.get_instance().remove_delay(self.widget(), self.__debounce_id)
            self.__debounce_id = None
            self.__axis.clear()
            for p in self.__data: p.draw(self.__axis, self.__xlim, self.__ylim, self.__zlim)
        self.__limit_plot()
        self.draw()
    def __limit_plot(self):
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
