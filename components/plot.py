
class Plot:

    __expr = None
    __free_vars = []

    def __init__(self, expr, free_vars):
        self.__expr = expr
        self.__free_vars = free_vars

    def getDimensionality(self):
        return len(self.__free_vars) + 1

    def getPlot2D(self, values):
        if self.getDimensionality() != 2:
            raise ValueError("No 2D values of " \
                + str(self.getDimensionality()) \
                + "D plot")
        output = []
        var = self.__free_vars[0]
        for i in values:
            output.append(self.__expr.evalf(subs = { var: i }))
        return output

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
