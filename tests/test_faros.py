import datetime as dt
import os
import unittest

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '/home/jost/DHC/devicely')
import devicely

class SpacelabsTestCase(unittest.TestCase):
    READ_PATH = 'tests/Faros_test_data'
    WRITE_PATH = 'tests/SpaceLabs_test_data_written'

    def setUp(self):
        self.expected_labels = ['ECG', 'Accelerometer_X', 'Accelerometer_Y', 'Accelerometer_Z', 'Marker', 'HRV']
        self.expected_sample_freqs = dict(zip(self.expected_labels, [1000, 100, 100, 100, 1, 5]))
        expected_signal_heads = np.array([[ 26.,  -6., -31., -39., -17.],
                                      [164., 152., 152., 117., -47.],
                                      [ 23.,  23., -24.,  11., 246.],
                                      [-1172., -1172., -1079.,  -985., -1125.],
                                      [0., 0., 0., 0., 0.],
                                      [0., 0., 0., 0., 0.]])
        self.expected_signal_heads = dict(zip(self.expected_labels, expected_signal_heads))                                      
        self.expected_start_time = pd.Timestamp("3.1.2019 16:12:43")

    def test_basic_read(self):
        reader = devicely.FarosReader(self.READ_PATH)
        self.assertEqual(reader.sample_freqs, self.expected_sample_freqs)
        self.assertEqual(set(reader.data.columns), set(self.expected_labels + ['acc_mag']))
        self.assertEqual(reader.start_time, self.expected_start_time)
        for label, np_array in self.expected_signal_heads.items():
            self.assertEqual(reader.data[label].dropna().values[:5], np_array)

if __name__ == '__main__':
    unittest.main()
