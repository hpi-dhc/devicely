from datetime import datetime
import glob
import os
import random

import numpy as np
import pandas as pd
import pyedflib


class FarosReader:

    #signal_names = ['ECG', 'HRV', 'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'acc_mag']

    def __init__(self, path):
        self._init_filelist(path)

        with pyedflib.EdfReader(self.filelist['edf']) as reader:
            self.data = pd.DataFrame()
            self.sample_freqs = dict(zip(reader.getSignalLabels(), reader.getSampleFrequencies()))
            self.start_time = reader.getStartdatetime()
            indices = dict()

            for i in range(len(reader.getSignalLabels())):
                label = reader.getLabel(i)
                freq = self.sample_freqs[label]
                signal_arr = reader.readSignal(i)
                if (freq, len(signal_arr)) not in indices:
                    indices[(freq, len(signal_arr))] = pd.date_range(start=self.start_time, 
                                                                     periods=len(signal_arr), 
                                                                     freq=pd.DateOffset(seconds=1/freq))
                series = pd.Series(signal_arr, index=indices[(freq, len(signal_arr))], name=label)
                self.data = self.data.join(series, how='outer')

            if all(label in self.data.columns for label in ['Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z']):
                self.data['acc_mag'] = np.linalg.norm([self.data['Accelerometer_X'], self.data['Accelerometer_Y'], self.data['Accelerometer_Z']], axis=0)
                self.sample_freqs['acc_mag'] = self.sample_freqs['Accelerometer_X']

    def write(self, path):
        signal_data = []
        labels = self.data.columns.drop('acc_mag')
        with pyedflib.EdfWriter(path, n_channels=len(labels)) as writer:
            writer.setStartdatetime(self.start_time)
            for i, label in enumerate(labels):
                writer.setLabel(i, label)
                writer.setSamplefrequency(i, self.sample_freqs[label])
                writer.write()
                signal_data.append(self.data[label].dropna().values)
            writer.writeSamples(signal_data)

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

    def _init_filelist(self, path):
        self.filelist = dict()
        edf_filenames = glob.glob(os.path.join(path, f"*.EDF"))
        if len(edf_filenames) == 0:
            raise FileNotFoundError(f"No file with .EDF extension found in {path}.")
        if len(edf_filenames) > 1:
            raise Error(f"Multiple files with .EDF extension found in {path}. This is ambiguous.")
        self.filelist['edf'] = edf_filenames.pop()

        for key, file_extension in {'asc': 'ASC', 'sdf': 'SDF'}.items():
            filenames = glob.glob(os.path.join(path, f"*.{file_extension}"))
            if len(filenames) == 1:
                self.filelist[key] = filenames.pop()