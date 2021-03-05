import os

from tkinter import filedialog
from tkinter.messagebox import showinfo

class FileManager:

    __instance = None

    DELIM = ":"
    PROJECT_EXT = ".hx"

    @staticmethod
    def get_instance():
        if FileManager.__instance is None:
            raise Exception("No instance of FileManager.")
        return FileManager.__instance

    def __init__(self):
        if FileManager.__instance is not None:
            raise Exception("Invalid initialistion of FileManager.")
        else:
            FileManager.__instance = self

    def __mkdirs(self, path):
        os.makedirs(os.path.dirname(path), exist_ok = True)
    def __exists(self, path):
        return os.path.exists(path)

    def __file_to_dict(self, path, default = None):
        data = {}
        with open(path, 'r') as file:
            for line in file:
                args = line.split(FileManager.DELIM, 1)
                if len(args) == 2:
                    data[args[0]] = args[1].strip('\n')
        rewrite = False
        if not default is None:
            for k in default.keys():
                if not k in data:
                    rewrite = True
                    data[k] = default[k]
        if rewrite: self.__overwrite_file(path, data)
        return data

    def load_file(self, name, default = None):
        return self.__load_file(self.get_files_path(name), default)
    def __load_file(self, path, default = None):
        if not self.__exists(path):
            if not default is None: self.__overwrite_file(path, default)
            return default
        return self.__file_to_dict(path, default)

    def overwrite_file(self, name, content):
        self.__overwrite_file(self.get_files_path(name), content)
    def __overwrite_file(self, path, content):
        if not self.__exists(path):
            self.__mkdirs(path)
        with open(path, 'w+') as file:
            for (x, y) in content.items():
                file.write(str(x) + FileManager.DELIM + str(y) + "\n")

    def load_project(self):
        path = filedialog.askopenfilename(title = "Loading a Project",
            filetypes = [("Helix Project Files", "*" + FileManager.PROJECT_EXT)],
            defaultextension = FileManager.PROJECT_EXT)
        data = None
        try:
            data = self.__load_file(path)
            if data is None:
                raise ValueError("No data found, does the file exist?")
        except Exception as e:
            showinfo("Helix Graphing Tool - Project Open Error",
                "Could not open the requested project:\n" + str(e))
        return data
    def save_project(self):
        path = filedialog.asksaveasfilename(title = "Saving the Project",
            filetypes = [("Helix Project Files", "*" + FileManager.PROJECT_EXT)],
            defaultextension = FileManager.PROJECT_EXT)
        try:
            self.__overwrite_file(path, {})
        except Exception as e:
            showinfo("Helix Graphing Tool - Project Save Error",
                "Could not save the project:\n" + str(e))

    @staticmethod
    def get_files_path(*args):
        return FileManager.get_path("files", *args)

    @staticmethod
    def get_path(*args):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), *args)
    