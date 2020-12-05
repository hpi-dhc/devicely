from functools import reduce
import os
import random
import sys

import numpy as np
import pandas as pd


class EmpaticaReader:
    signal_names = ['acc', 'bvp', 'eda', 'hr', 'temp']
    acc_names = ['acc_x', 'acc_y', 'acc_z']

    def file_empty_or_not_existing(path):
        return not os.path.isfile(path) or os.stat(path).st_size == 0

    def __init__(self, path):
        self.init_filelist(path)
        self.start_times = {}
        self.sample_freqs = {}

        self.BVP = self._read_signal('bvp')
        self.EDA = self._read_signal('eda')
        self.HR = self._read_signal('hr')
        self.TEMP = self._read_signal('temp')
        self.ACC = self._read_acc()
        self.IBI = self._read_ibi()

        if not self.__class__.file_empty_or_not_existing(self.filelist['tags']):
            self.tags = pd.read_csv(self.filelist['tags'], header=None, parse_dates=[0],
                                    date_parser=lambda x: pd.Timestamp(float(x), unit='s'))
        else:
            self.tags = None

        self._update_joined_dataframe()

    def write(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        self._write_signal(path, self.BVP)
        self._write_signal(path, self.EDA)
        self._write_signal(path, self.HR)
        self._write_signal(path, self.TEMP)
        self._write_acc(path)
        self._write_ibi(path)

        if self.tags is not None:
            numeric_tags = pd.to_numeric(self.tags[0]) / 1e9
            numeric_tags.to_csv(os.path.join(path, 'tags.csv'), header=None, index=None)

    def _read_signal(self, signal_name):
        if self.__class__.file_empty_or_not_existing(self.filelist[signal_name]):
            print(f"File {self.filelist[signal_name]} is empty or doesn't exist. Skipping")
            return None
        with open(self.filelist[signal_name]) as f:
            self.start_times[signal_name] = pd.Timestamp(float(f.readline()), unit='s')
            self.sample_freqs[signal_name] = float(f.readline())
            df = pd.read_csv(f, names=[signal_name])
            df.index = pd.date_range(start=self.start_times[signal_name], freq=f"{1 / self.sample_freqs[signal_name]}S",
                                     periods=len(df))
            return df

    def _write_signal(self, dir_path, dataframe):
        if dataframe is not None:
            signal_name = dataframe.columns[0]
            file_path = os.path.join(dir_path, f"{signal_name.upper()}.csv")
            with open(file_path, 'w') as f:
                f.write(f"{str(self.start_times[signal_name].value / 10 ** 9)}\n")
                f.write(f"{str(self.sample_freqs[signal_name])}\n")
                f.write('\n'.join([str(x) for x in dataframe[signal_name]]))

    def _read_acc(self):
        if self.__class__.file_empty_or_not_existing(self.filelist['acc']):
            print(f"File {self.filelist['acc']} is empty or doesn't exist. Skipping")
            return None
        with open(self.filelist['acc']) as f:
            start_times = [pd.Timestamp(float(x), unit='s') for x in f.readline().split(', ')]
            sample_freqs = [float(x) for x in f.readline().split(', ')]
            self.start_times['acc'] = start_times[0]
            self.sample_freqs['acc'] = sample_freqs[0]
            df = pd.read_csv(f, names=self.acc_names)
            df['acc_mag'] = np.linalg.norm(df.to_numpy(), axis=1)
            df.index = pd.date_range(start=self.start_times['acc'], freq=f"{1 / self.sample_freqs['acc']}S",
                                     periods=len(df))
            return df

    def _write_acc(self, dir_path):
        if self.ACC is not None:
            file_path = os.path.join(dir_path, "ACC.csv")
            with open(file_path, 'w') as f:
                start_time_as_string = str(self.start_times['acc'].value / 10 ** 9)
                sample_freq_as_string = str(self.sample_freqs['acc'])
                f.write(', '.join([start_time_as_string] * 3) + '\n')
                f.write(', '.join([sample_freq_as_string] * 3) + '\n')
                f.write(self.ACC.drop(columns='acc_mag').to_csv(header=None, index=None))

    def _read_ibi(self):
        if self.__class__.file_empty_or_not_existing(self.filelist['ibi']):
            print(f"File {self.filelist['acc']} is empty or doesn't exist. Skipping")
            return None
        with open(self.filelist['ibi']) as f:
            self.start_times['ibi'] = pd.Timestamp(float(f.readline().split(',')[0]), unit='s')
            df = pd.read_csv(f, names=['timedelta', 'ibi'])
            df.index = self.start_times['ibi'] + pd.to_timedelta(df.timedelta, unit='s')
            df.index.name = None
            return df

    def _write_ibi(self, dir_path):
        if self.IBI is not None:
            file_path = os.path.join(dir_path, "IBI.csv")
            with open(file_path, 'w') as f:
                f.write(f"{self.start_times['ibi'].value / 1e9}, IBI\n")
                f.write(self.IBI.to_csv(index=None, header=None))

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('- 30 days').value
            two_years = pd.Timedelta('- 730 days').value
            random_timedelta = pd.Timedelta(random.uniform(one_month, two_years))
            self.timeshift(random_timedelta)

        dfs = [df for df in [self.BVP, self.EDA, self.HR, self.TEMP, self.ACC, self.IBI] if df is not None]

        if isinstance(shift, pd.Timestamp):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] = shift
            if self.tags is not None:
                timedeltas = self.tags - self.tags.loc[0, 0]
                self.tags = shift + timedeltas
            for df in dfs:
                timedeltas = df.index - df.index[0]
                df.index = shift + timedeltas

        if isinstance(shift, pd.Timedelta):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] += shift
            if self.tags is not None:
                self.tags += shift
            for df in dfs:
                df.index += shift

        self._update_joined_dataframe()

    def _update_joined_dataframe(self):
        dfs = [df for df in [self.BVP, self.EDA, self.HR, self.TEMP, self.ACC, self.IBI] if df is not None]
        self.data = reduce(lambda df1, df2: df1.join(df2, how='outer', sort=True), dfs)

    def init_filelist(self, path):
        self.filelist = {
            'acc': os.path.join(path, 'ACC.csv'),
            'bvp': os.path.join(path, 'BVP.csv'),
            'eda': os.path.join(path, 'EDA.csv'),
            'hr': os.path.join(path, 'HR.csv'),
            'ibi': os.path.join(path, 'IBI.csv'),
            'temp': os.path.join(path, 'TEMP.csv'),
            'tags': os.path.join(path, 'tags.csv')
        }