from tkinter import Tk, Menu
from tkinter.messagebox import showinfo

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.files import FileManager
from utils.theme import Theme
from utils.parsing import Parser
from utils.delay import DelayTracker

from components.equationEditor import EquationEditor
from components.equationViewer import EquationViewer

class Helix:

    def __init__(self):
        self.__root = Tk()
        self.__root.iconbitmap(ImageManager.get_images_path("icon.ico"))

        self.__fonts = FontManager(self.__root)
        self.__images = ImageManager()
        self.__files = FileManager()
        self.__theme = Theme()
        self.__parser = Parser()
        self.__delayTracker = DelayTracker()

        self.__width = 1280
        self.__height = 720

        self.__menu = Menu(self.__root)
        self.__file_menu = Menu(self.__menu, tearoff = 0)

        self.__frame_editor = None
        self.__frame_viewer = None
        self.__frame_split = 0.2

        self.__constructWindow()
        self.__constructMenu()
        self.__constructPanels()

        self.__root.lift()

    def __constructWindow(self):
        self.__root.title("Helix Graphing Tool")
        self.__root.geometry('%dx%d+%d+%d' %
            (self.__width, self.__height,
            (self.__root.winfo_screenwidth() / 2) - (self.__width / 2),
            (self.__root.winfo_screenheight() / 2) - (self.__height / 2)))
        self.__root.wm_protocol("WM_DELETE_WINDOW", self.__root.quit)
    def __constructMenu(self):
        # File Menu
        self.__file_menu.add_command(label = "New Project")
        self.__file_menu.add_command(label = "Save Project", command = self.__save_project)
        self.__file_menu.add_command(label = "Load Project", command = self.__load_project)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label = "Exit", command = self.__root.quit)
        self.__menu.add_cascade(label = "File", menu = self.__file_menu)
        # About Button
        self.__menu.add_command(label = "About", command = lambda :
            showinfo("Helix Graphing Tool", "Written by Tyler Wright\n"
                + "with Matplotlib and SymPy\n"
                + "\nwww.fluxanoia.co.uk"))
        # Root config
        self.__root.config(menu = self.__menu)
    def __constructPanels(self):
        self.__frame_viewer = EquationViewer(self.__root, self.__frame_split)
        self.__frame_editor = EquationEditor(self.__root, self.__frame_split,
            self.__frame_viewer.plot)

    @staticmethod
    def get_project_settings():
        return {
                EquationViewer.DIM_KEY : "2",
                EquationViewer.RECT_KEY : "-10 -10 20 20",
                EquationViewer.ELEV_KEY : "30",
                EquationViewer.AZIM_KEY : "-60",
                EquationViewer.CUBOID_KEY : "-10 -10 -10 20 20 20"
            }
    def __save_project(self):
        settings = {}
        self.__frame_viewer.add_settings(settings)
        self.__frame_editor.add_settings(settings)
        self.__files.save_project(settings)
    def __load_project(self):
        settings = self.__files.load_project(self.get_project_settings())
        self.__frame_viewer.set_settings(settings)
        self.__frame_editor.set_settings(settings)

    def run(self): self.__root.mainloop()

if __name__ == "__main__":
    Helix().run()
