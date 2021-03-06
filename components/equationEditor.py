import ast

import tkinter as tk

from utils.theme import Theme
from utils.parsing import Parser
from utils.fonts import FontManager

from components.equation import Equation
from components.scrollableFrame import ScrollableFrame

class EquationDivider(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, height = 4)
        Theme.get_instance().configure_editor_divider(self)
        self.pack(fill = tk.BOTH, expand = True)

class EquationEditor(ScrollableFrame):

    EQUATION_KEY = "eq"

    def __init__(self, parent, width, plotter):
        super().__init__(parent, self.__entry_config)
        Theme.get_instance().configure_editor(self)
        Theme.get_instance().configure_editor(self.getCanvas())
        Theme.get_instance().configure_editor(self.getInnerFrame())

        self.__plotter = plotter

        self.__entry_width = None
        self.__entries = []
        self.__dividers = []

        self.__plots = []
        self.__bindings = []

        self.__add_button_height = 0.05

        self.place(relwidth = width,
            relheight = 1 - self.__add_button_height)

        self.__entry_button = tk.Button(parent,
            text = "+",
            command = self.__add_entry)
        Theme.get_instance().configure_editor_button(self.__entry_button)
        FontManager.get_instance().configure_text(self.__entry_button)
        self.__entry_button.place(
            rely = 1 - self.__add_button_height,
            relwidth = width,
            relheight = self.__add_button_height)

    def set_settings(self, settings):
        self.__clear_entries()
        for k in settings.keys():
            if isinstance(k, str) and k.startswith(EquationEditor.EQUATION_KEY):
                self.__add_entry(ast.literal_eval(settings[k]))
        for e in self.__entries: e.update()
        self.__update()
    def add_settings(self, settings):
        counter = 0
        for e in self.__entries:
            settings[EquationEditor.EQUATION_KEY + str(counter)] = str(e.get_settings())
            counter += 1

    def __add_entry(self, settings = None):
        eq = Equation(self.getInnerFrame(), self.__update, self.__remove_entry, settings)
        eq.configure(width = self.__entry_width)
        eq.div = EquationDivider(self.getInnerFrame())
        self.__dividers.append(eq.div)
        self.__entries.append(eq)
    def __clear_entries(self):
        for e in self.__entries + self.__dividers:
            e.pack_forget()
        self.__entries = []
        self.__dividers = []
        self.__update()
    def __remove_entry(self, entry):
        if entry.div is not None:
            entry.div.pack_forget()
            self.__dividers.remove(entry.div)
        self.__entries.remove(entry)
        self.__update(entry)
    def __entry_config(self, width):
        self.__entry_width = width
        for e in self.__entries:
            e.set_width(self.__entry_width)

    def __update(self, changed_eq = None):
        parser = Parser.get_instance()
        unbound = [None, parser.get_symbol_y(), parser.get_symbol_z()]

        if changed_eq is None:
            self.__bindings = []
            self.__plots = []
            unaffected = []
        else:
            prior = set([b for b in self.__bindings if b.get_equation() is changed_eq])
            prior_names = list(map(lambda b : b.get_name(), prior))
            def unaffected_check(b):
                symbols = b.get_raw_free_symbols()
                if not b.get_name() in unbound: symbols.add(b.get_name())
                no_prior = len(symbols.intersection(prior_names)) == 0
                return no_prior and not b.get_equation() is changed_eq
            self.__bindings = [b for b in self.__bindings if unaffected_check(b)]
            self.__plots = [b for b in self.__plots if unaffected_check(b)]
            unaffected = [b.get_equation() for b in self.__bindings + self.__plots]

        def rm_dupes(var):
            def _rm_dupes(b, v = var):
                rm = b.get_name() == v
                if rm: b.get_equation().label("Multiple definitions.")
                return rm
            return _rm_dupes

        bound = list(map(lambda b : b.get_name(), self.__bindings))
        for e in self.__entries:
            p = e.get_parsed()
            if e in unaffected:
                continue
            elif p is None:
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
                        self.__plots.append(bind)
                    else:
                        self.__bindings.append(bind)
                        if bind.get_name() in bound:
                            bound.remove(bind.get_name())
                            self.__bindings = list(filter(rm_dupes(bind.get_name()),
                                self.__bindings))
                        else:
                            bound.append(bind.get_name())
            else:
                raise ValueError("Unhandled Parsed state.")

        used = []
        while len(used) < len(self.__bindings):
            to_subst = [b for b in self.__bindings if not b in used and \
                len(b.get_free_symbols()) == 0]
            used.extend(to_subst)
            if len(to_subst) == 0:
                break
            for sub in to_subst:
                rm = []
                for bind in self.__bindings + self.__plots:
                    err = None
                    if sub.binds_func():
                        err = bind.replace(sub.get_name(), sub.get_body())
                    elif sub.binds_var():
                        err = bind.subs([(sub.get_name(), sub.get_body())])
                    else:
                        raise ValueError("Unexpected binding type.")
                    if err is not None:
                        bind.label(err)
                        rm.append(bind)
                self.__bindings = list(filter(lambda b : not b in rm, self.__bindings))
                self.__plots = list(filter(lambda b : not b in rm, self.__plots))

        for b in [b for b in self.__bindings if not b in used]:
            b.label("Unresolvable.")
        self.__bindings = used

        for p in self.__plots:
            fv = p.get_free_symbols()
            if len(fv) == 0:
                p.label(str(p))
            else:
                p.label("Unbound: " + str(fv))
        self.__plots = list(filter(lambda p : len(p.get_free_symbols()) == 0, self.__plots))

        plot_entries = list(map(lambda p : p.get_equation(), self.__plots))
        for e in self.__entries:
            e.set_plottable(e in plot_entries)
        self.__plotter(list(filter(lambda p : not p.get_equation().is_hidden(), self.__plots)))
