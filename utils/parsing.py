import enum

import numpy as np
import sympy as sy
from sympy.core.function import UndefinedFunction, AppliedUndef
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, \
    function_exponentiation, \
    convert_xor

class Parser:

    __instance = None

    __transformations = standard_transformations \
        + (function_exponentiation, convert_xor)

    __comparatives = None

    __x = None
    __y = None
    __def_bindings = None

    @staticmethod
    def getInstance():
        if Parser.__instance is None:
            raise Exception("No instance of Parser.")
        return Parser.__instance

    def __init__(self):
        if Parser.__instance is not None:
            raise Exception("Invalid initialistion of Parser.")
        self.__comparatives = ['<', '>', '=']
        self.__x, self.__y = sy.symbols('x y')
        e, pi = sy.symbols('e pi')
        self.__def_bindings = [(e, np.exp(1)), (pi, np.pi)]
        Parser.__instance = self

    def parse(self, expr):
        return sy.sympify(parse_expr(expr,
            transformations = self.__transformations))

    def get_comparatives(self):
        return self.__comparatives

    def get_symbol_x(self):
        return self.__x
    def get_symbol_y(self):
        return self.__y

    def get_default_symbols(self):
        return [self.__x, self.__y]

    def get_default_bindings(self):
        return self.__def_bindings

class ParseMode(enum.Enum):
    NORMAL      = 0
    COMPARATIVE = 1

class Dimension(enum.Enum):
    TWO_D   = 2
    THREE_D = 3

class Binding:

    name = None
    body = None
    eq = None

    def get_symbols(self):
        var = set(self.body.free_symbols)
        func = set(self.body.atoms(AppliedUndef))
        return list(var.union(func))

    def get_xy_symbols(self):
        parser = Parser.getInstance()
        return list(filter(lambda s : s in parser.get_default_symbols(),
            self.get_symbols()))

    def get_free_symbols(self):
        parser = Parser.getInstance()
        return list(filter(lambda s : not (s in parser.get_default_symbols()),
            self.get_symbols()))

    def subs(self, subst):
        try:
            self.body = self.body.subs(subst)
        except Exception as e:
            return type(e).__name__
        return None

    def replace(self, x, y):
        try:
            self.body = self.body.replace(x, y)
        except Exception as e:
            return type(e).__name__
        return None

    def label(self, text):
        self.eq.label(text)

    def is_var(self):
        return isinstance(self.name, sy.Symbol)

    def is_func(self):
        return isinstance(self.name, UndefinedFunction)

class Parsed:

    eq = None
    colour = None

    __raw = None
    __blocks = []
    __comparative = None
    __restrictions = []

    __dim = None

    __binds = None

    __value = None
    __error = None

    def __init__(self, expr):
        self.__raw = expr
        self.eval()

    def eval(self):
        parser = Parser.getInstance()
        self.__blocks = []
        self.__comparative = None
        self.__restrictions = []
        self.__dim = None
        self.__binds = None
        self.__value = None
        self.__error = None
        # Partition the raw expression
        parsed_norm = ""
        parsed_comp = ""
        mode = ParseMode.NORMAL
        for s in self.__raw:
            if mode == ParseMode.NORMAL:
                if s in parser.get_comparatives():
                    if (self.__comparative is not None) and (self.__comparative != s):
                        self.__error = "Inconsistent comparatives."
                        return
                    self.__comparative = s
                    self.__blocks.append(parsed_norm)
                    parsed_norm = ""
                elif s == '{':
                    mode = ParseMode.COMPARATIVE
                else:
                    parsed_norm += s
            elif mode == ParseMode.COMPARATIVE:
                if s == '}':
                    mode = ParseMode.NORMAL
                    self.__restrictions.append(parsed_comp)
                    parsed_comp = ""
                else:
                    parsed_comp += s
            else:
                raise ValueError("Unknown ParseMode in Parsed.")
        if len(parsed_norm) != 0:
            self.__blocks.append(parsed_norm)
        if len(parsed_comp) != 0:
            self.__error = "Unmatched braces."
            return
        # Parse the partitioned blocks
        for i in range(len(self.__blocks)):
            try:
                self.__blocks[i] = Parser.getInstance().parse(self.__blocks[i])
                self.__blocks[i] = self.__blocks[i].subs(parser.get_default_bindings())
            except Exception as e:
                self.__error = type(e).__name__
                return
        # Evaluate the blocks
        xy = self.get_xy_symbols()
        fv = self.get_free_symbols()
        if len(self.__blocks) == 0:
            self.__error = "Empty."
        elif len(self.__blocks) == 1:
            if len(xy) == 0:
                try:
                    self.__value = self.__blocks[0].evalf()
                    self.__dim = 2
                except Exception as e:
                    self.__error = type(e).__name__
                    return
            elif len(xy) == 1:
                if xy[0] == parser.get_symbol_x(): self.__dim = 2
            elif len(xy) == 2:
                self.__dim = 3
        elif len(self.__blocks) == 2 and isinstance(self.__blocks[0], sy.Function):
            args = self.__blocks[0].args
            if not len(args) == len(set(args)):
                self.__error = "Duplicate inputs."
            else:
                self.__binds = Binding()
                self.__binds.name = sy.Function(self.__blocks[0].name)
                self.__binds.body = sy.Lambda(args, self.__blocks[1])
        elif len(self.__blocks) == 2 and parser.get_symbol_y() in xy:
            self.__bind(parser.get_symbol_y(),
                    sy.solve(sy.Eq(self.__blocks[0], self.__blocks[1]), parser.get_symbol_y()))
        elif len(self.__blocks) == 2 and parser.get_symbol_x() in xy:
            try:
                self.__value = list(sy.solveset(sy.Eq(self.__blocks[0], self.__blocks[1]),
                    parser.get_symbol_x(), domain = sy.S.Reals))
            except Exception as e:
                self.__error = type(e).__name__
                return
        elif len(self.__blocks) == 2 and len(fv) == 0:
            self.__value = 1 if sy.Eq(self.__blocks[0], self.__blocks[1]) else 0
        elif len(self.__blocks) == 2:
            bvar = None
            lhs_free = list(filter(lambda s : not (s in parser.get_default_symbols()),
                self.__blocks[0].free_symbols))
            if len(lhs_free) == 1:
                bvar = lhs_free[0]
            else:
                rhs_free = list(filter(lambda s : not (s in parser.get_default_symbols()),
                    self.__blocks[1].free_symbols))
                if len(rhs_free) == 1:
                    bvar = rhs_free[0]
                else:
                    self.__error = "Too many LHS free variables."
            if bvar is not None:
                self.__bind(bvar, sy.solve(sy.Eq(self.__blocks[0], self.__blocks[1]), bvar))
        elif len(self.__blocks) == 3:
            pass
        else:
            self.__error = "Too many chained expressions."

    def __bind(self, bvar, bbody):
        if isinstance(bbody, list):
            if len(bbody) == 0:
                self.__error = "No solutions for " + str(bvar) + "."
            if len(bbody) == 1:
                bbody = bbody[0]
        self.__binds = Binding()
        self.__binds.name = bvar
        self.__binds.body = bbody

    def subs(self, subst):
        for i in range(len(self.__blocks)):
            try:
                self.__blocks[i] = self.__blocks[i].subs(subst)
            except Exception as e:
                self.__error = type(e).__name__
                return self.__error
        return None

    def replace(self, x, y):
        for i in range(len(self.__blocks)):
            try:
                self.__blocks[i] = self.__blocks[i].replace(x, y)
            except Exception as e:
                self.__error = type(e).__name__
                return self.__error
        return None

    def get_symbols(self):
        symbols = set()
        if not self.has_error():
            for b in self.__blocks:
                symbols = symbols.union(set(b.free_symbols))
                symbols = symbols.union(set(b.atoms(AppliedUndef)))
        return list(symbols)

    def get_xy_symbols(self):
        parser = Parser.getInstance()
        return list(filter(lambda s : s in parser.get_default_symbols(),
            self.get_symbols()))

    def get_free_symbols(self):
        parser = Parser.getInstance()
        return list(filter(lambda s : not (s in parser.get_default_symbols()),
            self.get_symbols()))

    def get_comparative(self):
        return self.__comparative

    def get_blocks(self):
        return self.__blocks

    def has_binding(self):
        return self.__binds is not None
    def get_binding(self):
        return self.__binds

    def has_dim(self):
        return self.__dim is not None
    def get_dim(self):
        return self.__dim

    def has_value(self):
        return self.__value is not None
    def get_value(self):
        return self.__value

    def has_error(self):
        return self.__error is not None
    def get_error(self):
        return self.__error

    def __str__(self):
        s = ""
        for b in self.__blocks: s += str(b) + " "
        return s
