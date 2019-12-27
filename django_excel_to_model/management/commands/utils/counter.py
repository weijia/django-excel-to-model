

class Counter(object):
    def __init__(self, init=0, notification_interval=1000):
        super(Counter, self).__init__()
        self.cnt = init
        self.init = init
        self.notification_interval = notification_interval
        if self.notification_interval:
            print("Start counting: %d/%d" % (self.init-self.cnt, self.init))

    def decrease(self):
        self.cnt -= 1
        if self.notification_interval and ((self.init-self.cnt) % self.notification_interval == 0):
            print("Current: %d/%d" % (self.init-self.cnt, self.init))

    def is_equal_or_below(self, value):
        return self.cnt <= value

    def reset(self):
        self.cnt = self.init
