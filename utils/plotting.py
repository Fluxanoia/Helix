from sympy.plotting.plot import Plot, MatplotlibBackend, \
    plot, plot_parametric, plot3d, plot3d_parametric_line, plot3d_parametric_surface

class HelixPlot(Plot):

    def __init__(self):
        super().__init__(backend = HelixBackend)

    def plot(self, *args, **kwargs):
        self.extend(plot(*args, show = False, **kwargs))
    def plot_parametric(self, *args, **kwargs):
        self.extend(plot_parametric(*args, show = False, **kwargs))
    def plot3d(self, *args, **kwargs):
        self.extend(plot3d(*args, show = False, **kwargs))
    def plot3d_parametric_line(self, *args, **kwargs):
        self.extend(plot3d_parametric_line(*args, show = False, **kwargs))
    def plot3d_parametric_surface(self, *args, **kwargs):
        self.extend(plot3d_parametric_surface(*args, show = False, **kwargs))

    def getFigure(self):
        return self._backend.fig

class HelixBackend(MatplotlibBackend):

    def show(self): self.process_series()

    def save(self, path):
        self.process_series()
        self.fig.savefig(path)

    def close(self):
        pass
