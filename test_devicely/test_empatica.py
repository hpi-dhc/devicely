import unittest
from devicely import empatica
import pandas as pd
import random


class EmpaticaTestCase(unittest.TestCase):
    def setUp(self):
        self.empatica_reader = empatica.EmpaticaReader('Empatica_test_data')
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

    def test_read_signals(self):
        pd.testing.assert_frame_equal(self.empatica_reader.ACC, self.acc_df)
        pd.testing.assert_frame_equal(self.empatica_reader.BVP, self.bvp_df)
        pd.testing.assert_frame_equal(self.empatica_reader.EDA, self.eda_df)
        pd.testing.assert_frame_equal(self.empatica_reader.HR, self.hr_df)
        pd.testing.assert_frame_equal(self.empatica_reader.IBI, self.ibi_df)
        pd.testing.assert_frame_equal(self.empatica_reader.TEMP, self.temp_df)

    def test_read_start_times(self):
        self.assertEquals(self.empatica_reader.start_times, self.start_times)

    def test_read_sample_freqs(self):
        self.assertEquals(self.empatica_reader.sample_freqs, self.sample_freqs)

        if __name__ == '__main__':
            unittest.main()
