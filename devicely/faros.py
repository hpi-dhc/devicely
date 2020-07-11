import os
import pyedflib
import numpy as np
import pandas as pd
from datetime import datetime

from .helpers import create_df

class FarosReader:

    signal_names = ['ECG', 'HRV', 'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'acc_mag']

    def __init__(self, path, timeshift=0):
        self.init_filelist(path)

        with pyedflib.EdfReader(self.filelist['edf']) as f:

            # read EDF file into a dictionary, keys: signal_labels
            n = f.signals_in_file # get num of signal types
            signal_labels = f.getSignalLabels() # get labels for types of signals
            raw_sample_freqs = f.getSampleFrequencies()
            start_ts = (f.getStartdatetime() - datetime.fromtimestamp(timeshift)).total_seconds()

            raw_data = dict.fromkeys(signal_labels) # the signals have difference sizes, therefore put into a dictionary
            for i in np.arange(n):
                raw_data[signal_labels[i]] = f.readSignal(i)

        raw_data['acc_mag'] = np.linalg.norm([raw_data['Accelerometer_X'], raw_data['Accelerometer_Y'], raw_data['Accelerometer_Z']], axis=0)

        sample_freqs = {}
        for i in range(len(signal_labels)):
            sample_freqs[signal_labels[i]] = raw_sample_freqs[i]
        sample_freqs['acc_mag'] = sample_freqs['Accelerometer_X']
        start_timestamps = {}
        for name in self.signal_names:
            start_timestamps[name] = start_ts

        self.data = create_df(self.signal_names, raw_data, sample_freqs, start_timestamps)

    def init_filelist(self, path):
        files = {
            'EDF': '.EDF',
            'ASC': '.ASC',
            'SDF': '.SDF'
        }
        for file in os.listdir(path):
            if file.endswith(".EDF"):
                files['EDF'] = file
            elif file.endswith(".ASC"):
                files['ASC'] = file
            elif file.endswith(".SDF"):
                files['SDF'] = file

        self.filelist = {
            'edf': os.path.join(path, files['EDF']),
            'asc': os.path.join(path, files['ASC']),
            'sdf': os.path.join(path, files['SDF']),
        }
