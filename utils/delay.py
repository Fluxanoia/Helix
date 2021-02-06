
class DelayTracker:

    __instance = None

    __delays = []

    def addDelay(self, w, i):
        self.__delays.append((w, i))
    def endDelay(self, w, i):
        w.after_cancel(i)
        self.removeDelay(w, i)
    def removeDelay(self, w, i):
        if ((w, i) in self.__delays):
            self.__delays.remove((w, i))

    def endAll(self):
        for d in self.__delays:
            d[0].after_cancel(d[1])

    @staticmethod
    def getInstance():
        if DelayTracker.__instance is None:
            raise Exception("No instance of DelayTracker.")
        return DelayTracker.__instance

    def __init__(self):
        if DelayTracker.__instance is not None:
            raise Exception("Invalid initialistion of DelayTracker.")
        DelayTracker.__instance = self
