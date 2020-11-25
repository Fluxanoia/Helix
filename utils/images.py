import os
from PIL import Image, ImageTk

class ImageManager:

    __instance = None
    __dir = ""

    __images = {}

    @staticmethod
    def getInstance():
        if ImageManager.__instance is None:
            raise Exception("No instance of ImageManager.")
        return ImageManager.__instance

    def __init__(self):
        if ImageManager.__instance is not None:
            raise Exception("Invalid initialistion of ImageManager.")
        ImageManager.__instance = self
        self.__dir = os.path.join(os.path.dirname(__file__), '..') + "\\images\\"

    def getImage(self, name, width = None, height = None):
        name = self.__dir + name
        if self.__images.get(name, None) is None:
            self.__images[name] = { None : Image.open(name) }
        img = self.__images[name][None]

        if width is None or height is None:
            width, height = img.size

        if self.__images[name].get((width, height), None) is None:
            self.__images[name][(width, height)] = ImageTk.PhotoImage(
                img.resize((width, height), Image.ANTIALIAS))
        return self.__images[name][(width, height)]
