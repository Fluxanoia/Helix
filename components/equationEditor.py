import tkinter as tk

import sympy as sy

from utils.theme import Theme
from utils.parsing import Parser, Parsed
from utils.fonts import FontManager

from components.equation import Equation
from components.scrollableFrame import ScrollableFrame

class EquationEditor(ScrollableFrame):

    # Plotting
    __plotter = None

    # Entries
    __entry_width = None
    __entry_button = None
    __entries = []

    # Placement
    __add_button_height = 0.05

    def __init__(self, parent, width, plotter):
        super().__init__(parent, self.__entry_config)
        Theme.getInstance().configureEditor(self)
        Theme.getInstance().configureEditor(self.getCanvas())
        Theme.getInstance().configureEditor(self.getInnerFrame())

        self.__plotter = plotter

        self.place(relwidth = width,
            relheight = 1 - self.__add_button_height)

        self.__entry_button = tk.Button(parent,
            text = "+",
            command = self.__add_entry)
        Theme.getInstance().configureEditorButton(self.__entry_button)
        FontManager.getInstance().configureText(self.__entry_button)
        self.__entry_button.place(
            rely = 1 - self.__add_button_height,
            relwidth = width,
            relheight = self.__add_button_height)

        self.__add_entry()
        self.__entries[-1].force_text("x^2 + 1")

    def __add_entry(self):
        self.__entries.append(Equation(
            self.getInnerFrame(),
            self.__update,
            self.__remove_entry))
        self.__entries[-1].configure(width = self.__entry_width)

    def __remove_entry(self, entry):
        self.__entries.remove(entry)
        self.__update()

    def __entry_config(self, width):
        self.__entry_width = width
        for e in self.__entries:
            e.configure(width = self.__entry_width)

    def __update(self):
        parser = Parser.getInstance()

        bound = []
        bindings = []
        plottable = []

        def rm_dupes_gen(var):
            def rm_dupes(b, v = var):
                rm = b[0] == v
                if rm: b[2].label("Multiple definitions.")
                return rm
            return rm_dupes

        for e in self.__entries:
            p = e.get_parsed()
            if p is None: continue

            if p.has_binding():
                bind = p.get_binding()
                bind.eq = e
                if bind.name == parser.get_symbol_y():
                    plottable.append(Parsed(str(bind.body)))
                else:
                    bindings.append(bind)
                    if bind.name in bound:
                        bound.remove(bind.name)
                        bindings = list(filter(rm_dupes_gen(bind.name), bindings))
                    else:
                        bound.append(bind.name)
            elif p.has_dim():
                plottable.append(p)

        while len(bindings) > 0:
            done = []
            for b in bindings:
                if len(b.get_free_symbols()) == 0:
                    if len(b.get_xy_symbols()) == 0:
                        if b.is_func():
                            b.label("func_binding")
                        elif b.is_var():
                            b.label(b.body)
                        else:
                            raise ValueError("Unexpected binding type.")
                    done.append(b)
            if len(done) == 0: break
            for d in done:
                bindings.remove(d)
                for x in bindings + plottable:
                    if d.is_func():
                        x.replace(d.name, d.body)
                    elif d.is_var():
                        x.subs((d.name, d.body))
                    else:
                        raise ValueError("Unexpected binding type.")

        for (_, _, e) in bindings:
            e.label("Unresolvable.")

        plottable = list(filter(lambda p : len(p.get_free_symbols()) == 0, plottable))
        self.__plotter(plottable)
