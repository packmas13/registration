class Session(object):
    def __init__(self, responses):
        self.i = 0
        self.responses = responses

    def get(self, uri, params=None):
        r = self.responses[self.i]
        self.i += 1
        return r
