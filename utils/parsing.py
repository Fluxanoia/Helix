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
            Parser()
        return Parser.__instance

    def __init__(self):
        if Parser.__instance is not None:
            raise Exception("Invalid initialistion of singleton.")
        Parser.__instance = self

    def parse(self, expr):
        return parse_expr(expr,
            transformations = self.__transformations)

class ParseMode(enum.Enum):
    NORMAL      = 0
    COMPARATIVE = 1

class Parsed:

    __comparatives = ['<', '>', '=']

    __comparative = None
    __blocks = []

    __symbols = []
    __binds = None

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
                        self.__error = "Error."
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
            self.__error = "Error."
            return

        for i in range(len(blocks)):
            try:
                blocks[i] = Parser.getInstance().parse(blocks[i])
            except SyntaxError:
                self.__error = "Error."
                return

        if len(blocks) == 0:
            return
        elif len(blocks) == 1:
            self.__comparative = None
            self.__blocks = blocks
            self.__symbols = blocks[0].atoms(sympy.Symbol)
            self.__binds = None
        elif len(blocks) == 2:
            return
        else:
            self.__error = "Error."
            return

    def getComparative(self):
        return self.__comparative

    def getBlocks(self):
        return self.__blocks

    def getVariables(self):
        return self.__symbols

    def getBinding(self):
        return self.__binds

    def hasError(self):
        return self.__error is not None
    def getError(self):
        return self.__error
