import sympy
class Plot:

    __expr = None
    __free_vars = []

    def __init__(self, expr, free_vars):
        self.__expr = expr
        self.__free_vars = free_vars

    def getDimensionality(self):
        return len(self.__free_vars) + 1

    def __breakPlot2D(self, x, y, xs, ys):
        if len(x) > 0:
            xs.append(x)
            ys.append(y)
            x = []
            y = []
        return x, y, xs, ys

    def getPlot2D(self, values):
        if self.getDimensionality() != 2:
            raise ValueError("No 2D values of " \
                + str(self.getDimensionality()) \
                + "D plot")

        xs = []
        ys = []
        undef = []
        asymp = []
        ymin = None
        ymax = None

        x = []
        y = []
        var = self.__free_vars[0]
        for i in values:
            value = None
            try:
                value = self.__expr.evalf(subs = { var: i })
                if not value.is_Number:
                    value = None
            except:
                plus = sympy.limit(self.__expr, var, i, '+')
                minus = sympy.limit(self.__expr, var, i, '-')
                if not (plus.is_Number and minus.is_Number):
                    value = None
                    asymp.append(i)
                elif plus == minus:
                    value = plus
                    undef.append(i)
                else:
                    value = None
                    asymp.append(i)
            if value is None:
                x, y, xs, ys = self.__breakPlot2D(x, y, xs, ys)
            else:
                if ymin is None or ymax is None:
                    ymin = value
                    ymax = value
                elif value < ymin:
                    ymin = value
                elif value > ymax:
                    ymax = value
                x.append(i)
                y.append(value)
        x, y, xs, ys = self.__breakPlot2D(x, y, xs, ys)
        if ymin is None or ymax is None:
            ymin = 0
            ymax = 0
        return (xs, ys, undef, asymp, float(ymin), float(ymax))

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
