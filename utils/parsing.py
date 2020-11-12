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

    def parse(self, expr):
        try:
            return parse_expr(expr,
                transformations = self.__transformations)
        except SyntaxError:
            return "Syntax Error"
