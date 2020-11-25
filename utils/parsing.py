import enum

import sympy
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, \
    implicit_multiplication, \
    function_exponentiation, \
    convert_xor

class Parser:

    __instance = None

    __transformations = standard_transformations \
        + (implicit_multiplication, \
        function_exponentiation, \
        convert_xor)

    @staticmethod
    def getInstance():
        if Parser.__instance is None:
            raise Exception("No instance of Parser.")
        return Parser.__instance

    def __init__(self):
        if Parser.__instance is not None:
            raise Exception("Invalid initialistion of Parser.")
        Parser.__instance = self

    def parse(self, expr):
        return sympy.sympify(parse_expr(expr,
            transformations = self.__transformations))

class ParseMode(enum.Enum):
    NORMAL      = 0
    COMPARATIVE = 1

class Parsed:

    __comparatives = ['<', '>', '=']

    __comparative = None
    __blocks = []

    __symbols = []
    __binds = None

    __value = None
    __error = None

    def __init__(self, expr):
        mode = ParseMode.NORMAL

        comp = None
        blocks = []
        restrictions = []

        curr_norm = ""
        curr_comp = ""
        for s in expr:
            if mode == ParseMode.NORMAL:
                if s in self.__comparatives:
                    if comp is not None and comp != s:
                        self.__error = "Inconsistent comparatives."
                        return
                    comp = s
                    blocks.append(curr_norm)
                    curr_norm = ""
                elif s == '{':
                    mode = ParseMode.COMPARATIVE
                else:
                    curr_norm += s
            elif mode == ParseMode.COMPARATIVE:
                if s == '}':
                    mode = ParseMode.NORMAL
                    restrictions.append(curr_comp)
                    curr_comp = ""
                else:
                    curr_comp += s
            else:
                raise ValueError("Unknown ParseMode in Parsed.")
        if len(curr_norm) != 0:
            blocks.append(curr_norm)
        if len(curr_comp) != 0:
            self.__error = "Unmatched braces."
            return

        for i in range(len(blocks)):
            try:
                blocks[i] = Parser.getInstance().parse(blocks[i])
            except SyntaxError:
                self.__error = "Syntax error."
                return
            except:
                self.__error = "Error."
                return

        if len(blocks) == 0:
            return None
        elif len(blocks) == 1:
            self.__comparative = None
            self.__blocks = blocks
            self.__symbols = blocks[0].atoms(sympy.Symbol)
            self.__binds = None
            if len(self.__symbols) == 0:
                try:
                    self.__value = blocks[0].evalf()
                except TypeError:
                    self.__value = None
                    self.__error = "Evaluation error."
        elif len(blocks) == 2:
            return None
        else:
            self.__error = "Too many chained expressions."
            return None

    def getComparative(self):
        return self.__comparative

    def getBlocks(self):
        return self.__blocks

    def getVariables(self):
        return self.__symbols

    def getBinding(self):
        return self.__binds

    def hasValue(self):
        return self.__value is not None
    def getValue(self):
        return self.__value

    def hasError(self):
        return self.__error is not None
    def getError(self):
        return self.__error
