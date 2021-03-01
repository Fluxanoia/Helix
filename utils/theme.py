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

        self.__editor_body    = '#404040'
        self.__editor_divider = '#707070'

        self.__editor_button_body   = '#606060'
        self.__editor_button_active = '#808080'
        self.__editor_button_text   = '#FFFFFF'
        self.__editor_readout_text  = '#707070'

        self.__viewer_body        = '#202020'
        self.__viewer_button_body = '#606060'
        self.__viewer_text        = '#FFFFFF'

        self.__viewer_face  = '#202020'
        self.__viewer_spine = '#FFFFFF'

        self.__plot_colours = [(224, 82, 99), (3, 247, 235), (100, 87, 166),
            (99, 193, 50), (249, 200, 70)]

    def get_editor_body_colour(self):
        return self.__editor_body
    def get_editor_divider_colour(self):
        return self.__editor_divider
    def configure_editor_divider(self, w):
        w.configure(bg = self.__editor_divider)
        Theme.remove_border(w)
    def configure_editor(self, w):
        w.configure(bg = self.__editor_body)
        Theme.remove_border(w)
    def configure_editor_scale(self, w):
        w.config(bg = self.__editor_body, foreground = self.__editor_button_text)
        Theme.remove_border(w)
    def configure_editor_readout(self, w):
        w.configure(foreground = self.__editor_readout_text)
        Theme.remove_border(w)
    def configure_editor_button(self, w):
        w.configure(bg = self.__editor_button_body,
            activebackground = self.__editor_button_active,
            foreground = self.__editor_button_text)

    def configure_viewer(self, w):
        w.configure(bg = self.__viewer_body)
        Theme.remove_border(w)
    def configure_viewer_button(self, w):
        w.configure(bg = self.__viewer_button_body, foreground = self.__viewer_text)
    def configure_viewer_text(self, w):
        w.configure(bg = self.__viewer_body, foreground = self.__viewer_text)

    def configure_figure(self, f):
        f.patch.set_facecolor(self.__viewer_face)
    def configure_plot_2d(self, a):
        a.set_facecolor(self.__viewer_face)
        a.spines['left'].set_color(self.__viewer_spine)
        a.spines['bottom'].set_color(self.__viewer_spine)
        a.spines['right'].set_color('none')
        a.spines['top'].set_color('none')
        a.xaxis.label.set_color(self.__viewer_spine)
        a.yaxis.label.set_color(self.__viewer_spine)
        a.tick_params(axis = 'x', colors = self.__viewer_spine)
        a.tick_params(axis = 'y', colors = self.__viewer_spine)
    def configure_plot_3d(self, a):
        a.set_facecolor(self.__viewer_face)
        a.xaxis.label.set_color(self.__viewer_spine)
        a.xaxis.label.set_color(self.__viewer_spine)
        a.yaxis.label.set_color(self.__viewer_spine)
        a.zaxis.label.set_color(self.__viewer_spine)
        a.tick_params(axis = 'x', colors = self.__viewer_spine)
        a.tick_params(axis = 'y', colors = self.__viewer_spine)
        a.tick_params(axis = 'z', colors = self.__viewer_spine)
    def get_plot_colours(self):
        return self.__plot_colours

    @staticmethod
    def remove_border(w):
        w.configure(borderwidth = 0, highlightthickness = 0)
