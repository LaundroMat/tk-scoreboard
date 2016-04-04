class Contestant(object):
    def __init__(self, name, score=0):
        self.name = name
        self.score = score

    def __unicode__(self):
        return self.name
