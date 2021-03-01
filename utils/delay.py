
class DelayTracker:

    __instance = None

    @staticmethod
    def get_instance():
        if DelayTracker.__instance is None:
            raise Exception("No instance of DelayTracker.")
        return DelayTracker.__instance

    def __init__(self):
        if DelayTracker.__instance is not None:
            raise Exception("Invalid initialistion of DelayTracker.")
        DelayTracker.__instance = self
        self.__delays = []

    def add_delay(self, w, i):
        self.__delays.append((w, i))
    def end_delay(self, w, i):
        w.after_cancel(i)
        self.remove_delay(w, i)
    def remove_delay(self, w, i):
        if (w, i) in self.__delays:
            self.__delays.remove((w, i))

    def end_all(self):
        for d in self.__delays:
            d[0].after_cancel(d[1])
