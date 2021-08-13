"""
Tests for the ShimmerPlus module
"""
import os
import sys
import unittest

import pandas as pd
import devicely


class ShimmerPlusTestCase(unittest.TestCase):
    READ_PATH = 'tests/Shimmer_test_data/read_test_data.csv'
    WRITE_PATH = 'tests/Shimmer_test_data/write_test_data.csv'

    def setUp(self):
        self.expected_delimiter = ';'

        self.expected_data_head = pd.DataFrame(
            {'Shimmer_40AC_Timestamp_Unix_CAL': pd.to_datetime(['2020-07-28 10:56:50.034000', '2020-07-28 10:56:50.057000', '2020-07-28 10:56:50.074000', '2020-07-28 10:56:50.099000', '2020-07-28 10:56:50.111000']),
             'Shimmer_40AC_Accel_LN_X_CAL': [-1.434782608695652, -1.4021739130434783, -1.434782608695652, -1.4130434782608696, -1.4456521739130435],
             'Shimmer_40AC_Accel_LN_Y_CAL': [10.0, 10.0, 10.0, 10.0, 10.0],
             'Shimmer_40AC_Accel_LN_Z_CAL': [0.5543478260869565, 0.5543478260869565, 0.5543478260869565, 0.5217391304347826, 0.5108695652173912],
             'Shimmer_40AC_Accel_WR_X_CAL': [-3.9305804907241173, -3.9233991621783364, -3.897067624177139, -3.932974266906044, -3.944943147815679],
             'Shimmer_40AC_Accel_WR_Y_CAL': [8.42130460801915, 8.442848593656493, 8.42848593656493, 8.42130460801915, 8.42848593656493],
             'Shimmer_40AC_Accel_WR_Z_CAL': [-1.620586475164572, -1.5990424895272293, -1.6038300418910831, -1.589467384799521, -1.6612806702573308],
             'Shimmer_40AC_Battery_CAL': [4139.194139194139, 4137.728937728937, 4111.355311355311, 4140.65934065934, 4134.798534798534],
             'Shimmer_40AC_Ext_Exp_A15_CAL': [1684.9816849816848, 1673.260073260073, 1901.098901098901, 1722.3443223443223, 1678.3882783882782],
             'Shimmer_40AC_GSR_Range_CAL': [2.0, 2.0, 2.0, 2.0, 2.0],
             'Shimmer_40AC_GSR_Skin_Conductance_CAL': [2.493040293040293, 2.4915750915750916, 2.49010989010989, 2.4886446886446887, 2.4886446886446887],
             'Shimmer_40AC_GSR_Skin_Resistance_CAL': [401.1166617690273, 401.3525433695972, 401.58870255957635, 401.8251398292611, 401.8251398292611],
             'Shimmer_40AC_Gyro_X_CAL': [0.13740458015267176, 0.183206106870229, 0.2748091603053435, 0.22900763358778625, 0.13740458015267176],
             'Shimmer_40AC_Gyro_Y_CAL': [1.8778625954198473, 1.3282442748091603, 1.282442748091603, 1.450381679389313, 1.5114503816793892],
             'Shimmer_40AC_Gyro_Z_CAL': [-0.183206106870229, -0.41221374045801523, -0.1984732824427481, -0.12213740458015267, -0.47328244274809156],
             'Shimmer_40AC_Int_Exp_A12_CAL': [1680.5860805860805, 1703.296703296703, 1687.179487179487, 1650.5494505494505, 1701.8315018315018],
             'Shimmer_40AC_Mag_X_CAL': [-0.11244377811094453, -0.10944527736131934, -0.10794602698650674, -0.10644677661169415, -0.11394302848575712],
             'Shimmer_40AC_Mag_Y_CAL': [-0.9160419790104948, -0.9130434782608695, -0.9100449775112444, -0.9010494752623688, -0.9040479760119939],
             'Shimmer_40AC_Mag_Z_CAL': [-0.047976011994003, -0.047976011994003, -0.04947526236881559, -0.050974512743628186, -0.037481259370314844],
             'Shimmer_40AC_Pressure_BMP280_CAL': [100.43537920858897, 100.4297311006671, 100.44102732749235, 100.44102732749235, 100.43820326666797],
             'Shimmer_40AC_Temperature_BMP280_CAL': [33.365877509029815, 33.365877509029815, 33.365877509029815, 33.365877509029815, 33.365877509029815],
             'Shimmer_40AC_Accel_LN_mag': [10.1176036 , 10.11303086, 10.1176036 , 10.11280889, 10.11686206]},
            )

        self.expected_units = {
            'Shimmer_40AC_Timestamp_Unix_CAL': 'ms',
            'Shimmer_40AC_Accel_LN_X_CAL': 'm/(s^2)',
            'Shimmer_40AC_Accel_LN_Y_CAL': 'm/(s^2)',
            'Shimmer_40AC_Accel_LN_Z_CAL': 'm/(s^2)',
            'Shimmer_40AC_Accel_WR_X_CAL': 'm/(s^2)',
            'Shimmer_40AC_Accel_WR_Y_CAL': 'm/(s^2)',
            'Shimmer_40AC_Accel_WR_Z_CAL': 'm/(s^2)',
            'Shimmer_40AC_Battery_CAL': 'mV',
            'Shimmer_40AC_Ext_Exp_A15_CAL': 'mV',
            'Shimmer_40AC_GSR_Range_CAL': 'no_units',
            'Shimmer_40AC_GSR_Skin_Conductance_CAL': 'uS',
            'Shimmer_40AC_GSR_Skin_Resistance_CAL': 'kOhms',
            'Shimmer_40AC_Gyro_X_CAL': 'deg/s',
            'Shimmer_40AC_Gyro_Y_CAL': 'deg/s',
            'Shimmer_40AC_Gyro_Z_CAL': 'deg/s',
            'Shimmer_40AC_Int_Exp_A12_CAL': 'mV',
            'Shimmer_40AC_Mag_X_CAL': 'local_flux',
            'Shimmer_40AC_Mag_Y_CAL': 'local_flux',
            'Shimmer_40AC_Mag_Z_CAL': 'local_flux',
            'Shimmer_40AC_Pressure_BMP280_CAL': 'kPa',
            'Shimmer_40AC_Temperature_BMP280_CAL': 'Degrees Celsius'
        }

        self.reader = devicely.ShimmerPlusReader(self.READ_PATH)

    def _compare_reader_and_expected_values(self, reader, expected_delimiter, expected_units, expected_data_head):
        self.assertEqual(reader.delimiter, expected_delimiter)
        self.assertEqual(reader.units, expected_units)
        pd.testing.assert_frame_equal(reader.data.head(), expected_data_head)

    def test_basic_read(self):
        self._compare_reader_and_expected_values(self.reader,
                                                 self.expected_delimiter,
                                                 self.expected_units,
                                                 self.expected_data_head)

    def test_write(self):
        self.reader.write(self.WRITE_PATH)
        new_reader = devicely.ShimmerPlusReader(self.WRITE_PATH)
        self._compare_reader_and_expected_values(new_reader,
                                                 self.reader.delimiter,
                                                 self.reader.units,
                                                 self.reader.data.head())
        os.remove(self.WRITE_PATH)

    def test_timeshift_by_timedelta(self):
        shift = pd.Timedelta('1 days, 2 hours, 3 minutes, 4 seconds, 5 milliseconds')
        self.reader.timeshift(shift)
        expected_shifted_time_col = pd.Series(pd.to_datetime(['2020-07-29 12:59:54.039000', '2020-07-29 12:59:54.062000',
                                       '2020-07-29 12:59:54.079000', '2020-07-29 12:59:54.104000',
                                       '2020-07-29 12:59:54.116000']))
        pd.testing.assert_series_equal(self.reader.data.loc[:4, 'Shimmer_40AC_Timestamp_Unix_CAL'], expected_shifted_time_col, check_names=False)

    def test_timeshift_to_timestamp(self):
        shift = pd.Timestamp(day=23, month=4, year=2009, hour=6, minute=42, second=21, microsecond=int(593.32e3))
        self.reader.timeshift(shift)
        expected_shifted_time_col = pd.Series(pd.to_datetime(['2009-04-23 06:42:21.593000', '2009-04-23 06:42:21.616000',
                                                      '2009-04-23 06:42:21.633000', '2009-04-23 06:42:21.658000',
                                                      '2009-04-23 06:42:21.670000']))
        pd.testing.assert_series_equal(self.reader.data.loc[:4, 'Shimmer_40AC_Timestamp_Unix_CAL'], expected_shifted_time_col, check_names=False)

    def test_random_timeshift(self):
        earliest_possible_time_col = pd.Series(pd.to_datetime(['2018-07-29 10:56:50.034000', '2018-07-29 10:56:50.057000',
                                                     '2018-07-29 10:56:50.074000', '2018-07-29 10:56:50.099000',
                                                     '2018-07-29 10:56:50.111000']))
        latest_possible_time_col = pd.Series(pd.to_datetime(['2020-06-28 10:56:50.034000', '2020-06-28 10:56:50.057000',
                                                   '2020-06-28 10:56:50.074000', '2020-06-28 10:56:50.099000',
                                                   '2020-06-28 10:56:50.111000']))

        self.reader.timeshift()
        self.assertTrue((earliest_possible_time_col <= self.reader.data.loc[:4, 'Shimmer_40AC_Timestamp_Unix_CAL']).all())
        self.assertTrue((self.reader.data.loc[:4, 'Shimmer_40AC_Timestamp_Unix_CAL'] <= latest_possible_time_col).all())


if __name__ == '__main__':
    unittest.main()
