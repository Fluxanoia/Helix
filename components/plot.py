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
    def __breakSection3D(self, x, y, z, xs, ys, zs):
        x, xs = self.__breakSection(x, xs)
        y, ys = self.__breakSection(y, ys)
        z, zs = self.__breakSection(z, zs)
        return x, y, z, xs, ys, zs

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

        if len(asymp) > 0:
            if asymp[0] == xmin and self.evaluate({ var: xmin - step }) is None:
                asymp.pop(0)
            if asymp[-1] == xmax and self.evaluate({ var: xmax + step }) is None:
                asymp.pop(-1)
        return {
            "x": xs,
            "y": ys,
            "asymptotes": asymp,
            "min": float(ymin),
            "max": float(ymax)
            }

    def getPlot3D(self, xmin, xmax, ymin, ymax, count):
        if self.getDimensionality() != 3:
            raise ValueError("No 3D values of " \
                + str(self.getDimensionality()) \
                + "D plot")

        x_step = (xmax - xmin) / (count - 1)
        y_step = (xmax - xmin) / (count - 1)
        x_values = xmin + x_step * np.array(range(count))
        y_values = ymin + y_step * np.array(range(count))
        xs = []
        ys = []
        zs = []
        undefs = []
        zmin = None
        zmax = None

        x = []
        y = []
        z = []
        undef = []
        x_var = self.__free_vars[0]
        y_var = self.__free_vars[1]
        for i in range(len(x_values)):
            for j in range(len(y_values)):
                value = self.evaluate({ x_var: x_values[i], y_var: y_values[j] })
                if value is None:
                    undef.append((x_values[i], y_values[j]))
                    x, y, z, xs, ys, zs = self.__breakSection3D(x, y, z, xs, ys, zs)
                else:
                    undef, undefs = self.__breakSection(undef, undefs)
                    x.append(x_values[i])
                    y.append(y_values[j])
                    z.append(value)
                    zmin, zmax = updateBounds(zmin, zmax, value)

        undef, undefs = self.__breakSection(undef, undefs)
        x, y, z, xs, ys, zs = self.__breakSection3D(x, y, z, xs, ys, zs)
        zmin, zmax = updateBounds(zmin, zmax, 0)
        asymp = []
        for u in undefs:
            asymp.append(u[0])
            if len(u) > 1: asymp.append(u[-1])

        if len(asymp) > 0:
            has_prec_x = asymp[0][0] == xmin
            has_prec_y = asymp[0][1] == ymin
            if has_prec_x: prec_x = self.evaluate({ x_var: xmin - x_step, y_var: asymp[0][1] })
            if has_prec_y: prec_y = self.evaluate({ x_var: asymp[0][0], y_var: ymin - y_step })
            if (has_prec_x and prec_x is None) or (has_prec_y and prec_y is None): asymp.pop(0)

            has_succ_x = asymp[-1][0] == xmin
            has_succ_y = asymp[-1][1] == ymin
            if has_succ_x: succ_x = self.evaluate({ x_var: xmax + x_step, y_var: asymp[-1][1] })
            if has_succ_y: succ_y = self.evaluate({ x_var: asymp[-1][0], y_var: ymax + y_step })
            if (has_succ_x and succ_x is None) or (has_succ_y and succ_y is None): asymp.pop(-1)
        return {
            "x": xs,
            "y": ys,
            "z": zs,
            "asymptotes": asymp,
            "min": float(zmin),
            "max": float(zmax)
            }
