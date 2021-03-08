from datetime import datetime
import glob
import json
import os
import random

import numpy as np
import pandas as pd
import pyedflib


class FarosReader:

    #signal_names = ['ECG', 'HRV', 'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'acc_mag']
    def __init__(self, path):
        file_extension = os.path.splitext(path)[-1].lower()
        if file_extension == '.edf':
            self._read_from_edf(path)
        elif file_extension == '.csv':
            self._read_from_csv(path)
        else:
            raise ValueError(f"Wrong file extension. Expected one of [.edf, .csv]. Got {file_extension}.")

    def write(self, path):
        self._write_to_csv(path)

    def _read_from_edf(self, path):
        with pyedflib.EdfReader(path) as reader:
            self.data = pd.DataFrame()
            self.sample_freqs = dict()

            # Start time is identical for all signals
            self.start_time = pd.Timestamp(reader.getStartdatetime())

            # Creating a date_range index takes long and some signals have duplicate lengths and sample frequencies.
            # Thus we reuse indices to avoid long computation times.
            indices = dict()

            for i in range(len(reader.getSignalLabels())):
                label = reader.getLabel(i)
                sample_freq = pd.DateOffset(seconds=1/reader.getSampleFrequency(i))
                self.sample_freqs[label] = sample_freq
                signals = reader.readSignal(i)
                signal_length = len(signals)
                if (sample_freq, signal_length) not in indices:
                    indices[(sample_freq, signal_length)] = pd.date_range(start=self.start_time,
                                                                     periods=signal_length,
                                                                     freq=sample_freq)
                series = pd.Series(signals, index=indices[(sample_freq, signal_length)], name=label)
                self.data = self.data.join(series, how='outer')

            self.data.index.name = 'time'

            self._add_acc_mag()

    def _write_to_csv(self, path):
        with open(path, 'w') as f:
            json.dump({'start_time': int(self.start_time.value / 1e9),
                       'sample_freqs': {label: 1/dateoffset.seconds for label, dateoffset in self.sample_freqs.items()}}, f)
            f.write('\n')
            self.data.to_csv(f)

    def _read_from_csv(self, path):
        with open(path, 'r') as f:
            metadata = json.loads(f.readline())
            self.start_time = pd.Timestamp(metadata['start_time'], unit='s')
            self.sample_freqs = {label: pd.DateOffset(seconds=1 / freq_hz) for label, freq_hz in metadata['sample_freqs'].items()}
            self.data = pd.read_csv(f, index_col='time', parse_dates=['time'])

    def _add_acc_mag(self):
        if all(label in self.data.columns for label in ['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z']):
            self.data['acc_mag'] = np.linalg.norm(self.data[['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z']], axis=1)
            self.sample_freqs['acc_mag'] = self.sample_freqs['Accelerometer_X']

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = - pd.Timedelta(random.uniform(one_month, two_years)).round('s')
            self.timeshift(random_timedelta)
        if isinstance(shift, pd.Timestamp):
            self.start_time = shift
            timedeltas = self.data.index - self.data.index.min()
            self.data.index = shift + timedeltas
        if isinstance(shift, pd.Timedelta):
            self.start_time += shift
            self.data.index += shift
