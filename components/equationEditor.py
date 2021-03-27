import ast

import tkinter as tk

from utils.theme import Theme
from utils.parsing import Parser

from components.equation import Equation, EquationLabelType
from components.scrollableFrame import ScrollableFrame

class EditorError(Exception):

    def __init__(self, m):
        self.__message = m
        super().__init__(self.__str__())

    def __str__(self):
        return str(self.__message)

class EquationDivider(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, height = 4)
        Theme.get_instance().configure_divider(self)
        self.pack(fill = tk.BOTH, expand = True)

class EquationEditor(ScrollableFrame):

    EQUATION_KEY = "eq"

    def __init__(self, parent, width, plotter, change_func):
        super().__init__(parent, self.__entry_config)
        theme = Theme.get_instance()
        theme.configure_editor(self)
        theme.configure_editor(self.get_canvas())
        theme.configure_editor(self.get_inner_frame())

        self.__plotter = plotter
        self.__change_func = change_func

        self.__entry_width = None
        self.__entries = []
        self.__dividers = []

        self.__plots = []
        self.__raw_plots = []
        self.__bindings = []

        self.__add_button_height = 0.05

        self.place(relwidth = width, relheight = 1 - self.__add_button_height)

        def entry_command():
            self.__add_entry()
            self.__update(self.__entries[-1])
        self.__entry_button = tk.Button(parent, text = "+", command = entry_command)
        theme.configure_button(self.__entry_button)
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
        self.__update(no_change = True)
    def add_settings(self, settings):
        counter = 0
        for e in self.__entries:
            settings[EquationEditor.EQUATION_KEY + str(counter)] = str(e.get_settings())
            counter += 1

    def __add_entry(self, settings = None):
        eq = Equation(self.get_inner_frame(), self.__update, self.__replot,
            self.__remove_entry, settings)
        eq.configure(width = self.__entry_width)
        eq.div = EquationDivider(self.get_inner_frame())
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

    def __update(self, changed_eq = None, no_change = False):
        unbound = [None, Parser.X, Parser.Y, Parser.Z]

        if changed_eq is None:
            self.__bindings = []
            self.__plots = []
            unaffected_eqs = []
        else:
            unaffected_eqs = []
            affected_names = []
            valid_name_check = lambda name : not name in unbound and not isinstance(name, tuple)
            for b in self.__bindings + self.__plots:
                if b.get_equation() is changed_eq:
                    name = b.get_name()
                    if valid_name_check(name): affected_names.append(name)
                else:
                    unaffected_eqs.append(b.get_equation())
            while len(unaffected_eqs) > 0:
                has_changed = False
                for b in self.__bindings + self.__plots:
                    if b.get_equation() not in unaffected_eqs:
                        continue
                    name = b.get_name()
                    symbols = b.get_free_symbols(True)
                    if valid_name_check(name): symbols.add(name)
                    if len(symbols.intersection(affected_names)) > 0:
                        has_changed = True
                        unaffected_eqs.remove(b.get_equation())
                        if valid_name_check(name):
                            affected_names.append(name)
                if not has_changed: break
            self.__bindings = [b for b in self.__bindings if b.get_equation() in unaffected_eqs]
            self.__plots = [b for b in self.__plots if b.get_equation() in unaffected_eqs]

        def rm_dupes(var):
            def _rm_dupes(b, v = var):
                rm = b.get_name() == v
                if rm: b.get_equation().label(EquationLabelType.ERROR, "Multiple definitions.")
                return rm
            return _rm_dupes

        bound = list(map(lambda b : b.get_name(), self.__bindings))
        for e in self.__entries:
            p = e.get_parsed()
            if e in unaffected_eqs:
                continue
            p.reset()
            if p.has_error():
                e.label(EquationLabelType.ERROR, p.get_error())
            elif p.has_binding():
                bind = p.get_binding()
                if bind.get_name() is None and bind.get_plot_type() is None:
                    e.label(EquationLabelType.VALUE, str(bind.get_body()))
                else:
                    e.label(EquationLabelType.VALUE, str(bind))
                    if bind.get_name() in unbound or isinstance(bind.get_name(), tuple):
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
                raise EditorError("Unhandled Parsed state.")

        used = []
        while len(used) < len(self.__bindings):
            to_subst = [b for b in self.__bindings if not b in used and \
                len(b.get_free_symbols()) == 0]
            used.extend(to_subst)
            if len(to_subst) == 0:
                break
            for sub in to_subst:
                subst = [(sub.get_name(), sub.get_body())]
                for bind in list(self.__bindings + self.__plots):
                    if sub == bind: continue
                    try:
                        if sub.binds_func():
                            bind.replace(subst)
                        elif sub.binds_var():
                            bind.subs(subst)
                        else:
                            raise EditorError("Unexpected binding type.")
                        if len(bind.get_free_symbols()) == 0: bind.default_ops()
                    except Exception as e:
                        bind.label(EquationLabelType.ERROR, str(e))
                        if bind in self.__bindings: self.__bindings.remove(bind)
                        if bind in self.__plots: self.__plots.remove(bind)

        for b in self.__bindings:
            if not b in used: b.label(EquationLabelType.ERROR, "Unresolvable.")
        self.__bindings = used

        for p in self.__plots:
            fv = p.get_free_symbols()
            if len(fv) > 0:
                p.label(EquationLabelType.ERROR, "Unbound: " + str(fv))
            elif not p.is_valid():
                p.label(EquationLabelType.ERROR, "Invalid atoms.")
            else:
                p.get_equation().label()
        self.__raw_plots = list(filter(lambda p : p.is_valid() \
            and len(p.get_free_symbols()) == 0, self.__plots))

        self.__replot(no_change = True)
        if not no_change: self.__change_func()
    def __replot(self, no_change = False):
        self.__plots = self.__raw_plots
        plot_entries = list(map(lambda p : p.get_equation(), self.__plots))
        for e in self.__entries:
            e.set_state(e in plot_entries)
        def plot_allowed(p):
            eq = p.get_equation()
            return not eq.is_hidden() and not eq.has_cancelled_plot()
        self.__plotter(list(filter(plot_allowed, self.__plots)))
        if not no_change: self.__change_func()
