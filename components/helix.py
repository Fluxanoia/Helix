from tkinter import Tk, Menu
from tkinter.messagebox import showinfo

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.theme import Theme
from utils.parsing import Parser
from utils.delay import DelayTracker

from components.equationEditor import EquationEditor
from components.equationViewer import EquationViewer

class Helix:

    def __init__(self):
        self.__root = Tk()

        self.__fonts = FontManager(self.__root)
        self.__images = ImageManager()
        self.__theme = Theme()
        self.__parser = Parser()
        self.__delayTracker = DelayTracker()

        self.__width = 1280
        self.__height = 720

        self.__menu = Menu(self.__root)
        self.__file_menu = Menu(self.__menu, tearoff = 0)
        self.__edit_menu = Menu(self.__menu, tearoff = 0)
        self.__help_menu = Menu(self.__menu, tearoff = 0)

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
        #self.__file_menu.add_command(label = "New")
        #self.__file_menu.add_command(label = "Open")
        #self.__file_menu.add_command(label = "Save")
        #self.__file_menu.add_separator()
        self.__file_menu.add_command(label = "Exit", command = self.__root.quit)
        self.__menu.add_cascade(label = "File", menu = self.__file_menu)
        # Edit Menu
        #self.__edit_menu.add_command(label = "Cut")
        #self.__edit_menu.add_command(label = "Copy")
        #self.__edit_menu.add_command(label = "Paste")
        #self.__menu.add_cascade(label = "Edit", menu = self.__edit_menu)
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

    def run(self):
        self.__root.mainloop()

if __name__ == "__main__":
    Helix().run()
