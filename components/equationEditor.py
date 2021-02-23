import tkinter as tk

from utils.theme import Theme
from utils.parsing import Parser, Parsed
from utils.fonts import FontManager

from components.equation import Equation
from components.scrollableFrame import ScrollableFrame

class EquationDivider(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, height = 4)
        Theme.get_instance().configureEditorDivider(self)
        self.pack(fill = tk.BOTH, expand = True)

class EquationEditor(ScrollableFrame):

    # Plotting
    __plotter = None

    # Entries
    __entry_width = None
    __entry_button = None
    __entries = []
    __dividers = []

    # Placement
    __add_button_height = 0.05

    def __init__(self, parent, width, plotter):
        super().__init__(parent, self.__entry_config)
        Theme.get_instance().configureEditor(self)
        Theme.get_instance().configureEditor(self.getCanvas())
        Theme.get_instance().configureEditor(self.getInnerFrame())

        self.__plotter = plotter

        self.place(relwidth = width,
            relheight = 1 - self.__add_button_height)

        self.__entry_button = tk.Button(parent,
            text = "+",
            command = self.__add_entry)
        Theme.get_instance().configureEditorButton(self.__entry_button)
        FontManager.get_instance().configureText(self.__entry_button)
        self.__entry_button.place(
            rely = 1 - self.__add_button_height,
            relwidth = width,
            relheight = self.__add_button_height)

        #self.__add_entry("f(x) = x^2 + 1")
        #self.__add_entry("a = 3")
        #self.__add_entry("f(x)")
        #self.__add_entry("f(x / a)")
        #self.__add_entry("g(x, y) = sin(x) + cos(y)")
        #self.__add_entry("g(x, y)")

    def __add_entry(self, text = None):
        eq = Equation(self.getInnerFrame(), self.__update, self.__remove_entry)
        eq.div = EquationDivider(self.getInnerFrame())
        self.__dividers.append(eq.div)
        self.__entries.append(eq)
        self.__entries[-1].configure(width = self.__entry_width)
        if text is not None:
            self.__entries[-1].force_text(text)

    def __remove_entry(self, entry):
        if entry.div is not None:
            entry.div.pack_forget()
            self.__dividers.remove(entry.div)
        self.__entries.remove(entry)
        self.__update()

    def __entry_config(self, width):
        self.__entry_width = width
        for e in self.__entries:
            e.set_width(self.__entry_width)

    def __update(self):
        bound = []
        plots = []
        bindings = []
        parser = Parser.get_instance()
        unbound = [None, parser.get_symbol_y(), parser.get_symbol_z()]

        def rm_dupes_gen(var):
            def rm_dupes(b, v = var):
                rm = b[0] == v
                if rm: b[2].label("Multiple definitions.")
                return rm
            return rm_dupes

        for e in self.__entries:
            p = e.get_parsed()
            if p is None:
                e.label("Empty.")
                continue
            p.reset()
            if p.has_error():
                e.label(p.get_error())
            elif p.has_binding():
                bind = p.get_binding()
                if bind.get_name() is None and bind.get_plot_type() is None:
                    e.label(str(bind.get_body()))
                else:
                    e.label(str(bind))
                    if bind.get_name() in unbound:
                        plots.append(bind)
                    else:
                        bindings.append(bind)
                        if bind.get_name() in bound:
                            bound.remove(bind.get_name())
                            bindings = list(filter(rm_dupes_gen(bind.get_name()), bindings))
                        else:
                            bound.append(bind.get_name())
            else:
                raise ValueError("Unhandled Parsed state.")

        while len(bindings) > 0:
            done = []
            for b in bindings:
                if len(b.get_free_symbols()) == 0:
                    done.append(b)
            if len(done) == 0: break
            for d in done:
                bindings.remove(d)
                rm = []
                for x in bindings + plots:
                    err = None
                    if d.binds_func():
                        err = x.replace(d.get_name(), d.get_body())
                    elif d.binds_var():
                        err = x.subs([(d.get_name(), d.get_body())])
                    else:
                        raise ValueError("Unexpected binding type.")
                    if err is not None:
                        x.eq.label(err)
                        rm.append(x)
                for r in rm:
                    if r in bindings: bindings.remove(r)
                    if r in plots: plots.remove(r)

        for (_, _, e) in bindings:
            e.label("Unresolvable.")
        for p in plots:
            fv = p.get_free_symbols()
            if len(fv) == 0:
                p.label(str(p))
            else:
                p.label("Unbound: " + str(fv))

        plots = list(filter(lambda p : len(p.get_free_symbols()) == 0, plots))
        plot_entries = list(map(lambda p : p.get_equation(), plots))
        for e in self.__entries:
            e.set_plottable(e in plot_entries)
        plots = list(filter(lambda p : not p.get_equation().is_hidden(), plots))
        self.__plotter(plots)
