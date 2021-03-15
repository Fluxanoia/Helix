import enum

class Dimension(enum.Enum):
    TWO_D   = 2
    THREE_D = 3

class PlotType(enum.Enum):
    LINE_2D = 0
    PARAMETRIC_2D = 1
    IMPLICIT_2D = 2

    SURFACE = 3
    PARAMETRIC_3D = 4
    PARAMETRIC_SURFACE = 5

    @staticmethod
    def two_d():
        return [PlotType.LINE_2D, PlotType.PARAMETRIC_2D, PlotType.IMPLICIT_2D]
    @staticmethod
    def three_d():
        return [PlotType.SURFACE, PlotType.PARAMETRIC_3D, PlotType.PARAMETRIC_SURFACE]
    @staticmethod
    def parametric():
        return [PlotType.PARAMETRIC_2D, PlotType.PARAMETRIC_3D, PlotType.PARAMETRIC_SURFACE]

    @staticmethod
    def get_dim(pt):
        if pt in PlotType.two_d():
            return Dimension.TWO_D
        if pt in PlotType.three_d():
            return Dimension.THREE_D
        raise ValueError("No dimension for PlotType.")
