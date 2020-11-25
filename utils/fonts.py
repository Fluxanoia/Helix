from tkinter import font

class FontManager:

    __instance = None

    __textFont = None

    def getTextFont(self):
        return self.__textFont
    def configureText(self, w):
        w.configure(font = self.getTextFont())

    @staticmethod
    def getInstance():
        if FontManager.__instance is None:
            raise Exception("No instance of FontManager.")
        return FontManager.__instance

    def __init__(self, root):
        if FontManager.__instance is not None:
            raise Exception("Invalid initialistion of FontManager.")
        else:
            FontManager.__instance = self
            self.__textFont = font.Font(root, size = 16)
