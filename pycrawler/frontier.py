__author__ = 'mengpeng'


class Frontier(object):

    def __init__(self):
        pass

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError


class DefaultFrontier(Frontier):

    def __init__(self, tasks=None):
        super(DefaultFrontier, self).__init__()
        self._tasks = tasks if tasks else []

    def __len__(self):
        return len(self._tasks)

    def __iter__(self):
        return iter(self._tasks)