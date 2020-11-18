class Theme:

    __instance = None

    __shades = [
        '#202020',
        '#404040',
        '#606060',
        '#808080'
    ]

    @staticmethod
    def getInstance():
        if Theme.__instance is None:
            Theme()
        return Theme.__instance

    def __init__(self):
        if Theme.__instance is not None:
            raise Exception("Invalid initialistion of singleton.")
        else:
            Theme.__instance = self

    def getShade(self, i):
        return self.__shades[i]
