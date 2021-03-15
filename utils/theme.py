from utils.fonts import FontManager

class Theme:

    __instance = None

    @staticmethod
    def get_instance():
        if Theme.__instance is None:
            raise Exception("No instance of Theme.")
        return Theme.__instance

    def __init__(self):
        if Theme.__instance is not None:
            raise Exception("Invalid initialistion of Theme.")
        Theme.__instance = self

        self.__body_text      = '#222222'
        self.__body_disabled  = '#333333'
        self.__body           = '#444444'
        self.__body_button    = '#777777'
        self.__body_highlight = '#777777'
        self.__body_active    = '#888888'

        self.__body_viewer = '#222222'

        self.__text           = '#FFFFFF'
        self.__text_disabled  = '#EEEEEE'
        self.__text_select_fg = '#FFFFFF'
        self.__text_select_bg = '#AAAAAA'

        self.__plot_colours = [(224, 82, 99), (3, 247, 235), (100, 87, 166),
            (99, 193, 50), (249, 200, 70)]

    def get_body_colour(self):
        return self.__body
    def get_body_highlight_colour(self):
        return self.__body_highlight
    def configure_editor(self, w):
        w.configure(bg = self.__body)
        Theme.remove_border(w)

    def configure_button(self, w):
        w.configure(bg = self.__body_button,
            activebackground = self.__body_active)
        self.__configure_text(w)
    def configure_label(self, w):
        w.configure(bg = self.__body)
        self.__configure_text(w)
    def configure_entry(self, w):
        w.configure(bg = self.__body_text,
            disabledbackground = self.__body_disabled,
            disabledforeground = self.__text_disabled,
            insertbackground = self.__text,
            selectbackground = self.__text_select_bg,
            selectforeground = self.__text_select_fg)
        self.__configure_text(w)
    def configure_scale(self, w):
        w.config(bg = self.__body, foreground = self.__text)
        Theme.remove_border(w)

    def configure_divider(self, w):
        w.configure(bg = self.__body_highlight)
        Theme.remove_border(w)
    def configure_viewer(self, w):
        w.configure(bg = self.__body_viewer)
        Theme.remove_border(w)
    def configure_colour_window(self, w):
        w.configure(bg = self.__body, highlightcolor = self.__body_highlight)

    def configure_figure(self, f):
        f.patch.set_facecolor(self.__body_viewer)
    def configure_plot_2d(self, a):
        a.set_facecolor(self.__body_viewer)
        a.spines['left'].set_color(self.__text)
        a.spines['bottom'].set_color(self.__text)
        a.spines['right'].set_color('none')
        a.spines['top'].set_color('none')
        a.xaxis.label.set_color(self.__text)
        a.yaxis.label.set_color(self.__text)
        a.tick_params(axis = 'x', colors = self.__text)
        a.tick_params(axis = 'y', colors = self.__text)
    def configure_plot_3d(self, a):
        a.set_facecolor(self.__body_viewer)
        a.xaxis.label.set_color(self.__text)
        a.xaxis.label.set_color(self.__text)
        a.yaxis.label.set_color(self.__text)
        a.zaxis.label.set_color(self.__text)
        a.tick_params(axis = 'x', colors = self.__text)
        a.tick_params(axis = 'y', colors = self.__text)
        a.tick_params(axis = 'z', colors = self.__text)
    def get_plot_colours(self):
        return self.__plot_colours

    def __configure_text(self, w):
        w.configure(foreground = self.__text)
        FontManager.get_instance().configure_text(w)

    @staticmethod
    def remove_border(w):
        w.configure(borderwidth = 0, highlightthickness = 0)
