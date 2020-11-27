import numpy as np

from utils.maths import updateBounds

class Plot:

    __expr = None
    __free_vars = []

    def __init__(self, expr, free_vars):
        self.__expr = expr
        self.__free_vars = free_vars

    def evaluate(self, subs):
        value = None
        try:
            value = self.__expr.evalf(subs = subs)
        except: return None
        if value is None: return None
        if not value.is_Number or value.is_infinite:
            return None
        return value

    def getFreeVariables(self):
        return self.__free_vars

    def getDimensionality(self):
        return len(self.__free_vars) + 1

    def __breakSection(self, x, xs):
        if len(x) > 0:
            xs.append(x)
            x = []
        return x, xs

    def __breakSection2D(self, x, y, xs, ys):
        x, xs = self.__breakSection(x, xs)
        y, ys = self.__breakSection(y, ys)
        return x, y, xs, ys

    def getPlot2D(self, xmin, xmax, count):
        if self.getDimensionality() != 2:
            raise ValueError("No 2D values of " \
                + str(self.getDimensionality()) \
                + "D plot")

        step = (xmax - xmin) / (count - 1)
        values = xmin + step * np.array(range(count))
        xs = []
        ys = []
        undefs = []
        ymin = None
        ymax = None

        x = []
        y = []
        undef = []
        var = self.__free_vars[0]
        for i in range(len(values)):
            value = self.evaluate({ var: values[i] })
            if value is None:
                undef.append(values[i])
                x, y, xs, ys = self.__breakSection2D(x, y, xs, ys)
            else:
                undef, undefs = self.__breakSection(undef, undefs)
                x.append(values[i])
                y.append(value)
                ymin, ymax = updateBounds(ymin, ymax, value)
        undef, undefs = self.__breakSection(undef, undefs)
        x, y, xs, ys = self.__breakSection2D(x, y, xs, ys)
        ymin, ymax = updateBounds(ymin, ymax, 0)
        asymp = []
        for u in undefs:
            asymp.append(u[0])
            if len(u) > 1: asymp.append(u[-1])
        if len(asymp) > 0 and asymp[0] == xmin \
            and self.evaluate({ var: xmin - step }) is None:
            asymp.pop(0)
        if len(asymp) > 0 and asymp[-1] == xmax \
            and self.evaluate({ var: xmax + step }) is None:
            asymp.pop(-1)
        return xs, ys, asymp, float(ymin), float(ymax)

    def getPlot3D(self, x_values, y_values):
        if self.getDimensionality() != 3:
            raise ValueError("No 3D values of " \
                + str(self.getDimensionality()) \
                + "D plot")
        output = []
        x_var = self.__free_vars[0]
        y_var = self.__free_vars[1]
        for i in range(len(x_values)):
            row = []
            for j in range(len(x_values[i])):
                row.append(self.__expr.evalf(
                    subs = { x_var: x_values[i][j], y_var: y_values[i][j] }))
            output.append(row)
        return output
