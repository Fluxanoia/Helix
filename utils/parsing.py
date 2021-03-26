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
from sympy.core.containers import Tuple
from sympy.logic.boolalg import BooleanFunction
from sympy.core.compatibility import exec_

from utils.maths import PlotType

class ParsingError(Exception):

    def __init__(self, t, m):
        self.__type = t
        self.__message = m
        super().__init__(self.__str__())

    def __str__(self):
        return str(self.__type) + " -> " + str(self.__message)

class Parser:

    __instance = None

    LT = (LessThan, StrictLessThan)
    GT = (GreaterThan, StrictGreaterThan)

    RESERVED_SYMBOLS = ('x', 'y', 'z', 't', 'u', 'v')
    X, Y, Z, T, U, V = sy.symbols(('x', 'y', 'z', 't', 'u', 'v'))

    FILTER_XYZ = lambda s : s in [Parser.X, Parser.Y, Parser.Z]
    FILTER_NOT_XYZ = lambda s : not s in [Parser.X, Parser.Y, Parser.Z]

    FILTER_TUV = lambda s : s in [Parser.T, Parser.U, Parser.V]
    FILTER_NOT_TUV = lambda s : not s in [Parser.T, Parser.U, Parser.V]

    FILTER_RESERVED = lambda s : s in [Parser.X, Parser.Y, Parser.Z,
        Parser.T, Parser.U, Parser.V]
    FILTER_NOT_RESERVED = lambda s : not s in [Parser.X, Parser.Y, Parser.Z,
        Parser.T, Parser.U, Parser.V]

    VAR_TYPES = (sy.Symbol)
    FUNC_TYPES = (AppliedUndef, UndefinedFunction)
    SYMBOL_TYPES = (sy.Symbol, AppliedUndef, UndefinedFunction)

    @staticmethod
    def get_instance():
        if Parser.__instance is None:
            raise Exception("No instance of Parser.")
        return Parser.__instance

    def __init__(self):
        if Parser.__instance is not None:
            raise Exception("Invalid initialistion of Parser.")
        Parser.__instance = self
        self.__transformations = standard_transformations \
            + (function_exponentiation, convert_xor, convert_equals_signs)

        self.__global_dict = {}
        exec_('from sympy.core import *', self.__global_dict)
        exec_('from sympy.functions import *', self.__global_dict)
        exec_('from sympy.integrals import *', self.__global_dict)
        exclusions = ['sympify', 'SympifyError', 'Subs', 'evalf', 'evaluate']
        for e in exclusions: self.__global_dict.pop(e)

        e, pi = sy.symbols('e pi')
        def func_check(name):
            return lambda e : isinstance(e, sy.Function) \
                and getattr(e, 'name', None) == name

        self.__default_subs = [(e, np.exp(1)), (pi, np.pi)]
        self.__default_repl = [
            (func_check('der'), lambda e : Derivative(*e.args)),
            (func_check('int'), lambda e : Integral(*e.args))]
        self.__default_trans = [
            (lambda x : isinstance(x, (Derivative, Integral)), lambda e : e.doit())]
        self.__invalid_atoms = (Derivative, Integral)

    def is_reserved(self, name):
        return str(name) in Parser.RESERVED_SYMBOLS
    def is_defined(self, name):
        return self.is_reserved(name) or str(name) in self.__global_dict

    def subs(self, expr, sb = None):
        if isinstance(expr, (tuple, Tuple)):
            return tuple(map(lambda e : self.subs(e, sb), expr))
        if isinstance(expr, list):
            return list(map(lambda e : self.subs(e, sb), expr))
        try:
            expr = expr.subs(self.__default_subs if sb is None else sb)
        except Exception as e:
            raise ParsingError("Parser.subs", e) from e
        return expr
    def replace(self, expr, rp = None):
        if isinstance(expr, (tuple, Tuple)):
            return tuple(map(lambda e : self.replace(e, rp), expr))
        if isinstance(expr, list):
            return list(map(lambda e : self.replace(e, rp), expr))
        if rp is None: rp = self.__default_repl
        try:
            for (f, t) in rp: expr = expr.replace(f, t)
        except Exception as e:
            raise ParsingError("Parser.replace", e) from e
        return expr
    def transform(self, expr, tr = None):
        if isinstance(expr, (tuple, Tuple)):
            return tuple(map(lambda e : self.transform(e, tr), expr))
        if isinstance(expr, list):
            return list(map(lambda e : self.transform(e, tr), expr))
        if tr is None: tr = self.__default_trans
        try:
            for (f, t) in tr: expr = expr.replace(f, t)
        except Exception as e:
            raise ParsingError("Parser.transform", e) from e
        return expr
    def default_ops(self, expr):
        for f in [self.subs, self.replace, self.transform]:
            expr = f(expr)
        return expr

    def is_valid(self, expr):
        if isinstance(expr, (tuple, Tuple, list)):
            return all(map(self.is_valid, expr))
        return len(expr.atoms(*self.__invalid_atoms)) == 0

    def args(self, raw_expr):
        def _args(expr):
            if not isinstance(expr, Relational):
                return [expr]
            args = []
            for arg in expr.args:
                args.extend(_args(arg))
            return args
        return _args(raw_expr)
    def get_symbols(self, exprs, filter_func = None):
        if not isinstance(exprs, list): exprs = [exprs]
        def _to_undef(f):
            if isinstance(f, AppliedUndef):
                return sy.Function(f.name)
            return f
        def _add_symbols(e):
            s = set(getattr(e, 'free_symbols', []))
            if hasattr(e, 'atoms'):
                atoms = e.atoms(*Parser.FUNC_TYPES)
                atoms = list(map(_to_undef, atoms))
                s = s.union(set(atoms))
            return s
        symbols = set()
        for expr in exprs:
            if isinstance(expr, (tuple, Tuple)):
                symbols = symbols.union(*map(_add_symbols, expr))
            else:
                symbols = symbols.union(_add_symbols(expr))
        if not filter_func is None:
            symbols = set(filter(filter_func, symbols))
        return symbols

    def parse(self, expr):
        return parse_expr(expr, global_dict = self.__global_dict,
            transformations = self.__transformations,
            evaluate = False)
    def parse_number(self, expr):
        for t in (list, tuple):
            if isinstance(expr, t): return t(map(self.parse_number, expr))
        try:
            expr = self.parse(expr)
            expr = expr.evalf()
            if expr.is_number: return expr
        except:
            return None

    def get_default_subs(self): return self.__default_subs
    def get_default_repl(self): return self.__default_repl
    def get_default_trans(self): return self.__default_trans

class Binding:

    def __init__(self, name, body, plot_type,
        dep = None, eq = None, cl = None, pl = None, sig = None):
        self.__name = name
        self.__body = body
        self.__plot_type = plot_type

        self.__dependencies = set() if dep is None else dep
        self.__equation = eq
        self.__colour = cl
        self.__parametric_lims = {} if pl is None else pl

        self.__signature = sig

    def split(self):
        if isinstance(self.__body, list):
            f = lambda b : Binding(self.__name, b,
                self.__plot_type, self.__dependencies,
                self.__equation, self.__colour,
                self.__parametric_lims)
            return [f(b) for b in self.__body]
        return [self]
    def get_signature(self):
        return self if self.__signature is None else self.__signature

    def label(self, t, text):
        if not self.__equation is None: self.__equation.label(t, text)

    def get_symbols(self):
        return Parser.get_instance().get_symbols(self.get_body())
    def get_xyz_symbols(self):
        return Parser.get_instance().get_symbols(self.get_body(), Parser.FILTER_XYZ)
    def get_tuv_symbols(self):
        return Parser.get_instance().get_symbols(self.get_body(), Parser.FILTER_TUV)
    def get_free_symbols(self, historical = False):
        fv = Parser.get_instance().get_symbols(self.get_body(), Parser.FILTER_NOT_RESERVED)
        return self.__dependencies.union(fv) if historical else fv
    def get_dependencies(self):
        return self.__dependencies

    def binds_var(self):
        return isinstance(self.__name, Parser.VAR_TYPES)
    def binds_func(self):
        return isinstance(self.__name, Parser.FUNC_TYPES)

    def __transform(self, func, tr, def_tr):
        fv = self.get_free_symbols()
        if tr is None: tr = def_tr
        self.__body = getattr(Parser.get_instance(), func)(self.__body, tr)
        for (d, _) in tr:
            if d in fv: self.__dependencies.add(d)
    def subs(self, sb = None):
        self.__transform('subs', sb, Parser.get_instance().get_default_subs())
    def replace(self, rp = None):
        self.__transform('replace', rp, Parser.get_instance().get_default_repl())
    def transform(self, tr = None):
        self.__transform('replace', tr, Parser.get_instance().get_default_trans())
    def default_ops(self):
        for f in [self.subs, self.replace, self.transform]: f()

    def is_valid(self):
        if self.__plot_type not in PlotType.parametric() \
            and isinstance(self.__body, (tuple, Tuple)):
            return False
        return Parser.get_instance().is_valid(self.__body)

    def get_name(self):
        return self.__name
    def get_body(self):
        return self.__body
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

    def get_parametric_limits(self):
        return self.__parametric_lims
    def set_parametric_limits(self, pl):
        self.__parametric_lims = pl

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
                return str(self.__body.lhs) \
                    + " " + op_dict[type(self.__body)] \
                    + " " + str(self.__body.rhs)
            else:
                return str(self.__body)
        elif self.__plot_type in PlotType.parametric():
            return str(self.__body)
        else:
            return str(self.__name) + " = " + str(self.__body)

class Parsed:

    def __init__(self, raw):
        self.__raw_expr = None
        self.__raw_args = None
        self.__raw_relation = None
        self.__is_parametric = False

        self.__raw = raw
        self.__raw_binding = None
        self.__raw_error = None

        self.__binding = None
        self.__error = None

        try:
            self.__eval()
        except Exception as e:
            self.__raw_error = str(e)
        self.reset()

    def __eval_gather(self):
        if len(self.__raw) == 0: raise ParsingError("Parsed.eval_gather", "Nothing to parse.")
        parser = Parser.get_instance()
        self.__raw_expr = self.__raw
        for f in [parser.parse, parser.subs, parser.replace]:
            self.__raw_expr = f(self.__raw_expr)
        if isinstance(self.__raw_expr, (tuple, Tuple)):
            self.__is_parametric = True
            self.__raw_args = self.__raw_expr
            if len(self.__raw_args) > 3:
                raise ParsingError("Parsed.eval_gather", "Parametrics not supported past 3D.")
            if len(self.__raw_args) < 2:
                raise ParsingError("Parsed.eval_gather", "Parametrics not supported below 2D.")
        else:
            self.__raw_args = parser.args(self.__raw_expr)
            if len(self.__raw_args) > 2:
                raise ParsingError("Parsed.eval_gather", "Too many relations.")
    def __eval_structure(self):
        def check_structure(raw_expr):
            def _valid_structure(expr, root = False):
                if isinstance(expr, BooleanFunction): return False
                if isinstance(expr, Unequality): return False#
                if isinstance(expr, (tuple, Tuple)):
                    if root:
                        return all(map(_valid_structure, expr))
                    else:
                        return False
                if isinstance(expr, Relational):
                    expr_type = type(expr)
                    if self.__raw_relation is None:
                        self.__raw_relation = expr_type
                    else:
                        comps = set(self.__raw_relation, expr_type)
                        if not all(c in Parser.LT for c in comps) and \
                            not all(c in Parser.GT for c in comps) and \
                            not (expr_type == self.__raw_relation and expr_type == Equality):
                            return False
                    return all(map(_valid_structure, expr.args))
                return True
            if not _valid_structure(raw_expr, True):
                raise ParsingError("Parsed.eval_structure", "Invalid structure.")
        check_structure(self.__raw_expr)
    def __eval_bind(self):
        parser = Parser.get_instance()
        xyz = parser.get_symbols(self.__raw_args, Parser.FILTER_XYZ)
        tuv = parser.get_symbols(self.__raw_args, Parser.FILTER_TUV)
        if len(xyz) > 0 and len(tuv) > 0:
            raise ParsingError("Parsed.eval_bind", "(x, y, z) and (t, u, v) shouldn't be mixed.")
        if self.__is_parametric:
            if len(self.__raw_args) == 2:
                if len(tuv) == 0:
                    raise ParsingError("Parsed.eval_bind", "Too few parametric variables.")
                elif len(tuv) < 2:
                    self.__bind(tuple(tuv), tuple(self.__raw_args), PlotType.PARAMETRIC_2D)
                else:
                    raise ParsingError("Parsed.eval_bind", "Too many parametric variables.")
            elif len(self.__raw_args) == 3:
                if len(tuv) == 0:
                    raise ParsingError("Parsed.eval_bind", "Too few parametric variables.")
                elif len(tuv) < 2:
                    self.__bind(tuple(tuv), tuple(self.__raw_args), PlotType.PARAMETRIC_3D)
                elif len(tuv) == 2:
                    self.__bind(tuple(tuv), tuple(self.__raw_args), PlotType.PARAMETRIC_SURFACE)
                else:
                    raise ParsingError("Parsed.eval_bind", "Too many parametric variables.")
            else:
                raise ParsingError("Parsed.eval_bind", "Unexpected parametric size.")
        elif len(self.__raw_args) == 1:
            arg = self.__raw_args[0]
            if len(xyz) == 0:
                self.__bind(Parser.Y, arg.evalf(), PlotType.LINE_2D)
            elif len(xyz) == 1:
                if Parser.X in xyz:
                    self.__bind(Parser.Y, arg, PlotType.LINE_2D)
                else:
                    raise ParsingError("Parsed.eval_bind",
                        "Couldn't evaluate univariate statement.")
            elif len(xyz) == 2:
                if not Parser.Z in xyz:
                    self.__bind(Parser.Z, arg, PlotType.SURFACE)
                else:
                    raise ParsingError("Parsed.eval_bind",
                        "Couldn't evaluate bivariate statement.")
        elif len(self.__raw_args) == 2:
            larg = self.__raw_args[0]
            rarg = self.__raw_args[1]
            larg_name = getattr(larg, 'name', None)
            if self.__raw_relation in Parser.LT + Parser.GT:
                if Parser.Z in xyz:
                    raise ParsingError("Parsed.eval_bind", "3D implicit plots are not supported.")
                else:
                    self.__bind(None, self.__raw_relation(larg, rarg), PlotType.IMPLICIT_2D)
            elif isinstance(larg, Parser.FUNC_TYPES):
                if larg_name is None or parser.is_defined(larg_name):
                    raise ParsingError("Parsed.eval_bind",
                        "Function name already defined or reserved.")
                args = larg.args
                if any([not isinstance(a, Parser.VAR_TYPES) for a in args]):
                    raise ParsingError("Parsed.eval_bind", "Function arguments must be symbols.")
                elif len(args) != len(set(args)):
                    raise ParsingError("Parsed.eval_bind", "Duplicate parameters.")
                func = sy.Lambda(args, rarg)
                if len(parser.get_symbols(func, Parser.FILTER_RESERVED)) > 0:
                    raise ParsingError("Parsed.eval_bind", "Cannot map to reserved variables.")
                self.__bind(sy.Function(larg_name), func, None)
            elif isinstance(larg, Parser.VAR_TYPES) and not parser.is_reserved(larg):
                if parser.is_defined(larg_name):
                    raise ParsingError("Parsed.eval_bind",
                        "Variable name already defined.")
                if len(parser.get_symbols(rarg, Parser.FILTER_RESERVED)) > 0:
                    raise ParsingError("Parsed.eval_bind", "Cannot map to reserved variables.")
                self.__bind(larg, rarg, None)
            elif Parser.Z in xyz:
                sol = sy.solve(sy.Eq(larg, rarg), Parser.Z, domain = sy.S.Reals)
                if isinstance(sol, (list, tuple, Tuple)):
                    if len(sol) == 0:
                        raise ParsingError("Parsed.eval_bind", "No solutions.")
                    elif len(sol) == 1:
                        self.__bind(Parser.Z, sol[0], PlotType.SURFACE)
                    else:
                        self.__bind(Parser.Z, sol, PlotType.SURFACE)
                else:
                    self.__bind(Parser.Z, sol, PlotType.SURFACE)
            elif Parser.Y in xyz:
                sol = sy.solve(sy.Eq(larg, rarg), Parser.Y, domain = sy.S.Reals)
                if isinstance(sol, (list, tuple, Tuple)):
                    if len(sol) == 1:
                        self.__bind(Parser.Y, sol[0], PlotType.LINE_2D)
                    else:
                        self.__bind(None, sy.Eq(larg, rarg), PlotType.IMPLICIT_2D)
                else:
                    self.__bind(Parser.Y, sol, PlotType.LINE_2D)
            elif Parser.X in xyz:
                self.__bind(Parser.X, list(sy.solveset(sy.Eq(larg, rarg), Parser.X,
                    domain = sy.S.Reals)), None)
            else:
                self.__bind(None, sy.Eq(larg, rarg), None)
        else:
            raise ParsingError("Parsed.eval_bind", "Unexpected argument structure.")
    def __eval_finish(self):
        if not self.__raw_binding is None: self.__raw_binding.default_ops()
    def __eval(self):
        self.__eval_gather()
        self.__eval_structure()
        self.__eval_bind()
        self.__eval_finish()
    def __bind(self, name, body, plot_type):
        if isinstance(body, list):
            if len(body) == 0:
                raise ParsingError("Parsed.bind", "No solutions for " + str(name) + ".")
            elif len(body) == 1:
                body = body[0]
        if not isinstance(body, (sy.Expr, Relational, tuple, Tuple, list)):
            raise ParsingError("Parsed.bind", "Invalid bind.")
        self.__raw_binding = Binding(name, body, plot_type)

    def reset(self):
        self.__binding = copy.copy(self.__raw_binding)
        self.__error = self.__raw_error

    def has_binding(self):
        return self.__binding is not None
    def get_binding(self):
        return self.__binding
    def has_error(self):
        return self.__error is not None
    def get_error(self):
        return self.__error

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

    def __str__(self):
        if self.has_binding():
            return str(self.get_binding())
        else:
            return str(self.__raw_expr)
