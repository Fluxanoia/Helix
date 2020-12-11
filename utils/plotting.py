import tkinter as tk

from matplotlib.backends._backend_tk import FigureCanvasTk, blit
from matplotlib.backends.backend_agg import FigureCanvasAgg

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

class HelixCanvasBase(FigureCanvasTk):

    def __init__(self, figure, master=None, resize_callback=None):
        super(FigureCanvasTk, self).__init__(figure)
        self._idle = True
        self._idle_callback = None
        w, h = self.figure.bbox.size.astype(int)
        self._tkcanvas = tk.Canvas(
            master = master, background="white",
            width = w, height = h, borderwidth = 0,
            highlightthickness = 0)
        self._tkphoto = tk.PhotoImage(
            master = self._tkcanvas, width = w, height = h)
        self._tkcanvas.create_image(w // 2, h // 2, image = self._tkphoto)
        self._resize_callback = resize_callback
        self._tkcanvas.bind("<Configure>", self.resize)
        self._tkcanvas.bind("<Key>", self.key_press)
        self._tkcanvas.bind("<Motion>", self.motion_notify_event)
        self._tkcanvas.bind("<Enter>", self.enter_notify_event)
        self._tkcanvas.bind("<Leave>", self.leave_notify_event)
        self._tkcanvas.bind("<KeyRelease>", self.key_release)
        for name in ["<Button-1>", "<Button-2>", "<Button-3>"]:
            self._tkcanvas.bind(name, self.button_press_event)
        for name in [
                "<Double-Button-1>", "<Double-Button-2>", "<Double-Button-3>"]:
            self._tkcanvas.bind(name, self.button_dblclick_event)
        for name in [
                "<ButtonRelease-1>", "<ButtonRelease-2>", "<ButtonRelease-3>"]:
            self._tkcanvas.bind(name, self.button_release_event)

        for name in "<Button-4>", "<Button-5>":
            self._tkcanvas.bind(name, self.scroll_event)

        root = self._tkcanvas.winfo_toplevel()
        root.bind("<MouseWheel>", self.scroll_event_windows, "+")

        def filter_destroy(event):
            if event.widget is self._tkcanvas:
                self._master.update_idletasks()
                self.close_event()
        root.bind("<Destroy>", filter_destroy, "+")

        self._master = master

class HelixCanvas(FigureCanvasAgg, HelixCanvasBase):

    def draw(self):
        super().draw()
        blit(self._tkphoto, self.renderer._renderer, (0, 1, 2, 3))
        self._master.update_idletasks()

    def blit(self, bbox = None):
        blit(self._tkphoto, self.renderer._renderer,
            (0, 1, 2, 3), bbox = bbox)
        self._master.update_idletasks()
