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

        df = create_df(signal_names, signals, sample_freqs, start_times)

        # Read inter beat intervals
        if os.stat(self.filelist['ibi']).st_size != 0:
            ibi_filename = self.filelist['ibi']
            with open(ibi_filename, 'r') as f:
                ts_line = f.readline()
                start_time = pd.to_datetime(int(ts_line[:ts_line.find('.')]), unit='s')
                split = re.split('[,\n]', f.read())
                ibis = np.array(split[1:-1:2]).astype(float)
                timedeltas = list(map(lambda x: pd.Timedelta(x, unit='s'), np.array(split[:-1:2]).astype(float)))
                timestamps = list(map(lambda x: start_time + x, timedeltas))
                df_ibi = pd.DataFrame({'ibi': ibis}, index=timestamps)
            self.data = df.join(df_ibi, how='outer')
        else:
            self.data = df
            print("IBI file is empty.")

    def init_filelist(self, path):
        self.filelist = {
            'acc': os.path.join(path, 'ACC.csv'),
            'bvp': os.path.join(path, 'BVP.csv'),
            'eda': os.path.join(path, 'EDA.csv'),
            'hr': os.path.join(path, 'HR.csv'),
            'ibi': os.path.join(path, 'IBI.csv'),
            'temp': os.path.join(path, 'TEMP.csv'),
        }
