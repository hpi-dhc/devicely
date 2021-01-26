import datetime as dt
import os
import shutil
import unittest

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '/home/jost/DHC/devicely')
import devicely

class FarosTestCase(unittest.TestCase):
    READ_PATH = 'tests/Faros_test_data/testfilename.EdF'
    WRITE_PATH = 'tests/Faros_test_data/writtentestfile.csv'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reader = devicely.FarosReader(self.READ_PATH)

    def setUp(self):
        self.expected_sample_freqs = {
            'ECG': pd.DateOffset(seconds=1/1000),
            'Accelerometer_X': pd.DateOffset(seconds=1/100),
            'Accelerometer_Y': pd.DateOffset(seconds=1/100),
            'Accelerometer_Z': pd.DateOffset(seconds=1/100),
            'Marker': pd.DateOffset(seconds=1/1),
            'HRV': pd.DateOffset(seconds=1/5),
            'acc_mag': pd.DateOffset(seconds=1/100)
        }
        self.expected_signal_heads = {
            'ECG': np.array([ 26.,  -6., -31., -39., -17.]),
            'Accelerometer_X': np.array([164., 152., 152., 117., -47.]),
            'Accelerometer_Y': np.array([ 23.,  23., -24.,  11., 246.]),
            'Accelerometer_Z': np.array([-1172., -1172., -1079.,  -985., -1125.]),
            'Marker': np.array([0., 0., 0., 0., 0.]),
            'HRV': np.array([0., 0., 0., 0., 0.]),
            'acc_mag': np.array([1183.64226014, 1182.03933945, 1089.91788682, 991.98538296, 1152.54067173])
        }
        self.expected_start_time = pd.Timestamp("3.1.2019 16:12:43")

    def test_basic_read(self):
        self.assertEqual(self.reader.sample_freqs, self.expected_sample_freqs)
        self.assertEqual(set(self.reader.data.columns), set(self.expected_signal_heads.keys()))
        self.assertEqual(self.reader.start_time, self.expected_start_time)
        for label, expected_first_values in self.expected_signal_heads.items():
            np.testing.assert_almost_equal(self.reader.data[label].dropna().head(), expected_first_values)

    def test_write(self):
        self.reader.write(self.WRITE_PATH)
        write_reader = devicely.FarosReader(self.WRITE_PATH)
        self.assertEqual(write_reader.start_time, self.reader.start_time)
        self.assertEqual(write_reader.sample_freqs, self.reader.sample_freqs)
        pd.testing.assert_frame_equal(write_reader.data, self.reader.data, check_like=True)
        os.remove(self.WRITE_PATH)
    
    def test_timeshift_by_timedelta(self):
        reader = devicely.FarosReader(self.READ_PATH)
        shift = pd.Timedelta('1 days, 2 hours, 3 minutes, 4 seconds, 5 milliseconds')
        reader.timeshift(shift)
        expected_shifted_index_head = pd.DatetimeIndex(['2019-03-02 18:15:47.005000', '2019-03-02 18:15:47.006000',
                                                        '2019-03-02 18:15:47.007000', '2019-03-02 18:15:47.008000',
                                                        '2019-03-02 18:15:47.009000'])
        pd.testing.assert_index_equal(reader.data.head().index, expected_shifted_index_head, check_names=False)
        self.assertEqual(reader.start_time, pd.Timestamp('2019-03-02 18:15:47.005000'))

    def test_timeshift_to_timestamp(self):
        reader = devicely.FarosReader(self.READ_PATH)
        shift = pd.Timestamp(day=23, month=4, year=2009, hour=6, minute=42, second=21, microsecond=int(593.32e3))
        reader.timeshift(shift)
        expected_shifted_index_head = pd.DatetimeIndex(['2009-04-23 06:42:21.593320', '2009-04-23 06:42:21.594320',
                                                        '2009-04-23 06:42:21.595320', '2009-04-23 06:42:21.596320',
                                                        '2009-04-23 06:42:21.597320'])
        pd.testing.assert_index_equal(reader.data.head().index, expected_shifted_index_head, check_names=False)
        self.assertEqual(reader.start_time, shift)

    def test_random_timeshift(self):
        reader = devicely.FarosReader(self.READ_PATH)
        earliest_possible_index = pd.DatetimeIndex(['2017-03-01 16:12:43', '2017-03-01 16:12:43.001000',
                                                    '2017-03-01 16:12:43.002000', '2017-03-01 16:12:43.003000',
                                                    '2017-03-01 16:12:43.004000'])
        latest_possible_index = pd.DatetimeIndex(['2019-01-30 16:12:43', '2019-01-30 16:12:43.001000',
                                                  '2019-01-30 16:12:43.002000', '2019-01-30 16:12:43.003000',
                                                  '2019-01-30 16:12:43.004000'])

        earliest_possible_start_time = pd.Timestamp('2017-03-01 16:12:43')
        latest_possible_start_time = pd.Timestamp('2019-01-30 16:12:43')

        reader.timeshift()
        self.assertTrue((earliest_possible_index <= reader.data.head().index).all())
        self.assertTrue((reader.data.head().index <= latest_possible_index).all())
        self.assertLess(earliest_possible_start_time, reader.start_time)
        self.assertLess(reader.start_time, latest_possible_start_time)

if __name__ == '__main__':
    unittest.main()
