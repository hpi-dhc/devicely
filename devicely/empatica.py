import datetime
import os
import re
import numpy as np
import pandas as pd

from .helpers import create_df


class EmpaticaReader:
    signal_names = ['acc', 'bvp', 'eda', 'hr', 'temp']
    acc_names = ['acc_x', 'acc_y', 'acc_z']

    def __init__(self, path):
        self.init_filelist(path)
        self.signals = {}
        self.start_times = {}
        self.sample_freqs = {}

        for signal in self.signal_names:
            filename = self.filelist[signal]
            split = pd.read_csv(filename, header=None).to_numpy()
            if signal == 'acc':
                for index, axis in enumerate(self.acc_names):
                    self.start_times[axis] = pd.Timestamp(split[0, index], unit='s')
                    self.sample_freqs[axis] = split[1, index]
                    self.signals[axis] = split[2:, index]
            else:
                self.start_times[signal] = pd.Timestamp(split[0, 0], unit='s')
                self.sample_freqs[signal] = split[1, 0]
                self.signals[signal] = split[2:, 0]

            # signals[signal] = split

        self.signals['acc_mag'] = np.linalg.norm([self.signals['acc_x'], self.signals['acc_y'], self.signals['acc_z']],
                                                 axis=0)
        self.sample_freqs['acc_mag'] = self.sample_freqs['acc_x']
        self.start_times['acc_mag'] = self.start_times['acc_x']

        # Read inter beat intervals
        if os.stat(self.filelist['ibi']).st_size != 0:
            ibi_df = pd.read_csv(self.filelist['ibi'], header=None)
            start_time = pd.Timestamp(ibi_df.iloc[0, 0], unit='s')
            timedeltas = pd.to_timedelta(ibi_df.iloc[1:, 0], unit='s')
            ibis = pd.to_timedelta(ibi_df.iloc[1:, 1].astype('float'), unit='s')
            self.ibi_data = {
                "start_time": start_time,
                "ibis": ibis,
                "timedeltas": timedeltas
            }
        else:
            self.ibi_data = None
            print("IBI file is empty.")

        # self.data = self.get_dataframe(signal_names, signals, sample_freqs, start_times, ibi_data=self.ibi_data)

    def timeshift(self, value):
        if isinstance(value, pd.Timestamp):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] = value
            self.ibi_data["start_time"] = value
        if isinstance(value, pd.Timedelta):
            for signal_name in self.start_times.keys():
                self.start_times[signal_name] += value
            self.ibi_data["start_time"] += value

    def get_dataframe(self, signal_names, signals, sample_freqs, start_times, ibi_data=None):
        df = create_df(signal_names, signals, sample_freqs, start_times)
        if ibi_data is not None:
            ibi_timestamps = list(map(lambda x: ibi_data["start_time"] + x, ibi_data["timedeltas"]))
            df_ibi = pd.DataFrame({'ibi': ibi_data["ibis"]}, index=ibi_timestamps)
            df = df.join(df_ibi, how='outer')

        return df

    def write(self, path):
        empatica_path = os.path.join(path, "Empatica")
        os.mkdir(empatica_path)
        for signal_name in self.signal_names:
            file_path = os.path.join(empatica_path, f"{signal_name.upper()}.csv")
            with open(file_path, 'w') as f:
                if signal_name == "acc":
                    starting_times = [self.start_times[axis].value / 10 ** 9 for axis in self.acc_names]
                    sample_freqs = [self.sample_freqs[axis] for axis in self.acc_names]
                    signals = np.array([self.signals[axis] for axis in self.acc_names]).T
                    acc_data = np.row_stack([starting_times, sample_freqs, signals])
                    pd.DataFrame(acc_data).to_csv(file_path, header=None, index=None)
                else:
                    f.write(str(self.start_times[signal_name].value / 10 ** 9) + '\n')
                    f.write(str(self.sample_freqs[signal_name]) + '\n')
                    f.write('\n'.join([str(x) for x in self.signals[signal_name]]))

        #Write inter beat intervals
        if self.ibi_data is not None:
            file_path = os.path.join(empatica_path, "IBI.csv")
            df = pd.DataFrame({
                self.ibi_data["start_time"].value / 10**9: [x.value / 10**9 for x in self.ibi_data["timedeltas"]],
                "IBI": [timedelta.value / 10**9 for timedelta in self.ibi_data["ibis"]]
            })
            df.to_csv(file_path, index=None)

    def init_filelist(self, path):
        self.filelist = {
            'acc': os.path.join(path, 'ACC.csv'),
            'bvp': os.path.join(path, 'BVP.csv'),
            'eda': os.path.join(path, 'EDA.csv'),
            'hr': os.path.join(path, 'HR.csv'),
            'ibi': os.path.join(path, 'IBI.csv'),
            'temp': os.path.join(path, 'TEMP.csv'),
        }
