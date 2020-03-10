class Session(object):
    response = None
    exception = None

    def __init__(self, config):
        pass

    def get(self, uri, params=None):
        if self.exception:
            raise self.exception
        return self.response
