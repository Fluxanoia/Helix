class Theme:

    __instance = None

    __editor_body = '#404040'
    __editor_div = '#707070'

    __editor_button_body   = '#606060'
    __editor_button_active = '#808080'
    __editor_button_text   = '#FFFFFF'

    __viewer_body        = '#202020'
    __viewer_button_body = '#606060'
    __viewer_text        = '#FFFFFF'

    __viewer_face_color  = '#202020'
    __viewer_spine_color = '#FFFFFF'

    __tab_body = '#606060'

    __tab_button_body        = '#707070'
    __tab_button_body_active = '#808080'
    __tab_button_text        = '#FFFFFF'

    __variable_selector_body     = '#606060'
    __variable_selector_text     = '#FFFFFF'
    __variable_selector_checkbox = '#303030'

    def getEditorBody(self):
        return self.__editor_body
    def getEditorDivider(self):
        return self.__editor_div
    def configureEditorDivider(self, w):
        w.configure(bg = self.getEditorDivider())
        self.removeBorder(w)
    def configureEditor(self, w):
        w.configure(bg = self.getEditorBody())
        self.removeBorder(w)

    def getEditorButtonBody(self):
        return self.__editor_button_body
    def getEditorButtonBodyActive(self):
        return self.__editor_button_active
    def getEditorButtonText(self):
        return self.__editor_button_text
    def configureEditorButton(self, w):
        w.configure(bg = self.getEditorButtonBody(),
            activebackground = self.getEditorButtonBodyActive(),
            foreground = self.getEditorButtonText())

    def getViewerBody(self):
        return self.__viewer_body
    def getViewerButtonBody(self):
        return self.__viewer_button_body
    def getViewerText(self):
        return self.__viewer_text
    def configureViewer(self, w):
        w.configure(bg = self.getViewerBody())
        self.removeBorder(w)
    def configureViewerButton(self, w):
        w.configure(bg = self.getViewerButtonBody(),
            foreground = self.getViewerText())
    def configureViewerText(self, w):
        w.configure(bg = self.getViewerBody(),
            foreground = self.getViewerText())

    def getViewerFace(self):
        return self.__viewer_face_color
    def getViewerSpine(self):
        return self.__viewer_spine_color
    def configureFigure(self, f):
        f.patch.set_facecolor(self.getViewerFace())
    def configurePlot2D(self, a):
        a.set_facecolor(self.getViewerFace())

        a.spines['left'].set_color(self.getViewerSpine())
        a.spines['bottom'].set_color(self.getViewerSpine())
        a.spines['right'].set_color('none')
        a.spines['top'].set_color('none')

        a.xaxis.label.set_color(self.getViewerSpine())
        a.yaxis.label.set_color(self.getViewerSpine())
        a.tick_params(axis = 'x', colors = self.getViewerSpine())
        a.tick_params(axis = 'y', colors = self.getViewerSpine())

    def configurePlot3D(self, a):
        a.set_facecolor(self.getViewerFace())

        a.xaxis.label.set_color(self.getViewerSpine())
        a.xaxis.label.set_color(self.getViewerSpine())
        a.yaxis.label.set_color(self.getViewerSpine())
        a.zaxis.label.set_color(self.getViewerSpine())
        a.tick_params(axis = 'x', colors = self.getViewerSpine())
        a.tick_params(axis = 'y', colors = self.getViewerSpine())
        a.tick_params(axis = 'z', colors = self.getViewerSpine())

    def getTabBody(self):
        return self.__tab_body
    def configureTabBar(self, w):
        w.configure(bg = self.getTabBody())
        self.removeBorder(w)

    def getTabButtonBody(self):
        return self.__tab_button_body
    def getTabButtonBodyActive(self):
        return self.__tab_button_body_active
    def getTabButtonText(self):
        return self.__tab_button_text
    def configureTabButton(self, w):
        w.configure(bg = self.getTabButtonBody(),
            activebackground = self.getTabButtonBodyActive(),
            foreground = self.getTabButtonText())

    def getVariableSelectorBody(self):
        return self.__variable_selector_body
    def getVariableSelectorText(self):
        return self.__variable_selector_text
    def getVariableSelectorCheckbox(self):
        return self.__variable_selector_checkbox
    def configureVariableSelector(self, w):
        w.configure(bg = self.getVariableSelectorBody())
        self.removeBorder(w)
    def configureVariableSelectorText(self, w):
        w.configure(bg = self.getVariableSelectorBody(),
            foreground = self.getVariableSelectorText())
    def configureVariableSelectorCheckbox(self, w):
        w.configure(bg = self.getVariableSelectorBody(),
            foreground = self.getVariableSelectorText(),
            selectcolor = self.getVariableSelectorCheckbox())

    def removeBorder(self, w):
        w.configure(borderwidth = 0,
            highlightthickness = 0)

    @staticmethod
    def getInstance():
        if Theme.__instance is None:
            raise Exception("No instance of Theme.")
        return Theme.__instance

    def __init__(self):
        if Theme.__instance is not None:
            raise Exception("Invalid initialistion of Theme.")
        Theme.__instance = self
