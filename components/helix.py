from tkinter import Tk, Menu
from tkinter.messagebox import showinfo, askyesno

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

        self.__root.bind("<Control-s>", lambda _e : self.__save_project(False))
        self.__root.bind("<Control-S>", self.__save_project)

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

        self.__file_loaded = False
        self.__file_changed = False

        self.__constructWindow()
        self.__constructMenu()
        self.__constructPanels()

        self.__root.lift()
    def __constructWindow(self):
        self.__set_title()
        self.__root.geometry('%dx%d+%d+%d' %
            (self.__width, self.__height,
            (self.__root.winfo_screenwidth() / 2) - (self.__width / 2),
            (self.__root.winfo_screenheight() / 2) - (self.__height / 2)))
        self.__root.wm_protocol("WM_DELETE_WINDOW", self.__root.quit)
    def __constructMenu(self):
        # File Menu
        self.__file_menu.add_command(label = "New Project", command = self.__new_project)
        self.__file_menu.add_command(label = "Save Project", command =
            lambda : self.__save_project(False))
        self.__file_menu.add_command(label = "Save As...", command = self.__save_project)
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
        self.__frame_viewer = EquationViewer(self.__root, self.__frame_split,
            self.__mark_changes)
        self.__frame_editor = EquationEditor(self.__root, self.__frame_split,
            self.__frame_viewer.plot, self.__mark_changes)

    @staticmethod
    def get_project_settings():
        return {
                EquationViewer.DIM_KEY : "2",
                EquationViewer.RECT_KEY : "-10 -10 20 20",
                EquationViewer.ELEV_KEY : "30",
                EquationViewer.AZIM_KEY : "-60",
                EquationViewer.CUBOID_KEY : "-10 -10 -10 20 20 20"
            }
    def __new_project(self):
        if self.__file_loaded and self.__file_changed:
            if not askyesno("Are you sure?", "Unsaved data will be lost!"): return
        settings = Helix.get_project_settings()
        self.__frame_viewer.set_settings(settings)
        self.__frame_editor.set_settings(settings)
        self.__files.new_project()
        self.__file_loaded = False
        self.__set_title()
    def __save_project(self, save_as = True):
        settings = {}
        self.__frame_viewer.add_settings(settings)
        self.__frame_editor.add_settings(settings)
        new_file = self.__files.save_project(settings, save_as)
        if not save_as and new_file:
            self.__file_changed = False
            self.__file_loaded = True
        elif not new_file is None and not new_file:
            self.__file_changed = False
        self.__set_title()
    def __load_project(self):
        settings = self.__files.load_project(Helix.get_project_settings())
        if not settings is None:
            self.__frame_viewer.set_settings(settings)
            self.__frame_editor.set_settings(settings)
            self.__file_loaded = True
            self.__file_changed = False
            self.__set_title()
    def __mark_changes(self):
        if self.__file_loaded:
            if not self.__file_changed:
                self.__file_changed = True
                self.__set_title()

    def __set_title(self):
        title = "Helix"
        if self.__file_loaded:
            title += " - " + self.__files.get_current_project_name()
            if self.__file_changed:
                title += "*"
        self.__root.title(title)

    def run(self): self.__root.mainloop()

if __name__ == "__main__":
    Helix().run()
