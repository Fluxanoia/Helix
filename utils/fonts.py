from tkinter import font

class FontManager:

    __instance = None

    __textFont = None

    @staticmethod
    def getInstance(root = None):
        if FontManager.__instance is None:
            FontManager(root)
        return FontManager.__instance

    def __init__(self, root):
        if FontManager.__instance is not None:
            raise Exception("Invalid initialistion of singleton.")
        else:
            FontManager.__instance = self
            self.__textFont = font.Font(root, size=16)

    def getTextFont(self):
        return self.__textFont
