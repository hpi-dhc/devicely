import datetime as dt
import os
import unittest

import numpy as np
import pandas as pd

import devicely

class SpacelabsTestCase(unittest.TestCase):
    READ_PATH = 'tests/SpaceLabs_test_data/spacelabs.abp'
    WRITE_PATH = 'tests/SpaceLabs_test_data/spacelabs_written.abp'

    def setUp(self):
        self.subject = '000002'

        timestamps = pd.to_datetime(
            ['1.1.99 17:03', '1.1.99 17:05', '1.1.99 17:07', '1.1.99 17:09', '1.1.99 17:11', '1.1.99 17:13',
             '1.1.99 17:25', '1.1.99 17:28', '1.1.99 17:31', '1.1.99 17:34', '1.1.99 17:36',
             '1.1.99 17:39', '1.1.99 23:42', '1.1.99 23:59', '1.2.99 00:01'])

        self.data = pd.DataFrame({
            'timestamp': timestamps,
            'date': timestamps.map(lambda timestamp: timestamp.date()),
            'time': timestamps.map(lambda timestamp: timestamp.time()),
            'SYS(mmHg)': [11, 142, 152, 151, 145, 3, 4, 164, 154, 149, 153, 148, 148, 148, 148],
            'DIA(mmHg)': [0, 118, 112, 115, 110, 0, 0, 119, 116, 119, 118, 114, 114, 114, 114],
            'x': [0, 99, 95, 96, 91, 0, 0, 95, 95, 98, 96, 93, 93, 93, 93],
            'y': [0, 61, 61, 61, 59, 0, 0, 63, 63, 63, 60, 62, 62, 62, 62],
            'z': 15 * [np.nan],
            'error': ['EB', np.nan, np.nan, np.nan, np.nan, 'EB', 'EB', np.nan, np.nan, np.nan, np.nan, np.nan,
                      np.nan, np.nan, np.nan]
        })

        self.xml = {'PATIENTINFO': {'DOB': '16.09.1966', 'RACE': 'native american'},
                    'REPORTINFO': {'PHYSICIAN': 'Dr. Hannibal Lecter',
                                   'NURSETECH': 'admin',
                                   'STATUS': 'NOTCONFIRMED',
                                   'CALIPERSUMMARY': {'COUNT': '0'}}}

        self.spacelabs_reader = devicely.SpacelabsReader(self.READ_PATH)

    def test_read(self):
        pd.testing.assert_frame_equal(self.spacelabs_reader.data, self.data)
        self.assertEqual(self.spacelabs_reader.subject, self.subject)
        self.assertEqual(self.spacelabs_reader.metadata, self.xml)

    def test_deidentify(self):
        self.spacelabs_reader.deidentify()
        self.spacelabs_reader.write(self.WRITE_PATH)
        read_file_contents = open(self.READ_PATH, 'r').readlines()
        written_file_contents = open(self.WRITE_PATH, 'r').readlines()
        self.assertEqual(read_file_contents[2:-1], written_file_contents[2:-1])

        read_file_contents = open(self.READ_PATH, 'r').readlines()
        written_file_contents = open(self.WRITE_PATH, 'r').readlines()
        self.assertNotEqual(read_file_contents[1:2], written_file_contents[1:2])

        read_file_contents = open(self.READ_PATH, 'r').readlines()
        written_file_contents = open(self.WRITE_PATH, 'r').readlines()
        self.assertNotEqual(read_file_contents[:-1], written_file_contents[:-1])

        os.remove(self.WRITE_PATH)

    def test_write(self):
        self.spacelabs_reader.write(self.WRITE_PATH)
        read_file_contents = open(self.READ_PATH, 'r').readlines()
        written_file_contents = open(self.WRITE_PATH, 'r').readlines()
        self.assertEqual(read_file_contents, written_file_contents)

        os.remove(self.WRITE_PATH)

    def test_random_timeshift(self):
        old_timestamp_column = self.spacelabs_reader.data.timestamp.copy()
        self.spacelabs_reader.timeshift()
        new_timestamp_column = self.spacelabs_reader.data.timestamp
        new_date_column = self.spacelabs_reader.data.date
        new_time_column = self.spacelabs_reader.data.time

        self.assertTrue((old_timestamp_column - pd.Timedelta('730 days') <= new_timestamp_column).all())
        self.assertTrue((new_timestamp_column <= old_timestamp_column - pd.Timedelta('30 days')).all())

        testing_timestamp_column = pd.Series([dt.datetime.combine(new_date_column[i], new_time_column[i]) for i in
                                  range(len(self.spacelabs_reader.data))])
        testing_timestamp_column.name = 'timestamp'

        pd.testing.assert_series_equal(new_timestamp_column, testing_timestamp_column)

    def test_drop_EB(self):
        self.data.drop(index=[0, 5, 6], inplace=True)
        self.data.set_index('timestamp', inplace=True)

        self.spacelabs_reader.drop_EB()

        pd.testing.assert_frame_equal(self.spacelabs_reader.data, self.data)

if __name__ == '__main__':
    unittest.main()
