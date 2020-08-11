import numpy as np
import pandas as pd
import datetime as dt

class ShimmerPlusReader:

    def __init__(self, path, delimiter, timeshift=0):
        self.data = pd.read_csv(path, sep=delimiter, skiprows=1)
        self.data = self.data.dropna(axis=1, how='all')
        self.units = self.data.iloc[0] # saving self.data units
        self.data = self.data.drop(0)
        if self.units['Shimmer_40AC_Timestamp_Unix_CAL'] != 'ms':
            print('Please save the data in miliseconds before proceeding.')
            self.data = pd.DataFrame()
        else:
            self.data['time'] = self.data['Shimmer_40AC_Timestamp_Unix_CAL'].apply(lambda x: dt.datetime.fromtimestamp(float(x)/1000))

            self.data = self.data.drop_duplicates(subset='Shimmer_40AC_Timestamp_Unix_CAL')

            self.data.set_index('time', inplace=True, verify_integrity=True)
            self.data.sort_index(inplace=True)
            # Calculating the acc_magnitude
            self.data['acc_mag'] = np.linalg.norm([
                self.data['Shimmer_40AC_Accel_LN_X_CAL'].astype(float),
                self.data['Shimmer_40AC_Accel_LN_Y_CAL'].astype(float),
                self.data['Shimmer_40AC_Accel_LN_Z_CAL'].astype(float)], axis=0)
            # Calculating timeshift
            self.data.index = self.data.index.shift(periods=-timeshift, freq='1H')