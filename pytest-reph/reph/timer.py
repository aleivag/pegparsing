import time


class Timer(object):
    NO_START = 0
    STARTED = 1
    STOPED = 3

    def __init__(self, name):
        self.name = name
        self.t0 = None
        self.tf = None
        self.sucess = None
        self.state = self.NO_START

    def start(self):
        assert self.state == self.NO_START
        self.state = self.STARTED
        self.t0 = time.time()

    def stop(self):
        assert self.state == self.STARTED
        self.state = self.STOPED
        self.tf = time.time()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exctype, excinst, exctb):
        self.stop()
        self.sucess = exctype is None
        return self.sucess
