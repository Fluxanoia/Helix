import tkinter as tk

class ScrollableFrame(tk.Frame):

    __config = None

    __canvas = None
    __scroll = None
    __frame = None

    __active_scroll = False

    def __init__(self, parent, config, **args):
        super().__init__(parent, args)
        self.__config = config
        self.__canvas = tk.Canvas(self, args)
        self.__frame = tk.Frame(self.__canvas, args)
        self.__scroll = tk.Scrollbar(self, command = self.__canvas.yview)
        self.__canvas.configure(yscrollcommand = self.__scrollSet)

        self.__canvas.pack(fill = tk.BOTH, expand = True)
        self.__canvas.create_window((0, 0), window = self.__frame, anchor = tk.NW)

        self.bind("<Configure>", self.__onConfigure)
        self.bind('<Enter>', self.__bind_scroll)
        self.bind('<Leave>', self.__unbind_scroll)
        self.__frame.bind("<Configure>", self.onFrameConfigure)

    def __scrollSet(self, lo, hi):
        self.__active_scroll = float(lo) > 0.0 or float(hi) < 1.0
        if self.__active_scroll:
            self.__scroll.place(
                x = self.winfo_width() - self.__scroll.winfo_width(),
                relheight = 1)
        else:
            self.__scroll.place_forget()
        self.__onConfigure(None)
        self.__scroll.set(lo, hi)

    def __onConfigure(self, _event):
        width = self.winfo_width()
        if self.__active_scroll:
            width -= self.__scroll.winfo_width()
        self.__config(width)

    def onFrameConfigure(self, _event):
        self.__canvas.configure(scrollregion = self.__canvas.bbox(tk.ALL))

    def __bind_scroll(self, _event):
        self.__canvas.bind_all("<MouseWheel>", self.__mouse_scroll)
        self.__canvas.bind_all("<Button-4>", self.__mouse_scroll)
        self.__canvas.bind_all("<Button-5>", self.__mouse_scroll)

    def __unbind_scroll(self, _event):
        self.__canvas.unbind_all("<MouseWheel>")
        self.__canvas.unbind_all("<Button-4>")
        self.__canvas.unbind_all("<Button-5>")

    def __mouse_scroll(self, event):
        if not self.__active_scroll:
            return
        self.__canvas.yview_scroll(1 if event.num == 5 or event.delta < 0 else -1, tk.UNITS)

    def getInnerFrame(self):
        return self.__frame

    def getCanvas(self):
        return self.__canvas
