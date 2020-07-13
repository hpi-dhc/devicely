import pandas as pd

class TagReader:

    def __init__(self, path, timeshift=0):
        self.data = pd.read_csv(path, names=[None, 'time', 'tag'], index_col=0)
        self.data['time'] = pd.to_datetime(self.data['time'], format='%Y/%m/%d(%a) %H:%M:%S')
        self.data.set_index('time', inplace=True, verify_integrity=True)
        self.data.sort_index(inplace=True)
        self.data.index = self.data.index.shift(periods=-timeshift, freq='1H')