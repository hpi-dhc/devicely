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
        signals = {}
        start_times = {}
        sample_freqs = {}

        for signal in self.signal_names:
            filename = self.filelist[signal]
            with open(filename, 'r') as f:
                ts_line = f.readline()
                start_times[signal] = int(ts_line[:ts_line.find('.')])
                sf_line = f.readline()
                sample_freqs[signal] = int(sf_line[:sf_line.find('.')])
                split = re.split('[,\n]', f.read())
                split = np.array(split[:-1]).astype(float)
                if signal == 'acc':
                    for index, axis in enumerate(self.acc_names):
                        signals[axis] = split[index::3]
                        sample_freqs[axis] = sample_freqs[signal]
                        start_times[axis] = start_times[signal]
                    del start_times[signal]
                    del sample_freqs[signal]
                    continue
                signals[signal] = split

        signals['acc_mag'] = np.linalg.norm([signals['acc_x'], signals['acc_y'], signals['acc_z']], axis=0)
        sample_freqs['acc_mag'] = sample_freqs['acc_x']
        start_times['acc_mag'] = start_times['acc_x']

        signal_names = self.signal_names.copy()
        signal_names.remove('acc')
        signal_names = signal_names + self.acc_names + ['acc_mag']

        self.signal_names = signal_names
        self.signals = signals
        self.sample_freqs = sample_freqs
        self.start_times = start_times

        # Read inter beat intervals
        if os.stat(self.filelist['ibi']).st_size != 0:
            ibi_filename = self.filelist['ibi']
            with open(ibi_filename, 'r') as f:
                ts_line = f.readline()
                start_time = pd.to_datetime(int(ts_line[:ts_line.find('.')]), unit='s')
                split = re.split('[,\n]', f.read())
                ibis = np.array(split[1:-1:2]).astype(float)
                timedeltas = list(map(lambda x: pd.Timedelta(x, unit='s'), np.array(split[:-1:2]).astype(float)))
                self.ibi_data = {
                    "start_time": start_time,
                    "ibis": ibis,
                    "timedeltas": timedeltas
                }
        else:
            self.ibi_data = None
            print("IBI file is empty.")

        self.data = self.get_dataframe(signal_names, signals, sample_freqs, start_times, ibi_data=self.ibi_data)

    def get_dataframe(self, signal_names, signals, sample_freqs, start_times, ibi_data=None):
        df = create_df(signal_names, signals, sample_freqs, start_times)
        if ibi_data is not None:
            ibi_timestamps = list(map(lambda x: ibi_data["start_time"] + x, ibi_data["timedeltas"]))
            df_ibi = pd.DataFrame({'ibi': ibi_data["ibis"]}, index=ibi_timestamps)
            df = df.join(df_ibi, how='outer')

        return df

    def write(self, path, as_dataframe=False):
        if as_dataframe:
            self.data.to_csv(path_or_buf=path)
        else:
            empatica_path = os.path.join(path, "Empatica")
            os.mkdir(empatica_path)
            for signal_name in ['acc', 'bvp', 'eda', 'hr', 'temp']:
                file_path = os.path.join(empatica_path, f"{signal_name.upper()}.csv")
                with open(file_path, 'w') as f:
                    if signal_name == "acc":
                        starting_times = [self.start_times[axis] for axis in self.acc_names]
                        sample_freqs = [self.sample_freqs[axis] for axis in self.acc_names]
                        signals = np.array([self.signals[axis] for axis in self.acc_names]).T
                        acc_data = np.row_stack([starting_times, sample_freqs, signals])
                        pd.DataFrame(acc_data).to_csv(file_path, header=None, index=None)
                    else:
                        f.write(str(self.start_times[signal_name]) + '\n')
                        f.write(str(self.sample_freqs[signal_name]) + '\n')
                        f.write('\n'.join([str(x) for x in self.signals[signal_name]]))

    def init_filelist(self, path):
        self.filelist = {
            'acc': os.path.join(path, 'ACC.csv'),
            'bvp': os.path.join(path, 'BVP.csv'),
            'eda': os.path.join(path, 'EDA.csv'),
            'hr': os.path.join(path, 'HR.csv'),
            'ibi': os.path.join(path, 'IBI.csv'),
            'temp': os.path.join(path, 'TEMP.csv'),
        }
