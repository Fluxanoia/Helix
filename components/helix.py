from tkinter import Tk, Menu
from tkinter.messagebox import showinfo

from utils.fonts import FontManager
from utils.images import ImageManager
from utils.parsing import Parser

from components.equationEditor import EquationEditor
from components.equationViewer import EquationViewer

class Helix:

    # Root
    __root = Tk()

    # Managers
    __fonts = FontManager(__root)
    __images = ImageManager()
    __parser = Parser()

    # Dimensions
    __width = 1280
    __height = 720

    # Menu Bar Widgets
    __menu = Menu(__root)
    __file_menu = Menu(__menu, tearoff = 0)
    __edit_menu = Menu(__menu, tearoff = 0)
    __help_menu = Menu(__menu, tearoff = 0)

    # Main Frames
    __frame_editor = None
    __frame_viewer = None
    __frame_split = 0.2

    def __init__(self):
        self.__constructWindow()
        self.__constructMenu()
        self.__constructPanels()

    def __constructWindow(self):
        self.__root.title("Helix Graphing Tool")
        self.__root.geometry('%dx%d+%d+%d' %
            (self.__width, self.__height,
            (self.__root.winfo_screenwidth() / 2) - (self.__width / 2),
            (self.__root.winfo_screenheight() / 2) - (self.__height / 2)))

    def __constructMenu(self):
        # File Menu
        self.__file_menu.add_command(label = "New")
        self.__file_menu.add_command(label = "Open")
        self.__file_menu.add_command(label = "Save")
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label = "Exit", command = Tk.quit)
        self.__menu.add_cascade(label = "File", menu = self.__file_menu)
        # Edit Menu
        self.__edit_menu.add_command(label = "Cut")
        self.__edit_menu.add_command(label = "Copy")
        self.__edit_menu.add_command(label = "Paste")
        self.__menu.add_cascade(label = "Edit", menu = self.__edit_menu)
        # About Button
        self.__menu.add_command(label = "About", command = lambda :
            showinfo("Helix Graphing Tool", "Written by Tyler Wright\n"
                + "with Matplotlib and SymPy\n"
                + "\nwww.fluxanoia.co.uk"))
        # Root config
        self.__root.config(menu = self.__menu)

    def __constructPanels(self):
        self.__frame_editor = EquationEditor(self.__root,
            self.__frame_split,
            bg = '#757575',
            borderwidth = 0,
            highlightthickness = 0)
        self.__frame_viewer = EquationViewer(self.__root,
            self.__frame_split,
            bg = '#505050',
            borderwidth = 0,
            highlightthickness = 0)

    def run(self):
        self.__root.mainloop()

if __name__ == "__main__":
    Helix().run()
