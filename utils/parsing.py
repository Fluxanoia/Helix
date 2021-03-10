import copy

import numpy as np
import sympy as sy
from sympy.integrals import Integral
from sympy.core.function import UndefinedFunction, AppliedUndef, Derivative
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, \
    function_exponentiation, convert_xor, convert_equals_signs
from sympy.core.relational import Relational, GreaterThan, LessThan, StrictGreaterThan, \
    StrictLessThan, Equality, Unequality
from sympy.logic.boolalg import BooleanFunction
from sympy.core.compatibility import exec_

from utils.maths import PlotType

class Parser:

    __instance = None

    @staticmethod
    def get_instance():
        if Parser.__instance is None:
            raise Exception("No instance of Parser.")
        return Parser.__instance

    def __init__(self):
        if Parser.__instance is not None:
            raise Exception("Invalid initialistion of Parser.")
        Parser.__instance = self
        self.__x, self.__y, self.__z = sy.symbols('x y z')
        self.__transformations = standard_transformations \
            + (function_exponentiation, convert_xor, convert_equals_signs)

        self.__global_dict = {}
        exec_('from sympy.core import *', self.__global_dict)
        exec_('from sympy.functions import *', self.__global_dict)
        exec_('from sympy.integrals import *', self.__global_dict)
        exclusions = ['sympify', 'SympifyError', 'Subs', 'evalf', 'evaluate']
        for e in exclusions: self.__global_dict.pop(e)

        self.__invalid_atoms = (Derivative, Integral)

        e, pi = sy.symbols('e pi')
        self.__default_subs = [(e, np.exp(1)), (pi, np.pi)]
        self.__default_repl = [
            (lambda e : isinstance(e, sy.Function) and e.name == 'int',
                lambda e : Integral(*e.args)),
            (lambda x : isinstance(x, (Derivative, Integral)),
                lambda e : e.doit())]

    def default_binds(self, expr):
        try:
            expr = expr.subs(self.__default_subs)
            for (f, t) in self.__default_repl:
                expr = expr.replace(f, t)
        except Exception as e:
            return str(e)
        return expr
        
    def has_invalid_atoms(self, expr):
        return len(expr.atoms(*self.__invalid_atoms)) > 0

    def args(self, raw_expr):
        def _args(expr):
            if not isinstance(expr, Relational):
                return [expr]
            args = []
            for arg in expr.args:
                args.extend(_args(arg))
            return args
        return _args(raw_expr)
    def get_symbols(self, exprs):
        if not isinstance(exprs, list): exprs = [exprs]
        symbols = set()
        for expr in exprs:
            try:
                symbols = symbols.union(set(expr.free_symbols))
                symbols = symbols.union(set(expr.atoms(AppliedUndef)))
            except:
                continue
        return list(symbols)
    def get_xy_symbols(self, exprs):
        return list(filter(lambda s : s in self.get_default_symbols(),
            self.get_symbols(exprs)))
    def get_free_symbols(self, exprs):
        return list(filter(lambda s : not (s in self.get_default_symbols()),
            self.get_symbols(exprs)))

    def parse(self, expr):
        return parse_expr(expr, global_dict = self.__global_dict,
            transformations = self.__transformations)

    def get_symbol_x(self):
        return self.__x
    def get_symbol_y(self):
        return self.__y
    def get_symbol_z(self):
        return self.__z
    def get_default_symbols(self):
        return [self.__x, self.__y]

class Binding:

    def __init__(self, name, body, plot_type):
        self.__name = name
        self.__body = body
        self.__plot_type = plot_type
        self.__dependencies = set()
        self.__equation = None
        self.__colour = None

    def subs(self, substitutions):
        try:
            for (old, new) in substitutions:
                if old in self.get_free_symbols():
                    self.__body = self.__body.subs(old, new)
                    self.__dependencies.add(old)
        except Exception as e:
            return str(e)
        return None
    def replace(self, old, new):
        try:
            if any(map(lambda v : isinstance(v, old), self.get_free_symbols())):
                self.__body = self.__body.replace(old, new)
                self.__dependencies.add(old)
        except Exception as e:
            return str(e)
        return None

    def default_binds(self):
        db = Parser.get_instance().default_binds(self.__body)
        if not isinstance(db, str):
            self.__body = db
            return None
        return db
        
    def is_valid(self):
        return not Parser.get_instance().has_invalid_atoms(self.__body)

    def label(self, text):
        self.__equation.label(text)

    def get_symbols(self):
        return Parser.get_instance().get_free_symbols(self.get_body())
    def get_xy_symbols(self):
        parser = Parser.get_instance()
        return list(filter(lambda s : s in parser.get_default_symbols(),
            self.get_symbols()))
    def get_free_symbols(self):
        parser = Parser.get_instance()
        return list(filter(lambda s : not (s in parser.get_default_symbols()),
            self.get_symbols()))
    def get_raw_free_symbols(self):
        return self.__dependencies.union(set(self.get_free_symbols()))

    def binds_var(self):
        return isinstance(self.__name, sy.Symbol)
    def binds_func(self):
        return isinstance(self.__name, UndefinedFunction)

    def get_name(self):
        return self.__name
    def get_body(self):
        return self.__body
    def get_dependencies(self):
        return self.__dependencies
    def get_plot_type(self):
        return self.__plot_type
    def get_equation(self):
        return self.__equation
    def set_equation(self, equation):
        self.__equation = equation
    def get_colour(self):
        return self.__colour
    def set_colour(self, colour):
        self.__colour = colour

    def __str__(self):
        if self.__name is None:
            if isinstance(self.__body, Relational):
                op_dict = {
                    GreaterThan : ">=",
                    LessThan : "<=",
                    StrictGreaterThan : ">",
                    StrictLessThan : "<",
                    Equality : "=",
                    Unequality : "/="
                }
                return str(self.__body.lhs) + " " + op_dict[type(self.__body)] \
                    + " " + str(self.__body.rhs)
            else:
                return str(self.__body)
        else:
            return str(self.__name) + " = " + str(self.__body)

class Parsed:

    def __init__(self, raw):
        self.__raw_expr = None
        self.__raw_args = None
        self.__raw_relation = None
        self.__is_parametric = False

        self.__raw_binding = None
        self.__raw_error = None

        self.__binding = None
        self.__error = None

        self.__eval(raw)
        if not self.__raw_binding is None and self.__raw_error is None:
            self.__raw_error = self.__raw_binding.default_binds()
        self.reset()

    def __eval(self, raw):
        # Gather raw data
        self.__raw = raw
        if len(raw) == 0:
            self.__raw_error = "Empty."
            return
        parser = Parser.get_instance()
        try:
            self.__raw_expr = parser.parse(self.__raw)
        except Exception as e:
            self.__raw_error = str(e)
            return
        if isinstance(self.__raw_expr, tuple):
            self.__is_parametric = True
            self.__raw_args = list(self.__raw_expr)
        else:
            self.__raw_args = parser.args(self.__raw_expr)
        # Check for valid relational usage
        lt = [LessThan, StrictLessThan]
        gt = [GreaterThan, StrictGreaterThan]
        def valid_structure(raw_expr):
            def _valid_structure(expr):
                if isinstance(expr, BooleanFunction): return False
                if isinstance(expr, Unequality): return False
                if isinstance(expr, Relational):
                    expr_type = type(expr)
                    if self.__raw_relation is None:
                        self.__raw_relation = expr_type
                    else:
                        comps = set(self.__raw_relation, expr_type)
                        if not all(c in lt for c in comps) and \
                            not all(c in gt for c in comps) and \
                            not (expr_type == self.__raw_relation and expr_type == Equality):
                            return False
                    return all(map(_valid_structure, expr.args))
                return True
            return _valid_structure(raw_expr)
        if not valid_structure(self.__raw_expr):
            self.__raw_error = "Invalid relations."
            return
        if len(self.__raw_args) > 2:
            self.__raw_error = "Too many relations."
            return
        # Evaluate the args
        xy = parser.get_xy_symbols(self.__raw_args)
        fv = parser.get_free_symbols(self.__raw_args)
        if len(self.__raw_args) == 1:
            if self.__is_parametric:
                pass # TODO parametric
            elif len(xy) == 0:
                try:
                    self.__bind(parser.get_symbol_y(), self.__raw_args[0].evalf(),
                        PlotType.LINE_2D)
                except Exception as e:
                    self.__raw_error = str(e)
            elif len(xy) == 1:
                if xy[0] == parser.get_symbol_x():
                    self.__bind(parser.get_symbol_y(), self.__raw_args[0], PlotType.LINE_2D)
            elif len(xy) == 2:
                self.__bind(parser.get_symbol_z(), self.__raw_args[0], PlotType.SURFACE)
        elif len(self.__raw_args) == 2:
            if self.__is_parametric:
                pass # TODO parametric
            elif isinstance(self.__raw_relation,
                (GreaterThan, LessThan, StrictGreaterThan, StrictLessThan)):
                if callable(self.__raw_relation):
                    self.__bind(None, self.__raw_relation(self.__raw_args[0], self.__raw_args[1]),
                        PlotType.IMPLICIT_2D)
                else:
                    raise ValueError("Uncallable relation.")
            elif isinstance(self.__raw_args[0], sy.Function):
                if hasattr(self.__raw_args[0], 'name'):
                    args = self.__raw_args[0].args
                    if any([not isinstance(a, sy.Symbol) for a in args]):
                        self.__raw_error = "Function arguments must be Symbols."
                    else:
                        if len(args) == len(set(args)):
                            self.__bind(sy.Function(self.__raw_args[0].name),
                                sy.Lambda(args, self.__raw_args[1]), None)
                        else:
                            self.__raw_error = "Duplicate parameters."
                else:
                    self.__raw_error = "Multiple definitions."
            elif parser.get_symbol_y() in xy:
                try:
                    self.__bind(None, sy.Eq(self.__raw_args[0], self.__raw_args[1]),
                        PlotType.IMPLICIT_2D)
                except:
                    self.__raw_error = "Unsolvable."
            elif parser.get_symbol_x() in xy:
                try:
                    self.__bind(None, list(sy.solveset(
                        sy.Eq(self.__raw_args[0], self.__raw_args[1]),
                        parser.get_symbol_x(), domain = sy.S.Reals)), None)
                except Exception as e:
                    self.__raw_error = str(e)
            elif len(fv) == 0:
                self.__bind(None, sy.Eq(self.__raw_args[0], self.__raw_args[1]), None)
            else:
                lhs_fv = list(filter(lambda s : not (s in parser.get_default_symbols()),
                    parser.get_free_symbols(self.__raw_args[0])))
                if len(lhs_fv) == 1:
                    name = lhs_fv[0]
                    self.__bind(name, sy.solve(sy.Eq(self.__raw_args[0], self.__raw_args[1]), name),
                        None)
                else:
                    self.__raw_error = "Too many free variables."
        else:
            raise ValueError("Unexpected argument count.")
    def __bind(self, name, body, plot_type):
        if isinstance(body, list):
            if len(body) == 0:
                self.__raw_error = "No solutions for " + str(name) + "."
            elif len(body) == 1:
                body = body[0]
        self.__raw_binding = Binding(name, body, plot_type)

    def reset(self):
        self.__binding = copy.copy(self.__raw_binding)
        self.__error = self.__raw_error
    def get_equation(self):
        if self.has_binding(): return self.get_binding().get_colour()
        return None
    def set_equation(self, equation):
        if self.has_binding(): self.get_binding().set_equation(equation)
        if self.__raw_binding is not None:
            self.__raw_binding.set_equation(equation)
    def get_colour(self):
        if self.has_binding(): return self.get_binding().get_colour()
        return None
    def set_colour(self, colour):
        if self.has_binding(): self.get_binding().set_colour(colour)
        if self.__raw_binding is not None:
            self.__raw_binding.set_colour(colour)

    def has_binding(self):
        return self.__binding is not None
    def get_binding(self):
        return self.__binding
    def has_error(self):
        return self.__error is not None
    def get_error(self):
        return self.__error

    def __str__(self):
        if self.has_binding():
            return str(self.get_binding())
        else:
            return str(self.__raw_expr)
