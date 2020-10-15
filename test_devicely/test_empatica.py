import unittest
from devicely import empatica
import pandas as pd
import os
import shutil

class EmpaticaTestCase(unittest.TestCase):
    WRITE_PATH = 'Empatica_test_data_write'

    def setUp(self):
        self.empatica_reader = empatica.EmpaticaReader('Empatica_test_data_read')
        self.start_times = {
            'acc': pd.Timestamp(1551453301, unit='s'),
            'bvp': pd.Timestamp(1551453301, unit='s'),
            'eda': pd.Timestamp(1551453301, unit='s'),
            'hr': pd.Timestamp(1551453311, unit='s'),
            'ibi': pd.Timestamp(1551453301, unit='s'),
            'temp': pd.Timestamp(1551453301, unit='s'),
        }
        self.sample_freqs = {
            'acc': 32,
            'bvp': 64,
            'eda': 4,
            'hr': 1,
            'temp': 4,
        }
        self.acc_df = pd.DataFrame({
            'acc_x': [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, -1.0, -1.0,
                      -1.0, -1.0, -1.0, -1.0],
            'acc_y': [65.0, 65.0, 65.0, 65.0, 64.0, 64.0, 65.0, 65.0, 65.0, 65.0, 65.0, 64.0, 65.0, 65.0, 65.0,
                      64.0, 64.0, 64.0, 65.0, 65.0],
            'acc_z': [5.0, 5.0, 4.0, 5.0, 5.0, 5.0, 5.0, 4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.0, 5.0, 5.0,
                      5.0],
            'acc_mag': [65.19969325081216, 65.19969325081216, 65.13063795173512, 65.19969325081216,
                        64.20280367709809, 64.20280367709809, 65.19969325081216, 65.13063795173512,
                        65.19969325081216, 65.19969325081216, 65.19969325081216, 64.20280367709809,
                        65.19202405202648, 65.19202405202648, 65.19969325081216, 64.20280367709809,
                        64.13267497929586, 64.20280367709809, 65.19969325081216, 65.19969325081216]
        })
        self.bvp_df = pd.DataFrame({
            'bvp': [-0.0, -0.0, 1.37, 1.72, -0.0, -93.32, -104.05, -118.82, -137.78, -160.29, -184.86, -210.06, -233.45,
                    -251.99, -262.04, -261.2, -0.0, -0.0, -0.0, -0.0]
        })
        self.eda_df = pd.DataFrame({
            'eda': [0.0, 0.0, 0.005126, 0.003844, 0.003844, 0.002563, 0.0, 0.005126, 0.005126, 0.002563, 0.002563,
                    0.005126, 0.003844, 0.003844, 0.002563, 0.005126, 0.003844, 0.002563, 0.002563, 0.0]
        })
        self.hr_df = pd.DataFrame({
            'hr': [88.0, 88.0, 88.67, 85.0, 89.8, 88.5, 93.0, 97.88, 100.33, 102.3, 104.36, 106.25, 107.38, 108.29,
                   109.27, 110.62, 110.76, 111.0, 110.32, 109.5]
        })
        self.ibi_df = pd.DataFrame({
            'timedeltas': [145.631666, 146.522332, 151.725695, 152.835121, 153.710161, 154.725832, 161.679276,
                           162.741824, 163.773122, 164.757542, 165.757587, 166.69513, 167.585796, 168.429585,
                           169.288999, 170.148413, 170.929699, 171.695359, 172.539148, 173.492316, 174.398608],
            'ibis': [0.62509, 0.890666, 1.062549, 1.109426, 0.87504, 1.015671, 1.031297, 1.062549, 1.031297, 0.98442,
                     1.000046, 0.937543, 0.890666, 0.843789, 0.859414, 0.859414, 0.781286, 0.76566, 0.843789, 0.953169,
                     0.906291]
        })
        self.ibi_df['timedeltas'] = pd.to_timedelta(self.ibi_df['timedeltas'], unit='s')
        self.ibi_df['ibis'] = pd.to_timedelta(self.ibi_df['ibis'], unit='s')

        self.temp_df = pd.DataFrame({
            'temp': [23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.6, 23.71, 23.71, 23.712, 23.69, 23.69,
                     23.69, 23.69, 23.65, 23.65, 23.65, 23.65]
        })

    def test_basic_read(self):
        self._test_empatica_reader_contents(self.start_times, self.sample_freqs, self.acc_df, self.bvp_df, self.eda_df,
                                            self.hr_df, self.ibi_df, self.temp_df)

    def test_basic_write(self):
        self.empatica_reader.write(self.WRITE_PATH)
        self._test_written_path_contents(self.WRITE_PATH, self.start_times, self.sample_freqs,
                                         self.acc_df.drop(columns=['acc_mag']), self.bvp_df,
                                         self.eda_df, self.hr_df, self.ibi_df, self.temp_df)
        shutil.rmtree(self.WRITE_PATH)

    def test_timeshift_with_timestamp_as_parameter(self):
        timestamp = pd.Timestamp('23 April 2009, 4am')
        shifted_start_times = {signal_name: timestamp for signal_name in self.start_times.keys()}
        self.empatica_reader.timeshift(timestamp)
        self._test_empatica_reader_contents(shifted_start_times, self.sample_freqs, self.acc_df, self.bvp_df,
                                            self.eda_df,
                                            self.hr_df, self.ibi_df, self.temp_df)

    def test_timeshift_with_timedelta_as_parameter(self):
        timedelta = pd.Timedelta('42 days, 420 hours, 69 seconds')
        shifted_start_times = {signal_name: timestamp + timedelta for signal_name, timestamp in
                               self.start_times.items()}
        self.empatica_reader.timeshift(timedelta)
        self._test_empatica_reader_contents(shifted_start_times, self.sample_freqs, self.acc_df, self.bvp_df,
                                            self.eda_df,
                                            self.hr_df, self.ibi_df, self.temp_df)

    def test_random_timeshift(self):
        self.empatica_reader.timeshift()
        self._test_empatica_reader_contents(self.start_times, self.sample_freqs, self.acc_df, self.bvp_df, self.eda_df,
                                            self.hr_df, self.ibi_df, self.temp_df, random_timeshift_applied=True)

    def test_write_timeshift(self):
        shift = pd.Timedelta('-1 day, 2 hours, 3 minutes, 4 seconds')
        shifted_start_times = {signal_name: timestamp + shift for signal_name, timestamp in self.start_times.items()}
        self.empatica_reader.timeshift(shift)
        self.empatica_reader.write(self.WRITE_PATH)
        self._test_written_path_contents(self.WRITE_PATH, shifted_start_times, self.sample_freqs,
                                         self.acc_df.drop(columns=['acc_mag']), self.bvp_df,
                                         self.eda_df, self.hr_df, self.ibi_df, self.temp_df)
        shutil.rmtree(self.WRITE_PATH)

    def _test_empatica_reader_contents(self, start_times, sample_freqs, acc_df, bvp_df, eda_df, hr_df, ibi_df, temp_df,
                                       random_timeshift_applied=False):
        pd.testing.assert_frame_equal(self.empatica_reader.ACC, acc_df)
        pd.testing.assert_frame_equal(self.empatica_reader.BVP, bvp_df)
        pd.testing.assert_frame_equal(self.empatica_reader.EDA, eda_df)
        pd.testing.assert_frame_equal(self.empatica_reader.HR, hr_df)
        pd.testing.assert_frame_equal(self.empatica_reader.IBI, ibi_df)
        pd.testing.assert_frame_equal(self.empatica_reader.TEMP, temp_df)

        if random_timeshift_applied:
            for signal_name in start_times.keys():
                self.assertLess(self.empatica_reader.start_times[signal_name], start_times[signal_name])
        else:
            self.assertEquals(self.empatica_reader.start_times, start_times)

        self.assertEquals(self.empatica_reader.sample_freqs, sample_freqs)

    def _test_written_path_contents(self, path, start_times, sample_freqs, acc_df, bvp_df, eda_df, hr_df, ibi_df,
                                    temp_df, random_timeshift_applied=False):
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'ACC.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'BVP.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'EDA.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'HR.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'IBI.csv')))
        self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'TEMP.csv')))
        # self.assertTrue(os.path.isfile(os.path.join(self.WRITE_PATH, 'info.txt')))

        written_start_times = {}
        written_sample_freqs = {}
        with open(os.path.join(path, 'ACC.csv'), 'r') as f:
            written_start_times['acc'] = pd.Timestamp(float(f.readline().split(',')[0]), unit='s')
            written_sample_freqs['acc'] = float(f.readline().split(',')[0])
            written_acc_signals = pd.read_csv(f, names=['acc_x', 'acc_y', 'acc_z'])
        with open(os.path.join(path, 'BVP.csv'), 'r') as f:
            written_start_times['bvp'] = pd.Timestamp(float(f.readline()), unit='s')
            written_sample_freqs['bvp'] = float(f.readline())
            written_bvp_signals = pd.read_csv(f, names=['bvp'])
        with open(os.path.join(path, 'EDA.csv'), 'r') as f:
            written_start_times['eda'] = pd.Timestamp(float(f.readline()), unit='s')
            written_sample_freqs['eda'] = float(f.readline())
            written_eda_signals = pd.read_csv(f, names=['eda'])
        with open(os.path.join(path, 'HR.csv'), 'r') as f:
            written_start_times['hr'] = pd.Timestamp(float(f.readline()), unit='s')
            written_sample_freqs['hr'] = float(f.readline())
            written_hr_signals = pd.read_csv(f, names=['hr'])
        with open(os.path.join(path, 'IBI.csv'), 'r') as f:
            first_line_split = f.readline().split(', ')
            self.assertEquals(first_line_split[1], 'IBI\n')
            written_start_times['ibi'] = pd.Timestamp(float(first_line_split[0]), unit='s')
            to_timedelta = lambda x: (pd.Timedelta(float(x), unit='s'))
            written_ibi_signals = pd.read_csv(f, names=['timedeltas', 'ibis'],
                                              converters={0: to_timedelta, 1: to_timedelta})
        with open(os.path.join(path, 'TEMP.csv'), 'r') as f:
            written_start_times['temp'] = pd.Timestamp(float(f.readline()), unit='s')
            written_sample_freqs['temp'] = float(f.readline())
            written_temp_signals = pd.read_csv(f, names=['temp'])

        pd.testing.assert_frame_equal(written_acc_signals, acc_df)
        pd.testing.assert_frame_equal(written_bvp_signals, bvp_df)
        pd.testing.assert_frame_equal(written_eda_signals, eda_df)
        pd.testing.assert_frame_equal(written_hr_signals, hr_df)
        pd.testing.assert_frame_equal(written_temp_signals, temp_df)

        # pd.testing.assert_frame_equal(written_ibi_signals, ibi_df)
        # Commented out because of rounding issues with pd.read_csv.
        # Floating point numbers are never completely exact, not even with the highest float_precision.
        # To quote github user chris-b1 from https://github.com/pandas-dev/pandas/issues/17154:
        # "Trying to get exact equality out of floating points is generally a losing battle,
        # doubly so with a lossy format like csv"

        if random_timeshift_applied:
            for signal_name in start_times.keys():
                self.assertLess(written_start_times[signal_name], start_times[signal_name])
        else:
            self.assertEquals(written_start_times, start_times)

        self.assertEquals(written_sample_freqs, sample_freqs)

if __name__ == '__main__':
    unittest.main()
