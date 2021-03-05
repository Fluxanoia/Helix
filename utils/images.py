from PIL import Image, ImageTk

from utils.files import FileManager

class ImageManager:

    __instance = None

    @staticmethod
    def get_instance():
        if ImageManager.__instance is None:
            raise Exception("No instance of ImageManager.")
        return ImageManager.__instance

    def __init__(self):
        if ImageManager.__instance is not None:
            raise Exception("Invalid initialistion of ImageManager.")
        ImageManager.__instance = self
        self.__images = {}

    def get_colour(self, r, g, b, width = None, height = None):
        if width is None or height is None:
            width = height = 32
        name = str(r) + "_" + str(g) + "_" + str(b)
        if self.__images.get(name, None) is None:
            self.__images[name] = { }

        if self.__images[name].get((width, height), None) is None:
            self.__images[name][(width, height)] = ImageTk.PhotoImage(Image.new('RGB',
                (width, height), color = (r, g, b)))
        return self.__images[name][(width, height)]

    def get_image(self, name, width = None, height = None):
        name = ImageManager.get_images_path(name)
        if self.__images.get(name, None) is None:
            self.__images[name] = { None : Image.open(name) }
        img = self.__images[name][None]

        if width is None or height is None:
            width, height = img.size

        if self.__images[name].get((width, height), None) is None:
            self.__images[name][(width, height)] = ImageTk.PhotoImage(
                img.resize((width, height), Image.ANTIALIAS))
        return self.__images[name][(width, height)]

    @staticmethod
    def get_images_path(*args):
        return FileManager.get_path("images", *args)
