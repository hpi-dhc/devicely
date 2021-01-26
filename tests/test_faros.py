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
    READ_PATH = 'tests/Faros_test_data'
    WRITE_PATH = 'tests/Faros_test_data_written'

    def setUp(self):
        self.expected_sample_freqs = {
            'ECG': 1000,
            'Accelerometer_X': 100,
            'Accelerometer_Y': 100,
            'Accelerometer_Z': 100,
            'Marker': 1,
            'HRV': 5,
            'acc_mag': 100
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
        self.reader = devicely.FarosReader(self.READ_PATH)


    def test_basic_read(self):
        self.assertEqual(self.reader.sample_freqs, self.expected_sample_freqs)
        self.assertEqual(set(self.reader.data.columns), set(self.expected_signal_heads.keys()))
        self.assertEqual(self.reader.start_time, self.expected_start_time)
        for label, expected_first_values in self.expected_signal_heads.items():
            np.testing.assert_almost_equal(self.reader.data[label].dropna().head(), expected_first_values)

    def test_write(self):
        old_df = self.reader.data
        if not os.path.exists(self.WRITE_PATH):
            os.mkdir(self.WRITE_PATH)
        written_file_path = os.path.join(self.WRITE_PATH, 'testfilename.EDF')
        self.reader.write(written_file_path)
        new_df = devicely.FarosReader(self.WRITE_PATH).data
        pd.testing.assert_frame_equal(old_df, new_df)
        shutil.rmtree(self.WRITE_PATH)

if __name__ == '__main__':
    unittest.main()
