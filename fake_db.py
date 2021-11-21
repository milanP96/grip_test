import json


class Db:
    def __init__(self):
        f = open('data.json')
        self._data = json.load(f)
        f.close()

    def data(self):
        return self._data
