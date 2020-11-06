import unittest
import os
import shutil
import sys

import pandas as pd

import devicely

class EmpaticaTestCase(unittest.TestCase):
    WRITE_PATH = 'test_data_write'

    def setUp(self):
        self.empatica_reader = devicely.EmpaticaReader('Empatica_test_data_read')
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
            'timedelta': [145.631666, 146.522332, 151.725695, 152.835121, 153.710161, 154.725832, 161.679276,
                           162.741824, 163.773122, 164.757542, 165.757587, 166.69513, 167.585796, 168.429585,
                           169.288999, 170.148413, 170.929699, 171.695359, 172.539148, 173.492316, 174.398608],
            'ibi': [0.62509, 0.890666, 1.062549, 1.109426, 0.87504, 1.015671, 1.031297, 1.062549, 1.031297, 0.98442,
                     1.000046, 0.937543, 0.890666, 0.843789, 0.859414, 0.859414, 0.781286, 0.76566, 0.843789, 0.953169,
                     0.906291]
        })
        self.ibi_df['timedelta'] = pd.to_timedelta(self.ibi_df['timedelta'], unit='s')
        self.ibi_df['ibi'] = pd.to_timedelta(self.ibi_df['ibi'], unit='s')

        self.temp_df = pd.DataFrame({
            'temp': [23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.75, 23.6, 23.71, 23.71, 23.712, 23.69, 23.69,
                     23.69, 23.69, 23.65, 23.65, 23.65, 23.65]
        })
        self.tags_df = pd.DataFrame([pd.Timestamp(x, unit='s') for x in [1549015050.68, 1549014523.17, 1549014702.49, 1549014872.04]])

    def test_basic_read(self):
        pd.testing.assert_frame_equal(self.empatica_reader.ACC, self.acc_df)
        pd.testing.assert_frame_equal(self.empatica_reader.BVP, self.bvp_df)
        pd.testing.assert_frame_equal(self.empatica_reader.EDA, self.eda_df)
        pd.testing.assert_frame_equal(self.empatica_reader.HR, self.hr_df)
        pd.testing.assert_frame_equal(self.empatica_reader.IBI, self.ibi_df)
        pd.testing.assert_frame_equal(self.empatica_reader.TEMP, self.temp_df)
        pd.testing.assert_frame_equal(self.empatica_reader.tags, self.tags_df)

        self.assertEqual(self.empatica_reader.start_times, self.start_times)
        self.assertEqual(self.empatica_reader.sample_freqs, self.sample_freqs)

    def test_basic_write(self):
        self.empatica_reader.write(self.WRITE_PATH)

        path = self.WRITE_PATH
        written_start_times = {}
        written_sample_freqs = {}
        written_signals = {}

        for signal_name in ['bvp', 'eda', 'hr', 'temp']:
            with open(os.path.join(self.WRITE_PATH, f"{signal_name.upper()}.csv"), 'r') as f:
                written_start_times[signal_name] = pd.Timestamp(float(f.readline().split(',')[0]), unit='s')
                written_sample_freqs[signal_name] = float(f.readline().split(',')[0])
                written_signals[signal_name] = pd.read_csv(f, names=[signal_name])
        with open(os.path.join(path, 'ACC.csv'), 'r') as f:
            written_start_times['acc'] = pd.Timestamp(float(f.readline().split(',')[0]), unit='s')
            written_sample_freqs['acc'] = float(f.readline().split(',')[0])
            written_signals['acc'] = pd.read_csv(f, names=['acc_x', 'acc_y', 'acc_z'])
        with open(os.path.join(path, 'IBI.csv'), 'r') as f:
            first_line_split = f.readline().split(', ')
            self.assertEqual(first_line_split[1], 'IBI\n')
            written_start_times['ibi'] = pd.Timestamp(float(first_line_split[0]), unit='s')
            to_timedelta = lambda x: (pd.Timedelta(float(x), unit='s'))
            written_signals['ibi'] = pd.read_csv(f, names=['timedelta', 'ibi'],
                                              converters={0: to_timedelta, 1: to_timedelta})

        written_tags = pd.read_csv(os.path.join(path, 'tags.csv'), header=None, parse_dates=[0],
                                   date_parser=lambda x: pd.Timestamp(float(x), unit='s'))

        pd.testing.assert_frame_equal(written_signals['acc'], self.acc_df.drop(columns=['acc_mag']))
        pd.testing.assert_frame_equal(written_signals['bvp'], self.bvp_df)
        pd.testing.assert_frame_equal(written_signals['eda'], self.eda_df)
        pd.testing.assert_frame_equal(written_signals['hr'], self.hr_df)
        pd.testing.assert_frame_equal(written_signals['temp'], self.temp_df)
        pd.testing.assert_frame_equal(written_tags, self.tags_df)

        shutil.rmtree(self.WRITE_PATH)

    def test_timeshift_with_timestamp_as_parameter(self):
        timestamp = pd.Timestamp('23 April 2009, 4am')
        shifted_start_times = {signal_name: timestamp for signal_name in self.start_times.keys()}
        timedelta = self.tags_df - self.tags_df.loc[0, 0]
        shifted_tags = timestamp + timedelta
        self.empatica_reader.timeshift(timestamp)

        self.assertEqual(self.empatica_reader.start_times, shifted_start_times)
        pd.testing.assert_frame_equal(self.empatica_reader.tags, shifted_tags)

    def test_timeshift_with_timedelta_as_parameter(self):
        timedelta = pd.Timedelta('42 days, 420 hours, 69 seconds')
        shifted_start_times = {signal_name: timestamp + timedelta for signal_name, timestamp in
                               self.start_times.items()}
        shifted_tags = self.tags_df + timedelta
        self.empatica_reader.timeshift(timedelta)

        self.assertEqual(self.empatica_reader.start_times, shifted_start_times)
        pd.testing.assert_frame_equal(self.empatica_reader.tags, shifted_tags)

    def test_random_timeshift(self):
        self.empatica_reader.timeshift()
        for signal_name, timestamp in self.empatica_reader.start_times.items():
            self.assertLessEqual(self.start_times[signal_name] - pd.Timedelta('730 days'), timestamp)
            self.assertLessEqual(timestamp, self.start_times[signal_name] - pd.Timedelta('30 days'))
        earliest_possible_tags = self.tags_df - pd.Timedelta('730 days')
        latest_possible_tags = self.tags_df - pd.Timedelta('30 days')
        self.assertTrue((earliest_possible_tags <= self.empatica_reader.tags).all()[0])
        self.assertTrue((self.empatica_reader.tags <= latest_possible_tags).all()[0])

    def test_joined_dataframe(self):
        self.assertIsNotNone(self.empatica_reader.data)
        self.assertIsInstance(self.empatica_reader.data, pd.DataFrame)
        pd.testing.assert_index_equal(self.empatica_reader.data.columns,
                                      pd.Index(['acc_x', 'acc_y', 'acc_z', 'acc_mag', 'bvp', 'eda', 'hr', 'temp']))

        acc_part_from_joined_df = self.empatica_reader.data[['acc_x', 'acc_y', 'acc_z', 'acc_mag']].dropna()
        self.assertEqual(len(acc_part_from_joined_df), len(self.acc_df))
        acc_part_from_joined_df.index = range(len(acc_part_from_joined_df))
        pd.testing.assert_frame_equal(acc_part_from_joined_df, self.acc_df)

        for signal_name, correct_df in zip(['bvp', 'eda', 'hr', 'temp'], [self.bvp_df, self.eda_df, self.hr_df, self.temp_df]):
            extracted_df_from_joined_df = self.empatica_reader.data[signal_name].to_frame().dropna()
            extracted_df_from_joined_df.index = range(len(extracted_df_from_joined_df))
            pd.testing.assert_frame_equal(extracted_df_from_joined_df, correct_df)

if __name__ == '__main__':
    unittest.main()
