"""
Tests for the muse module
"""
import os
import sys
import unittest

import numpy as np
import pandas as pd

import devicely


class MuseTestCase(unittest.TestCase):
    READ_PATH = 'tests/Muse_test_data/read_test_data.csv'
    WRITE_PATH = 'tests/Muse_test_data/write_test_data.csv'

    expected_data_head = pd.DataFrame(
        {'AUX_RIGHT': [844.1392, np.nan, 861.06226, 1009.34064, 1006.52014],
         'Accelerometer_X': [-0.23260498046875, np.nan, -0.23260498046875, -0.23260498046875, -0.23260498046875],
         'Accelerometer_Y': [-0.04901123046875, np.nan, -0.04901123046875, -0.04901123046875, -0.04901123046875],
         'Accelerometer_Z': [0.9664306640625, np.nan, 0.9664306640625, 0.9664306640625, 0.9664306640625],
         'Alpha_AF7': [0.70684004, np.nan, 0.7046354, 0.7046354, 0.7046354],
         'Alpha_AF8': [0.3738289, np.nan, 0.37960157, 0.37960157, 0.37960157],
         'Alpha_TP10': [0.5247787, np.nan, 0.5247787, 0.5247787, 0.5247787],
         'Alpha_TP9': [0.6818201, np.nan, 0.6818201, 0.6818201, 0.6818201],
         'Battery': [100.0, np.nan, 100.0, 100.0, 100.0],
         'Beta_AF7': [0.9047759, np.nan, 0.90967786, 0.90967786, 0.90967786],
         'Beta_AF8': [-0.074241824, np.nan, -0.07182129, -0.07182129, -0.07182129],
         'Beta_TP10': [0.24255054, np.nan, 0.24255054, 0.24255054, 0.24255054],
         'Beta_TP9': [0.40113458, np.nan, 0.40113458, 0.40113458, 0.40113458],
         'Delta_AF7': [0.65365446, np.nan, 0.6321334, 0.6321334, 0.6321334],
         'Delta_AF8': [0.87098247, np.nan, 0.8560632, 0.8560632, 0.8560632],
         'Delta_TP10': [0.7412762, np.nan, 0.7412762, 0.7412762, 0.7412762],
         'Delta_TP9': [0.7765235, np.nan, 0.7765235, 0.7765235, 0.7765235],
         'Elements': [np.nan, '/muse/elements/blink', np.nan, np.nan, np.nan],
         'Gamma_AF7': [0.7472885, np.nan, 0.73841846, 0.73841846, 0.73841846],
         'Gamma_AF8': [-0.29481375, np.nan, -0.29959682, -0.29959682, -0.29959682],
         'Gamma_TP10': [-0.3348679, np.nan, -0.3348679, -0.3348679, -0.3348679],
         'Gamma_TP9': [-0.0852012, np.nan, -0.0852012, -0.0852012, -0.0852012],
         'Gyro_X': [2.998199462890625, np.nan, 2.998199462890625, 2.998199462890625, 2.998199462890625],
         'Gyro_Y': [2.130889892578125, np.nan, 2.130889892578125, 2.130889892578125, 2.130889892578125],
         'Gyro_Z': [1.966400146484375, np.nan, 1.966400146484375, 1.966400146484375, 1.966400146484375],
         'HSI_AF7': [1.0, np.nan, 1.0, 1.0, 1.0],
         'HSI_AF8': [1.0, np.nan, 1.0, 1.0, 1.0],
         'HSI_TP10': [1.0, np.nan, 1.0, 1.0, 1.0],
         'HSI_TP9': [1.0, np.nan, 1.0, 1.0, 1.0],
         'HeadBandOn': [1.0, np.nan, 1.0, 1.0, 1.0],
         'RAW_AF7': [798.60803, np.nan, 796.5934, 805.8608, 805.4579],
         'RAW_AF8': [794.17584, np.nan, 791.75824, 789.7436, 784.5055],
         'RAW_TP10': [835.6777, np.nan, 833.663, 827.2161, 820.3663],
         'RAW_TP9': [832.4542, np.nan, 829.2308, 824.7985, 819.9634],
         'Theta_AF7': [0.328677, np.nan, 0.33023703, 0.33023703, 0.33023703],
         'Theta_AF8': [0.5665972, np.nan, 0.56282604, 0.56282604, 0.56282604],
         'Theta_TP10': [0.5058985, np.nan, 0.5058985, 0.5058985, 0.5058985],
         'Theta_TP9': [0.76928276, np.nan, 0.76928276, 0.76928276, 0.76928276]},
         index=pd.DatetimeIndex(['2021-04-05 15:48:04.834', '2021-04-05 15:48:04.840', '2021-04-05 15:48:04.836', '2021-04-05 15:48:04.842', '2021-04-05 15:48:04.843'], name='TimeStamp')
    )

    def setUp(self):
        self.reader = devicely.MuseReader(self.READ_PATH)

    def test_read(self):
        pd.testing.assert_frame_equal(self.reader.data.head(), self.expected_data_head, check_like=True)

    def test_write(self):
        self.reader.write(self.WRITE_PATH)
        new_reader = devicely.MuseReader(self.WRITE_PATH)
        pd.testing.assert_frame_equal(new_reader.data, self.reader.data)
        os.remove(self.WRITE_PATH)

    def test_timeshift_by_timedelta(self):
        shift = pd.Timedelta('1 days, 2 hours, 3 minutes, 4 seconds, 5 milliseconds')
        self.reader.timeshift(shift)
        expected_shifted_time_col = pd.DatetimeIndex(['2021-04-06 17:51:08.839000', '2021-04-06 17:51:08.845000',
                                                      '2021-04-06 17:51:08.841000', '2021-04-06 17:51:08.847000',
                                                      '2021-04-06 17:51:08.848000'],
                                                      name='TimeStamp')
        pd.testing.assert_index_equal(self.reader.data.head().index, expected_shifted_time_col)

    def test_timeshift_to_timestamp(self):
        ts_shift = pd.Timestamp('01.02.2015, 11:56:32')
        self.reader.timeshift(ts_shift)
        expected_shifted_time_col = pd.DatetimeIndex(['2015-01-02 11:56:32', '2015-01-02 11:56:32.006000',
                                                      '2015-01-02 11:56:32.002000', '2015-01-02 11:56:32.008000',
                                                      '2015-01-02 11:56:32.009000'],
                                                      name='TimeStamp')
        pd.testing.assert_index_equal(self.reader.data.head().index, expected_shifted_time_col)

    def test_random_timeshift(self):
        earliest_possible_time_col = pd.DatetimeIndex(['2019-04-06 15:48:04.834000', '2019-04-06 15:48:04.840000',
                                                       '2019-04-06 15:48:04.836000', '2019-04-06 15:48:04.842000',
                                                       '2019-04-06 15:48:04.843000'])

        latest_possible_time_col = pd.DatetimeIndex(['2021-03-06 15:48:04.834000', '2021-03-06 15:48:04.840000',
                                                     '2021-03-06 15:48:04.836000', '2021-03-06 15:48:04.842000',
                                                     '2021-03-06 15:48:04.843000'])

        self.reader.timeshift()
        self.assertTrue((earliest_possible_time_col <= self.reader.data.head().index).all())
        self.assertTrue((self.reader.data.head().index <= latest_possible_time_col).all())


if __name__ == '__main__':
    unittest.main()
