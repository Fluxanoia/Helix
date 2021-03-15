### Code adapted from:
### http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387

import tkinter as tk

from utils.theme import Theme

class Tooltip(object):

    def __init__(self, parent):
        self.__text = ""
        self.__window = None
        self.__label = None

        self.__parent = parent
        self.__parent.bind('<Enter>', self.__show)
        self.__parent.bind('<Leave>', self.__hide)

    def __show(self, _e = None):
        if not self.__window is None:
            self.__hide()
        x1, y1, _, y2 = self.__parent.bbox("insert")
        x1 += self.__parent.winfo_rootx() + 27
        y1 += self.__parent.winfo_rooty() + 27 + y2
        self.__window = tk.Toplevel(self.__parent)
        self.__window.wm_overrideredirect(1)
        self.__window.wm_geometry("+%d+%d" % (x1, y1))
        try:
            self.__window.tk.call("::tk::unsupported::MacWindowStyle",
                "style", self.__window._w, "help", "noActivates")
        except tk.TclError:
            pass
        self.__label = tk.Label(self.__window, text = self.__text, justify = tk.LEFT,
            relief = tk.SOLID, borderwidth = 1)
        Theme.get_instance().configure_tooltip_label(self.__label)
        self.__label.pack(ipadx = 1)

    def __hide(self, _e = None):
        w = self.__window
        self.__window = None
        if not w is None: w.destroy()

    def set_text(self, text):
        self.__text = "" if text is None else text
        if not self.__window is None: self.__show()
