import datetime
import operator
import os
import re
import random
from functools import reduce

import numpy as np
import pandas as pd

from .helpers import create_df


class EmpaticaReader:
    signal_names = ['acc', 'bvp', 'eda', 'hr', 'temp']
    acc_names = ['acc_x', 'acc_y', 'acc_z']

    def __init__(self, path):
        self.init_filelist(path)
        self.start_times = {}
        self.sample_freqs = {}

        self.BVP = self._read_signal('bvp')
        self.EDA = self._read_signal('eda')
        self.HR = self._read_signal('hr')
        self.TEMP = self._read_signal('temp')
        self.ACC = self._read_acc()
        # Read inter beat intervals
        if os.stat(self.filelist['ibi']).st_size != 0:
            self.IBI = self._read_ibi()
        else:
            self.IBI = None
            print("IBI file is empty.")

        self._update_joined_dataframe()

    def write(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        self._write_signal(path, self.BVP)
        self._write_signal(path, self.EDA)
        self._write_signal(path, self.HR)
        self._write_signal(path, self.TEMP)
        self._write_acc(path)
        if self.IBI is not None:
            self._write_ibi(path)

    def _read_signal(self, signal_name):
        with open(self.filelist[signal_name]) as f:
            self.start_times[signal_name] = pd.Timestamp(float(f.readline()), unit='s')
            self.sample_freqs[signal_name] = float(f.readline())
            df = pd.read_csv(f, names=[signal_name])
            return df

    def _write_signal(self, dir_path, dataframe):
        signal_name = dataframe.columns[0]
        file_path = os.path.join(dir_path, f"{signal_name.upper()}.csv")
        with open(file_path, 'w') as f:
            f.write(f"{str(self.start_times[signal_name].value / 10 ** 9)}\n")
            f.write(f"{str(self.sample_freqs[signal_name])}\n")
            f.write('\n'.join([str(x) for x in dataframe[signal_name]]))

    def _read_acc(self):
        with open(self.filelist['acc']) as f:
            start_times = [pd.Timestamp(float(x), unit='s') for x in f.readline().split(', ')]
            sample_freqs = [float(x) for x in f.readline().split(', ')]
            self.start_times['acc'] = start_times[0]
            self.sample_freqs['acc'] = sample_freqs[0]
            df = pd.read_csv(f, names=['acc_x', 'acc_y', 'acc_z'])
            df['acc_mag'] = np.linalg.norm(df.to_numpy(), axis=1)
            return df

    def _write_acc(self, dir_path):
        file_path = os.path.join(dir_path, "ACC.csv")
        with open(file_path, 'w') as f:
            start_time_as_string = str(self.start_times['acc'].value / 10 ** 9)
            sample_freq_as_string = str(self.sample_freqs['acc'])
            f.write(', '.join([start_time_as_string] * 3) + '\n')
            f.write(', '.join([sample_freq_as_string] * 3) + '\n')
            f.write(self.ACC.drop(columns='acc_mag').to_csv(header=None, index=None))

    def _read_ibi(self):
        to_timedelta = lambda x: (pd.Timedelta(float(x), unit='s'))

        with open(self.filelist['ibi']) as f:
            self.start_times['ibi'] = pd.Timestamp(float(f.readline().split(',')[0]), unit='s')
            df = pd.read_csv(f, names=['timedeltas', 'ibis'], converters={0: to_timedelta, 1: to_timedelta})
            return df

    def _write_ibi(self, dir_path):
        file_path = os.path.join(dir_path, "IBI.csv")
        with open(file_path, 'w') as f:
            f.write(f"{self.start_times['ibi'].value / 1e9}, IBI\n")
            timedeltas = pd.to_numeric(self.IBI['timedeltas']) / 1e9
            ibis = pd.to_numeric(self.IBI['ibis']) / 1e9
            f.write(pd.concat([timedeltas, ibis], axis=1).to_csv(index=None, header=None))

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = pd.Timedelta(random.uniform(one_month, two_years))
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] -= random_timedelta
        if isinstance(shift, pd.Timestamp):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] = shift
        if isinstance(shift, pd.Timedelta):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] += shift

        self._update_joined_dataframe()

    def _update_joined_dataframe(self):
        raw_data = {
            'acc': self.ACC.copy(),
            'bvp': self.BVP.copy(),
            'eda': self.EDA.copy(),
            'hr': self.HR.copy(),
            'temp': self.TEMP.copy()
        }
        for signal_name in raw_data.keys():
            sample_interval_length = int(1e9 / self.sample_freqs[signal_name])
            timerange = pd.date_range(start=self.start_times[signal_name], periods=len(raw_data[signal_name]),
                                      freq=f"{sample_interval_length}N")
            raw_data[signal_name].index = timerange

        self.joined_dataframe = reduce(lambda df1, df2: df1.join(df2, how='outer', sort=True), raw_data.values())

    def init_filelist(self, path):
        self.filelist = {
            'acc': os.path.join(path, 'ACC.csv'),
            'bvp': os.path.join(path, 'BVP.csv'),
            'eda': os.path.join(path, 'EDA.csv'),
            'hr': os.path.join(path, 'HR.csv'),
            'ibi': os.path.join(path, 'IBI.csv'),
            'temp': os.path.join(path, 'TEMP.csv'),
        }
