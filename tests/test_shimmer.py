import datetime as dt
import os
import shutil
import unittest

import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '/home/jost/DHC/devicely')
import devicely

class ShimmerTestCase(unittest.TestCase):
    READ_PATH = 'tests/Shimmer_test_data/read_test_data.csv'
    WRITE_PATH = 'tests/Shimmer_test_data/write_test_data.csv'

    def setUp(self):
        self.expected_delimiter = ';'

        self.expected_head = pd.DataFrame(
            {"Shimmer_40AC_Accel_LN_X_CAL": [-1.434782608695652, -1.4021739130434783, -1.434782608695652, -1.4130434782608696, -1.4456521739130435],
            "Shimmer_40AC_Accel_LN_Y_CAL": [10.0, 10.0, 10.0, 10.0, 10.0],
            "Shimmer_40AC_Accel_LN_Z_CAL": [0.5543478260869565, 0.5543478260869565, 0.5543478260869565, 0.5217391304347826, 0.5108695652173912],
            "Shimmer_40AC_Accel_WR_X_CAL": [-3.9305804907241173, -3.9233991621783364, -3.897067624177139, -3.932974266906044, -3.944943147815679],
            "Shimmer_40AC_Accel_WR_Y_CAL": [8.42130460801915, 8.442848593656493, 8.42848593656493, 8.42130460801915, 8.42848593656493],
            "Shimmer_40AC_Accel_WR_Z_CAL": [-1.620586475164572, -1.5990424895272293, -1.6038300418910831, -1.589467384799521, -1.6612806702573308],
            "Shimmer_40AC_Battery_CAL": [4139.194139194139, 4137.728937728937, 4111.355311355311, 4140.65934065934, 4134.798534798534],
            "Shimmer_40AC_Ext_Exp_A15_CAL": [1684.9816849816848, 1673.260073260073, 1901.098901098901, 1722.3443223443223, 1678.3882783882782],
            "Shimmer_40AC_GSR_Range_CAL": [2.0, 2.0, 2.0, 2.0, 2.0],
            "Shimmer_40AC_GSR_Skin_Conductance_CAL": [2.493040293040293, 2.4915750915750916, 2.49010989010989, 2.4886446886446887, 2.4886446886446887],
            "Shimmer_40AC_GSR_Skin_Resistance_CAL": [401.1166617690273, 401.3525433695972, 401.58870255957635, 401.8251398292611, 401.8251398292611],
            "Shimmer_40AC_Gyro_X_CAL": [0.13740458015267176, 0.183206106870229, 0.2748091603053435, 0.22900763358778625, 0.13740458015267176],
            "Shimmer_40AC_Gyro_Y_CAL": [1.8778625954198473, 1.3282442748091603, 1.282442748091603, 1.450381679389313, 1.5114503816793892],
            "Shimmer_40AC_Gyro_Z_CAL": [-0.183206106870229, -0.41221374045801523, -0.1984732824427481, -0.12213740458015267, -0.47328244274809156],
            "Shimmer_40AC_Int_Exp_A12_CAL": [1680.5860805860805, 1703.296703296703, 1687.179487179487, 1650.5494505494505, 1701.8315018315018],
            "Shimmer_40AC_Mag_X_CAL": [-0.11244377811094453, -0.10944527736131934, -0.10794602698650674, -0.10644677661169415, -0.11394302848575712],
            "Shimmer_40AC_Mag_Y_CAL": [-0.9160419790104948, -0.9130434782608695, -0.9100449775112444, -0.9010494752623688, -0.9040479760119939],
            "Shimmer_40AC_Mag_Z_CAL": [-0.047976011994003, -0.047976011994003, -0.04947526236881559, -0.050974512743628186, -0.037481259370314844],
            "Shimmer_40AC_Pressure_BMP280_CAL": [100.43537920858897, 100.4297311006671, 100.44102732749235, 100.44102732749235, 100.43820326666797],
            "Shimmer_40AC_Temperature_BMP280_CAL": [33.365877509029815, 33.365877509029815, 33.365877509029815, 33.365877509029815, 33.365877509029815],
            'acc_mag': [10.1176036 , 10.11303086, 10.1176036 , 10.11280889, 10.11686206]},
            index=pd.to_datetime(["2020-07-28 10:56:50.034", "2020-07-28 10:56:50.057", "2020-07-28 10:56:50.074", "2020-07-28 10:56:50.099", "2020-07-28 10:56:50.111"])
        )
        self.expected_head.index.name = 'time'

        self.expected_units = pd.Series(
            {'Shimmer_40AC_Timestamp_Unix_CAL': 'ms',
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
            'Shimmer_40AC_Temperature_BMP280_CAL': 'Degrees Celsius',
            'acc_mag': 'm/(s^2)'}
        )

        self.reader = devicely.ShimmerPlusReader(self.READ_PATH)


    def test_basic_read(self):
        self.assertEqual(self.reader.delimiter, self.expected_delimiter)
        pd.testing.assert_frame_equal(self.reader.data.head().reset_index(drop=True),
                                      self.expected_head.reset_index(drop=True))
        pd.testing.assert_index_equal(self.reader.data.head().index.round('ms'),
                                      self.expected_head.index.round('ms'))
        pd.testing.assert_series_equal(self.reader.units, self.expected_units, check_names=False)

    def test_write(self):
        self.reader.write(self.WRITE_PATH)
        new_reader = devicely.ShimmerPlusReader(self.WRITE_PATH)
        self.assertEqual(new_reader.delimiter, self.reader.delimiter)
        pd.testing.assert_frame_equal(new_reader.data.reset_index(drop=True), 
                                      self.reader.data.reset_index(drop=True))
        pd.testing.assert_index_equal(new_reader.data.index.round('s'), self.reader.data.index.round('s'))
        pd.testing.assert_series_equal(new_reader.units, self.reader.units)
        os.remove(self.WRITE_PATH)

if __name__ == '__main__':
    unittest.main()
