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
        empatica_dir_path = os.path.join(path, 'Empatica')
        os.mkdir(empatica_dir_path)
        self._write_signal(empatica_dir_path, self.BVP)
        self._write_signal(empatica_dir_path, self.EDA)
        self._write_signal(empatica_dir_path, self.HR)
        self._write_signal(empatica_dir_path, self.TEMP)
        self._write_acc(empatica_dir_path)
        if self.IBI is not None:
            self._write_ibi(empatica_dir_path)

    def _read_signal(self, signal_name):
        raw_signal_data = pd.read_csv(self.filelist[signal_name], header=None, float_precision='round_trip')
        self.start_times[signal_name] = pd.Timestamp(raw_signal_data.iloc[0, 0], unit='s')
        self.sample_freqs[signal_name] = raw_signal_data.iloc[1, 0]
        return pd.DataFrame({signal_name: raw_signal_data.iloc[2:, 0]})

    def _write_signal(self, dir_path, dataframe):
        signal_name = dataframe.columns[0]
        file_path = os.path.join(dir_path, f"{signal_name.upper()}.csv")
        with open(file_path, 'w') as f:
            f.write(f"{str(self.start_times[signal_name].value / 10 ** 9)}\n")
            f.write(f"{str(self.sample_freqs[signal_name])}\n")
            f.write('\n'.join([str(x) for x in dataframe[signal_name]]))

    def _read_acc(self):
        raw_signal_data = pd.read_csv(self.filelist['acc'], header=None)
        signal_dict = dict()
        for index, axis in enumerate(self.acc_names):
            self.start_times[axis] = pd.Timestamp(raw_signal_data.iloc[0, index], unit='s')
            self.sample_freqs[axis] = raw_signal_data.iloc[1, index]
            signal_dict[axis] = raw_signal_data.iloc[2:, index]
        signal_dict['acc_mag'] = np.linalg.norm(
            [signal_dict['acc_x'], signal_dict['acc_y'], signal_dict['acc_z']],
            axis=0)
        self.sample_freqs['acc_mag'] = self.sample_freqs['acc_x']
        self.start_times['acc_mag'] = self.start_times['acc_x']
        self.sample_freqs['acc'] = self.sample_freqs['acc_x']
        self.start_times['acc'] = self.start_times['acc_x']

        return pd.DataFrame(signal_dict)

    def _write_acc(self, dir_path):
        file_path = os.path.join(dir_path, "ACC.csv")
        with open(file_path, 'w') as f:
            f.write(', '.join([str(self.start_times[axis].value / 10 ** 9) for axis in self.acc_names]) + '\n')
            f.write(f"{self.sample_freqs['acc_x']}, {self.sample_freqs['acc_y']}, {self.sample_freqs['acc_z']}\n")
            f.write(self.ACC.drop(columns='acc_mag').to_csv(header=None, index=None))

    def _read_ibi(self):
        raw_ibi_data = pd.read_csv(self.filelist['ibi'], header=None)
        self.start_times['ibi'] = pd.Timestamp(raw_ibi_data.iloc[0, 0], unit='s')
        return pd.DataFrame({
            "timedeltas": pd.to_timedelta(raw_ibi_data.iloc[1:, 0], unit='s'),
            "ibis": pd.to_timedelta(raw_ibi_data.iloc[1:, 1].astype('float'), unit='s')
        })

    def _write_ibi(self, dir_path):
        file_path = os.path.join(dir_path, "IBI.csv")
        with open(file_path, 'w') as f:
            f.write(f"{self.start_times['ibi'].value / 10e9}, IBI\n")
            timedeltas = pd.to_numeric(self.IBI['timedeltas']) / 10e9
            ibis = pd.to_numeric(self.IBI['ibis']) / 10e9
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
