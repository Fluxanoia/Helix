import enum

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
        else:
            Parser.__instance = self

    def getTransformations(self):
        return self.__transformations

class ParseMode(enum.Enum):
    NORMAL      = 0
    COMPARATIVE = 1

class Parsed:

    __comparatives = ['<', '>', '=']

    __parsed = None

    __binds = []

    __error = None

    def __init__(self, expr):
        mode = ParseMode.NORMAL

        comp = []
        blocks = []
        restrictions = []

        curr_norm = ""
        curr_comp = ""
        for s in expr:
            if mode == ParseMode.NORMAL:
                if s in self.__comparatives:
                    comp.append(s)
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
            self.__error = "Unmatched restriction braces."

        try:
            self.__parsed = parse_expr(expr,
                transformations = Parser.getInstance().getTransformations())
        except SyntaxError:
            self.__parsed = None
            self.__error = "Syntax Error."
