import os
from tkinter import *
from tkinter.messagebox import showinfo

from equation import Equation
from fonts import FontManager
from images import ImageManager
from scrollableFrame import ScrollableFrame

class Helix:

    # Root
    __root = Tk()

    # Managers
    __fonts = FontManager(__root)
    __images = ImageManager()

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
    __frame_viewer = Frame(__root, bg = '#353535')
    __frame_split = 0.2
    __add_button_split = 0.05
    
    # Editor Entries
    __entry_width = None
    __entry_button = None
    __entries = []

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
        self.__file_menu.add_command(label = "Exit", command = lambda : self.__root.destroy())
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
        # Editor 
        self.__frame_editor = ScrollableFrame(self.__root, 
            self.__frameEditorConfig,
            bg = '#505050', 
            borderwidth = 0,
            highlightthickness = 0)
        self.__frame_editor.place(relwidth = self.__frame_split, 
            relheight = 1 - self.__add_button_split)
        # Viewer
        self.__frame_viewer.place(relx = self.__frame_split, 
            relwidth = 1 - self.__frame_split, 
            relheight = 1)
        # Entry Adding Button
        self.__entry_button = Button(self.__root, 
            text = "+",
            font = self.__fonts.getTextFont(),
            command = self.__addEntry)
        self.__entry_button.place(
            rely = 1 - self.__add_button_split, 
            relwidth = self.__frame_split, 
            relheight = self.__add_button_split)

    def run(self): 
        self.__root.after(1, self.update)
        self.__root.mainloop()

    def __frameEditorConfig(self, width):
        self.__entry_width = width
        for e in self.__entries: e.configure(width = self.__entry_width)

    def __addEntry(self): 
        self.__entries.append(Equation(
            self.__frame_editor.getInnerFrame(),
            lambda e : self.__entries.remove(e)))
        self.__entries[-1].configure(width = self.__entry_width)

    def update(self):
        self.__root.after(20, self.update)

helix = Helix()
helix.run()
