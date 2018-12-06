

class Counter(object):
    def __init__(self, init=0):
        super(Counter, self).__init__()
        self.cnt = init
        self.init = init

    def decrease(self):
        self.cnt -= 1

    def is_equal_or_below(self, value):
        return self.cnt <= value

    def reset(self):
        self.cnt = self.init
