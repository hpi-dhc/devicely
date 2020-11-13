import random

import pandas as pd

class TagReader:
    def __init__(self, path):
        self.data = pd.read_csv(path, names=['tag_number', 'time', 'tag'])
        self.data['time'] = pd.to_datetime(self.data['time'], format='%Y/%m/%d(%a) %H:%M:%S')
        self.data.set_index('time', inplace=True, verify_integrity=True)
        self.data.sort_index(inplace=True)

    def write(self, path):
        df_to_write = self.data.reset_index()[['tag_number', 'time', 'tag']]
        df_to_write.time = df_to_write.time.dt.strftime("%Y/%-m/%-d(%a)\u3000%H:%M:%S").str.lower()
        df_to_write.to_csv(path, header=None, index=None)

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = - pd.Timedelta(random.uniform(one_month, two_years)).round('s')
            self.timeshift(random_timedelta)
        if isinstance(shift, pd.Timedelta):
            self.data.index += shift
        if isinstance(shift, pd.Timestamp):
            timedeltas = self.data.index - self.data.index[0]
            self.data.index = shift + timedeltas
