from tkinter import font

class FontManager:

    __instance = None

    @staticmethod
    def get_instance():
        if FontManager.__instance is None:
            raise Exception("No instance of FontManager.")
        return FontManager.__instance

    def __init__(self, root):
        if FontManager.__instance is not None:
            raise Exception("Invalid initialistion of FontManager.")
        else:
            FontManager.__instance = self
            self.__text_font = font.Font(root, size = 16)

    def get_text_font(self):
        return self.__text_font
    def configure_text(self, w):
        w.configure(font = self.get_text_font())
