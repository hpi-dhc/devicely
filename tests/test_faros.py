import os
import shutil
import unittest

import numpy as np
import pandas as pd


import devicely

class FarosTestCase(unittest.TestCase):
    EDF_READ_PATH = 'tests/Faros_test_data/testfile_read.EDF'
    EDF_WRITE_PATH = 'tests/Faros_test_data/testfile_write.EDF'
    DIR_READ_PATH = 'tests/Faros_test_data/testdir_read'
    DIR_WRITE_PATH = 'tests/Faros_test_data/testdir_write'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reader_from_edf = devicely.FarosReader(self.EDF_READ_PATH)
        self.reader_from_dir = devicely.FarosReader(self.DIR_READ_PATH)
        
        self.expected_start_time = pd.Timestamp('2018-10-12 16:54:12')
        self.expected_sample_freqs = {
            'ECG': 500.0,
            'ACC': 25.0,
            'Marker': 1.0,
            'HRV': 5.0
        }
        self.expected_units = {
            'ECG': 'uV',
            'ACC': 'mg',
            'HRV': 'ms'
        }
        self.expected_edf_metadata = [
            {'label': 'ECG',
            'dimension': 'uV',
            'sample_rate': 500.0,
            'physical_max': 32767.0,
            'physical_min': -32768.0,
            'digital_max': 32767,
            'digital_min': -32768,
            'prefilter': '',
            'transducer': 'ECG electrode'},
            {'label': 'Accelerometer_X',
            'dimension': 'mg',
            'sample_rate': 25.0,
            'physical_max': 4000.0,
            'physical_min': -4000.0,
            'digital_max': 8000,
            'digital_min': -8000,
            'prefilter': '',
            'transducer': 'X-axis'},
            {'label': 'Accelerometer_Y',
            'dimension': 'mg',
            'sample_rate': 25.0,
            'physical_max': 4000.0,
            'physical_min': -4000.0,
            'digital_max': 8000,
            'digital_min': -8000,
            'prefilter': '',
            'transducer': 'Y-axis'},
            {'label': 'Accelerometer_Z',
            'dimension': 'mg',
            'sample_rate': 25.0,
            'physical_max': 4000.0,
            'physical_min': -4000.0,
            'digital_max': 8000,
            'digital_min': -8000,
            'prefilter': '',
            'transducer': 'Z-axis'},
            {'label': 'Marker',
            'dimension': '',
            'sample_rate': 1.0,
            'physical_max': 32767.0,
            'physical_min': -32768.0,
            'digital_max': 32767,
            'digital_min': -32768,
            'prefilter': '',
            'transducer': 'Event marker'},
            {'label': 'HRV',
            'dimension': 'ms',
            'sample_rate': 5.0,
            'physical_max': 65535.0,
            'physical_min': 0.0,
            'digital_max': 32767,
            'digital_min': -32768,
            'prefilter': '',
            'transducer': 'Heart Rate Variability'}
        ]

        self.expected_ECG_head = pd.Series(
            [-2134., -1631.,  -944.,   -45.,   538.],
            name='ECG',
            index=pd.DatetimeIndex(['2018-10-12 16:54:12', '2018-10-12 16:54:12.002000',
                                    '2018-10-12 16:54:12.004000', '2018-10-12 16:54:12.006000',
                                    '2018-10-12 16:54:12.008000'],
                                    dtype='datetime64[ns]', freq='2L')
        )
        self.expected_ACC_head = pd.DataFrame(
            {'X': [ 308.5,  289. ,  335.5,  375. ,  382.5],
             'Y': [-645. , -668. , -682. , -707.5, -670. ],
             'Z': [-523.5, -623.5, -674. , -623.5, -621.5],
             'mag': [ 886.14304714,  958.38262192, 1015.85444331, 1014.85639378, 990.69092052]},
             index=pd.DatetimeIndex(['2018-10-12 16:54:12', '2018-10-12 16:54:12.040000',
                                     '2018-10-12 16:54:12.080000', '2018-10-12 16:54:12.120000',
                                     '2018-10-12 16:54:12.160000'],
                                     dtype='datetime64[ns]', freq='40L')
        )
        self.expected_Marker_head = pd.Series(
            [0., 0., 0., 0., 0.],
            name='Marker',
            index=pd.DatetimeIndex(['2018-10-12 16:54:12', '2018-10-12 16:54:13',
                                    '2018-10-12 16:54:14', '2018-10-12 16:54:15',
                                    '2018-10-12 16:54:16'],
                                    dtype='datetime64[ns]', freq='S')
        )
        self.expected_HRV_head = pd.Series(
            [0., 0., 0., 0., 0.],
            name='HRV',
            index=pd.DatetimeIndex(['2018-10-12 16:54:12', '2018-10-12 16:54:12.200000',
                                    '2018-10-12 16:54:12.400000', '2018-10-12 16:54:12.600000',
                                    '2018-10-12 16:54:12.800000'],
                                    dtype='datetime64[ns]', freq='200L')
        )


    def _compare_reader_with_expected_attrs(self, reader, expected_start_time, expected_sample_freqs,
                                                   expected_units, expected_ECG_head,
                                                   expected_ACC_head, expected_Marker_head,
                                                   expected_HRV_head, expected_edf_metadata=None):
        self.assertEqual(reader.start_time, expected_start_time)
        self.assertEqual(reader.sample_freqs, expected_sample_freqs)
        self.assertEqual(reader.units, expected_units)
        self.assertEqual(reader._edf_metadata, expected_edf_metadata)
        pd.testing.assert_series_equal(reader.ECG.head(), expected_ECG_head, check_freq=False, check_dtype=False)
        pd.testing.assert_frame_equal(reader.ACC.head(), expected_ACC_head, check_freq=False, check_dtype=False)
        pd.testing.assert_series_equal(reader.Marker.head(), expected_Marker_head, check_freq=False, check_dtype=False)
        pd.testing.assert_series_equal(reader.HRV.head(), expected_HRV_head, check_freq=False, check_dtype=False)

        # test if the reader's joined dataframe is correct
        pd.testing.assert_series_equal(
            reader.data['ECG'].dropna().head(), expected_ECG_head,
            check_freq=False, check_dtype=False
        )
        pd.testing.assert_frame_equal(
            reader.data[['ACC_X', 'ACC_Y', 'ACC_Z', 'ACC_mag']].dropna().head(),
            expected_ACC_head.rename(columns={'X': 'ACC_X',
                                              'Y': 'ACC_Y',
                                              'Z': 'ACC_Z',
                                              'mag': 'ACC_mag'}),
                                     check_freq=False,
                                     check_dtype=False
        )
        pd.testing.assert_series_equal(
            reader.data['Marker'].dropna().head(),
            expected_Marker_head, check_freq=False, check_dtype=False
        )
        pd.testing.assert_series_equal(
            reader.data['HRV'].dropna().head(),
            expected_HRV_head, check_freq=False, check_dtype=False
        )

    def test_read_from_edf(self):
        """
        Tests if the reader that's created from a Faros-generated EDF file contains the expected values.
        """
        self._compare_reader_with_expected_attrs(self.reader_from_edf,
                                          self.expected_start_time, self.expected_sample_freqs,
                                          self.expected_units, self.expected_ECG_head,
                                          self.expected_ACC_head, self.expected_Marker_head,
                                          self.expected_HRV_head,
                                          expected_edf_metadata=self.expected_edf_metadata)

    def test_read_from_dir(self):
        """
        Tests if the reader that's created from a devicely-generated Faros directory contains the expected values.
        """
        self._compare_reader_with_expected_attrs(self.reader_from_dir,
                                          self.expected_start_time, self.expected_sample_freqs,
                                          self.expected_units, self.expected_ECG_head,
                                          self.expected_ACC_head, self.expected_Marker_head,
                                          self.expected_HRV_head)

    def test_write_to_dir(self):
        """
        Tests if both a reader created from an edf file and a reader created from a directory
        can be written back to a directory.
        """
        self.reader_from_edf.write(self.DIR_WRITE_PATH)
        new_reader = devicely.FarosReader(self.DIR_WRITE_PATH)
        
        self._compare_reader_with_expected_attrs(new_reader,
                                        self.expected_start_time, self.expected_sample_freqs,
                                        self.expected_units, self.expected_ECG_head,
                                        self.expected_ACC_head, self.expected_Marker_head,
                                        self.expected_HRV_head)

        
        shutil.rmtree(self.DIR_WRITE_PATH)

    def test_write_to_edf(self):
        """
        Tests if a reader's data can be written to an EDF file.
        """
        self.reader_from_edf.write(self.EDF_WRITE_PATH, format='edf')
        new_reader = devicely.FarosReader(self.EDF_WRITE_PATH)
        
        self._compare_reader_with_expected_attrs(new_reader,
                                          self.expected_start_time, self.expected_sample_freqs,
                                          self.expected_units, self.expected_ECG_head,
                                          self.expected_ACC_head, self.expected_Marker_head,
                                          self.expected_HRV_head,
                                          expected_edf_metadata=self.expected_edf_metadata)

        os.remove(self.EDF_WRITE_PATH)

    def test_timeshift_to_timestamp(self):
        timestamp = pd.Timestamp('1.2.2019, 21:43:23')

        expected_shifted_ecg_index_head = pd.DatetimeIndex(['2019-01-02 21:43:23', '2019-01-02 21:43:23.002000',
                                                            '2019-01-02 21:43:23.004000', '2019-01-02 21:43:23.006000',
                                                            '2019-01-02 21:43:23.008000'])
        expected_shifted_acc_index_head = pd.DatetimeIndex(['2019-01-02 21:43:23', '2019-01-02 21:43:23.040000',
                                                            '2019-01-02 21:43:23.080000', '2019-01-02 21:43:23.120000',
                                                            '2019-01-02 21:43:23.160000'])
        expected_shifted_marker_index_head = pd.DatetimeIndex(['2019-01-02 21:43:23', '2019-01-02 21:43:24',
                                                               '2019-01-02 21:43:25', '2019-01-02 21:43:26',
                                                               '2019-01-02 21:43:27'])
        expected_shifted_hrv_index_head = pd.DatetimeIndex(['2019-01-02 21:43:23', '2019-01-02 21:43:23.200000',
                                                            '2019-01-02 21:43:23.400000', '2019-01-02 21:43:23.600000',
                                                            '2019-01-02 21:43:23.800000'])
        expected_shifted_data_index_head = pd.DatetimeIndex(['2019-01-02 21:43:23', '2019-01-02 21:43:23.002000',
                                                            '2019-01-02 21:43:23.004000', '2019-01-02 21:43:23.006000',
                                                            '2019-01-02 21:43:23.008000'])

        # We need to use a reader other then self.reader_from_edf or self.reader_from_dir
        # to not change any of their attributes.
        reader = devicely.FarosReader(self.EDF_READ_PATH)
        reader.timeshift(timestamp)

        self.assertEqual(reader.start_time, timestamp)
        pd.testing.assert_index_equal(reader.ECG.head().index, expected_shifted_ecg_index_head)
        pd.testing.assert_index_equal(reader.ACC.head().index, expected_shifted_acc_index_head)
        pd.testing.assert_index_equal(reader.Marker.head().index, expected_shifted_marker_index_head)
        pd.testing.assert_index_equal(reader.HRV.head().index, expected_shifted_hrv_index_head)
        pd.testing.assert_index_equal(reader.data.head().index, expected_shifted_data_index_head)


    def test_timeshift_by_timedelta(self):
        timedelta = pd.Timedelta('- 32 days, 9 hours, 34 minutes, 12 seconds')

        expected_shifted_ecg_index_head = pd.DatetimeIndex(['2018-09-10 07:20:00', '2018-09-10 07:20:00.002000',
                                                            '2018-09-10 07:20:00.004000', '2018-09-10 07:20:00.006000',
                                                            '2018-09-10 07:20:00.008000'])
        expected_shifted_acc_index_head = pd.DatetimeIndex(['2018-09-10 07:20:00', '2018-09-10 07:20:00.040000',
                                                            '2018-09-10 07:20:00.080000', '2018-09-10 07:20:00.120000',
                                                            '2018-09-10 07:20:00.160000'])
        expected_shifted_marker_index_head = pd.DatetimeIndex(['2018-09-10 07:20:00', '2018-09-10 07:20:01',
                                                               '2018-09-10 07:20:02', '2018-09-10 07:20:03',
                                                               '2018-09-10 07:20:04'])
        expected_shifted_hrv_index_head = pd.DatetimeIndex(['2018-09-10 07:20:00', '2018-09-10 07:20:00.200000',
                                                            '2018-09-10 07:20:00.400000', '2018-09-10 07:20:00.600000',
                                                            '2018-09-10 07:20:00.800000'])
        expected_shifted_data_index_head = pd.DatetimeIndex(['2018-09-10 07:20:00', '2018-09-10 07:20:00.002000',
                                                             '2018-09-10 07:20:00.004000', '2018-09-10 07:20:00.006000',
                                                             '2018-09-10 07:20:00.008000'])

        reader = devicely.FarosReader(self.EDF_READ_PATH)
        reader.timeshift(timedelta)

        pd.testing.assert_index_equal(reader.ECG.head().index, expected_shifted_ecg_index_head)
        pd.testing.assert_index_equal(reader.ACC.head().index, expected_shifted_acc_index_head)
        pd.testing.assert_index_equal(reader.Marker.head().index, expected_shifted_marker_index_head)
        pd.testing.assert_index_equal(reader.HRV.head().index, expected_shifted_hrv_index_head)
        pd.testing.assert_index_equal(reader.data.head().index, expected_shifted_data_index_head)

    def test_random_timeshift(self):
        latest_possible_shifted_data_index = pd.DatetimeIndex(['2018-09-12 16:54:12', '2018-09-12 16:54:12.002000',
                                                               '2018-09-12 16:54:12.004000', '2018-09-12 16:54:12.006000',
                                                               '2018-09-12 16:54:12.008000'])
        earliest_possible_shifted_data_index = pd.DatetimeIndex(['2016-10-12 16:54:12', '2016-10-12 16:54:12.002000',
                                                                 '2016-10-12 16:54:12.004000', '2016-10-12 16:54:12.006000',
                                                                 '2016-10-12 16:54:12.008000'])

        reader = devicely.FarosReader(self.EDF_READ_PATH)
        reader.timeshift()

        self.assertTrue((earliest_possible_shifted_data_index <= reader.data.head().index).all())
        self.assertTrue((reader.data.head().index <= latest_possible_shifted_data_index).all())

if __name__ == '__main__':
    unittest.main()
