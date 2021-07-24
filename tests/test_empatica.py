import os
import shutil
import unittest

import pandas as pd

import devicely

class EmpaticaTestCase(unittest.TestCase):
    READ_PATH = 'tests/Empatica_test_data/test_data_read'
    WRITE_PATH = 'tests/Empatica_test_data/test_data_write'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reader = devicely.EmpaticaReader(self.READ_PATH)

        self.expected_start_times = {
            'ACC': pd.Timestamp(1551453301, unit='s'),
            'BVP': pd.Timestamp(1551453301, unit='s'),
            'EDA': pd.Timestamp(1551453301, unit='s'),
            'HR': pd.Timestamp(1551453311, unit='s'),
            'IBI': pd.Timestamp(1551453301, unit='s'),
            'TEMP': pd.Timestamp(1551453301, unit='s'),
        }

        self.expected_sample_freqs = {
            'ACC': 32,
            'BVP': 64,
            'EDA': 4,
            'HR': 1,
            'TEMP': 4,
        }
        
        self.expected_ACC_head = pd.DataFrame(
            {'X': [-1.0, -1.0, -1.0, -1.0, -1.0],
             'Y': [65.0, 65.0, 65.0, 65.0, 64.0],
             'Z': [5.0, 5.0, 4.0, 5.0, 5.0],
             'mag': [65.19969325, 65.19969325, 65.13063795, 65.19969325, 64.20280368]},
            index=pd.DatetimeIndex(['2019-03-01 15:15:01', '2019-03-01 15:15:01.031250',
                                    '2019-03-01 15:15:01.062500', '2019-03-01 15:15:01.093750',
                                    '2019-03-01 15:15:01.125000'])
        )
        
        self.expected_BVP_head = pd.Series(
            [0.0, 0.0, 0.0, 0.0, 0.0],
            index=pd.DatetimeIndex(['2019-03-01 15:15:01', '2019-03-01 15:15:01.015625',
                                    '2019-03-01 15:15:01.031250', '2019-03-01 15:15:01.046875',
                                    '2019-03-01 15:15:01.062500']),
            name='BVP'
        )

        self.expected_EDA_head = pd.Series(
            [0.0, 0.0, 0.005126, 0.003844, 0.003844],
            index=pd.DatetimeIndex(['2019-03-01 15:15:01', '2019-03-01 15:15:01.250000',
                                    '2019-03-01 15:15:01.500000', '2019-03-01 15:15:01.750000',
                                    '2019-03-01 15:15:02']),
            name='EDA'
        )

        self.expected_HR_head = pd.Series(
            [88.0, 88.0, 88.67, 85.0, 89.8],
            index=pd.DatetimeIndex(['2019-03-01 15:15:11', '2019-03-01 15:15:12',
                                    '2019-03-01 15:15:13', '2019-03-01 15:15:14',
                                    '2019-03-01 15:15:15']),
            name='HR'
        )

        self.expected_TEMP_head = pd.Series(
            [23.75, 23.75, 23.75, 23.75, 23.75],
            index=pd.DatetimeIndex(['2019-03-01 15:15:01', '2019-03-01 15:15:01.250000',
                                    '2019-03-01 15:15:01.500000', '2019-03-01 15:15:01.750000',
                                    '2019-03-01 15:15:02']),
            name='TEMP'
        )

        self.expected_IBI_head = pd.DataFrame(
            {'seconds_since_start': [145.631666, 146.522332, 151.725695, 152.835121, 153.710161],
             'IBI': [0.62509, 0.890666, 1.062549, 1.109426, 0.875040]}
        )

        self.expected_tags = pd.Series(pd.to_datetime([1551453311.68, 1551453318.17, 1551453319.49, 1551453328.04], unit='s'), name='tags')


    def _test_compare_real_and_expected(self, reader, expected_start_times, expected_sample_freqs,
                                              expected_ACC_head, expected_BVP_head,
                                              expected_EDA_head, expected_HR_head,
                                              expected_TEMP_head, expected_IBI_head,
                                              expected_tags):
        # helper method to test if a readers attributes match up with expected values

        # test metadata
        self.assertEqual(reader.start_times, expected_start_times)
        self.assertEqual(reader.sample_freqs, expected_sample_freqs)
        
        # test individual dataframes
        pd.testing.assert_frame_equal(reader.ACC.head(), expected_ACC_head, check_dtype=False, check_freq=False)
        pd.testing.assert_series_equal(reader.BVP.head(), expected_BVP_head, check_dtype=False, check_freq=False)
        pd.testing.assert_series_equal(reader.EDA.head(), expected_EDA_head, check_dtype=False, check_freq=False)
        pd.testing.assert_series_equal(reader.HR.head(), expected_HR_head, check_dtype=False, check_freq=False)
        pd.testing.assert_series_equal(reader.TEMP.head(), expected_TEMP_head, check_dtype=False, check_freq=False)
        pd.testing.assert_frame_equal(reader.IBI.head(), expected_IBI_head, check_dtype=False, check_freq=False)
        pd.testing.assert_series_equal(reader.tags, expected_tags, check_freq=False)

        # test joined dataframe
        pd.testing.assert_frame_equal(reader.data[['ACC_X', 'ACC_Y', 'ACC_Z']].dropna().head(),
                                      expected_ACC_head.drop(columns='mag').rename(columns={'X': 'ACC_X', 'Y': 'ACC_Y', 'Z': 'ACC_Z'}), check_dtype=False)
        pd.testing.assert_series_equal(reader.data['BVP'].dropna().head(), expected_BVP_head, check_dtype=False)
        pd.testing.assert_series_equal(reader.data['EDA'].dropna().head(), expected_EDA_head, check_dtype=False)
        pd.testing.assert_series_equal(reader.data['HR'].dropna().head(), expected_HR_head, check_dtype=False)
        pd.testing.assert_series_equal(reader.data['TEMP'].dropna().head(), expected_TEMP_head, check_dtype=False)

    def test_read(self):
        # tests the basic reading capability by comparing the read data to the expected values
        
        self._test_compare_real_and_expected(self.reader, self.expected_start_times, self.expected_sample_freqs,
                                                          self.expected_ACC_head, self.expected_BVP_head,
                                                          self.expected_EDA_head, self.expected_HR_head,
                                                          self.expected_TEMP_head, self.expected_IBI_head,
                                                          self.expected_tags)

    def test_write(self):
        # test the writing capability by writing, reading with a new reader and comparing the old to the new data
        
        self.reader.write(self.WRITE_PATH)
        new_reader = devicely.EmpaticaReader(self.WRITE_PATH)
        self._test_compare_real_and_expected(new_reader, self.expected_start_times, self.expected_sample_freqs,
                                                         self.expected_ACC_head, self.expected_BVP_head,
                                                         self.expected_EDA_head, self.expected_HR_head,
                                                         self.expected_TEMP_head, self.expected_IBI_head,
                                                         self.expected_tags)

        shutil.rmtree(self.WRITE_PATH)

    def test_timeshift_to_timestamp(self):
        # tests timeshifting all of the reader's time-related data to a timestamp

        shift = pd.Timestamp('23.04.2009 06:55:42')
        expected_start_times = {
            'ACC': shift,
            'BVP': shift,
            'EDA': shift,
            'HR': pd.Timestamp('23.04.2009 06:55:52'),
            'IBI': shift,
            'TEMP':shift
        }
        expected_ACC_index_head = pd.DatetimeIndex(['2009-04-23 06:55:42', '2009-04-23 06:55:42.031250',
                                                    '2009-04-23 06:55:42.062500', '2009-04-23 06:55:42.093750',
                                                    '2009-04-23 06:55:42.125000'])
        expected_data_index_head = pd.DatetimeIndex(['2009-04-23 06:55:42', '2009-04-23 06:55:42.015625',
                                                     '2009-04-23 06:55:42.031250', '2009-04-23 06:55:42.046875',
                                                     '2009-04-23 06:55:42.062500'])
        
        reader = devicely.EmpaticaReader(self.READ_PATH)
        reader.timeshift(shift)

        self.assertEqual(reader.start_times, expected_start_times)
        pd.testing.assert_index_equal(reader.ACC.head().index, expected_ACC_index_head)
        pd.testing.assert_index_equal(reader.data.head().index, expected_data_index_head)

    def test_timeshift_by_timedelta(self):
        # tests timeshifting all of the reader's time-related data by a timedelta

        shift = pd.Timedelta('- 7 days, 4 hours, 21 minutes, 32 seconds')
        expected_start_times = {
            'ACC': pd.Timestamp('2019-02-22 10:53:29'),
            'BVP': pd.Timestamp('2019-02-22 10:53:29'),
            'EDA': pd.Timestamp('2019-02-22 10:53:29'),
            'HR': pd.Timestamp('2019-02-22 10:53:39'),
            'IBI': pd.Timestamp('2019-02-22 10:53:29'),
            'TEMP':pd.Timestamp('2019-02-22 10:53:29')
        }
        expected_EDA_index_head = pd.DatetimeIndex(['2019-02-22 10:53:29', '2019-02-22 10:53:29.250000',
                                                    '2019-02-22 10:53:29.500000', '2019-02-22 10:53:29.750000',
                                                    '2019-02-22 10:53:30'])
        expected_data_index_head = pd.DatetimeIndex(['2019-02-22 10:53:29', '2019-02-22 10:53:29.015625',
                                                     '2019-02-22 10:53:29.031250', '2019-02-22 10:53:29.046875',
                                                     '2019-02-22 10:53:29.062500'])

        reader = devicely.EmpaticaReader(self.READ_PATH)
        reader.timeshift(shift)

        self.assertEqual(reader.start_times, expected_start_times)
        pd.testing.assert_index_equal(reader.EDA.head().index, expected_EDA_index_head)
        pd.testing.assert_index_equal(reader.data.head().index, expected_data_index_head)

    def test_random_timeshift(self):
        earliest_possible_start_times = {
            'ACC': pd.Timestamp('2017-03-01 15:15:01'),
            'BVP': pd.Timestamp('2017-03-01 15:15:01'),
            'EDA': pd.Timestamp('2017-03-01 15:15:01'),
            'HR': pd.Timestamp('2017-03-01 15:15:11'),
            'IBI': pd.Timestamp('2017-03-01 15:15:01'),
            'TEMP':pd.Timestamp('2017-03-01 15:15:01')
        }
        latest_possible_start_times = {
            'ACC': pd.Timestamp('2019-01-30 15:15:01'),
            'BVP': pd.Timestamp('2019-01-30 15:15:01'),
            'EDA': pd.Timestamp('2019-01-30 15:15:01'),
            'HR': pd.Timestamp('2019-01-30 15:15:11'),
            'IBI': pd.Timestamp('2019-01-30 15:15:01'),
            'TEMP': pd.Timestamp('2019-01-30 15:15:01')
        }
        earliest_possible_TEMP_index_head = pd.DatetimeIndex(['2017-03-01 15:15:01', '2017-03-01 15:15:01.250000',
                                                              '2017-03-01 15:15:01.500000', '2017-03-01 15:15:01.750000',
                                                              '2017-03-01 15:15:02'])
        latest_possible_TEMP_index_head = pd.DatetimeIndex(['2019-01-30 15:15:01', '2019-01-30 15:15:01.250000',
                                                            '2019-01-30 15:15:01.500000', '2019-01-30 15:15:01.750000',
                                                            '2019-01-30 15:15:02'])

        earliest_possible_data_index_head = pd.DatetimeIndex(['2017-03-01 15:15:01', '2017-03-01 15:15:01.015625',
                                                              '2017-03-01 15:15:01.031250', '2017-03-01 15:15:01.046875',
                                                              '2017-03-01 15:15:01.062500'])
        latest_possible_data_index_head = pd.DatetimeIndex(['2019-01-30 15:15:01', '2019-01-30 15:15:01.015625',
                                                            '2019-01-30 15:15:01.031250', '2019-01-30 15:15:01.046875',
                                                            '2019-01-30 15:15:01.062500'])

        reader = devicely.EmpaticaReader(self.READ_PATH)
        reader.timeshift()

        for signal_name, start_time in reader.start_times.items():
            self.assertLess(earliest_possible_start_times[signal_name], start_time)
            self.assertLess(start_time, latest_possible_start_times[signal_name])

        self.assertTrue((earliest_possible_TEMP_index_head <= reader.TEMP.head().index).all())
        self.assertTrue((reader.TEMP.head().index <= latest_possible_TEMP_index_head).all())

        self.assertTrue((earliest_possible_data_index_head <= reader.data.head().index).all())
        self.assertTrue((reader.data.head().index <= latest_possible_data_index_head).all())



if __name__ == '__main__':
    unittest.main()
