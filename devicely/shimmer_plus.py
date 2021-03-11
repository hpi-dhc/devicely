"""
Module to process Shimmer Plus data
"""
import random

import numpy as np
import pandas as pd


class ShimmerPlusReader:
    def __init__(self, path, delimiter=';'):
        self.delimiter = delimiter
        self.data = pd.read_csv(path, sep=delimiter, skiprows=1)
        self.data = self.data.dropna(axis=1, how='all')
        self.units = self.data.iloc[0] # saving self.data units
        self.data = self.data.drop(0).astype(float)
        self.data['time'] = pd.to_datetime(
            self.data['Shimmer_40AC_Timestamp_Unix_CAL'],
            unit=self.units['Shimmer_40AC_Timestamp_Unix_CAL']).round('ms')
        self.data.drop(columns=['Shimmer_40AC_Timestamp_Unix_CAL'], inplace=True)
        self.data = self.data.drop_duplicates(subset='time')
        self.data.set_index('time', inplace=True, verify_integrity=True)
        self.data.sort_index(inplace=True)
        self.data['acc_mag'] = np.linalg.norm(self.data[['Shimmer_40AC_Accel_LN_X_CAL',
                                                         'Shimmer_40AC_Accel_LN_Y_CAL',
                                                         'Shimmer_40AC_Accel_LN_Z_CAL']],
                                              axis=1)
        self.units['acc_mag'] = self.units['Shimmer_40AC_Accel_LN_Z_CAL']

    def write(self, path):
        write_df = self.data.drop(columns=['acc_mag'])
        write_df['Shimmer_40AC_Timestamp_Unix_CAL'] = (write_df.index.to_series().astype(int) / 1e6).round()
        units = self.units.drop('acc_mag').to_frame().transpose()
        write_df = pd.concat([units, write_df])
        with open(path, 'w') as f:
            f.write(f"\"sep={self.delimiter}\"\n")
            write_df.to_csv(f, index=None, sep=self.delimiter)

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = - pd.Timedelta(random.uniform(one_month, two_years)).round('ms')
            self.timeshift(random_timedelta)
        if isinstance(shift, pd.Timestamp):
            shift = shift.round('ms')
            timedeltas = self.data.index - self.data.index.min()
            self.data.index = shift + timedeltas
        if isinstance(shift, pd.Timedelta):
            self.data.index += shift.round('ms')
