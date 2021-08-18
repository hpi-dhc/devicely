"""
Tests for the Spacelabs module
"""
import datetime as dt
import os
import unittest

import numpy as np
import pandas as pd

import devicely


class SpacelabsTestCase(unittest.TestCase):
    READ_PATH = "tests/SpaceLabs_test_data/spacelabs.abp"
    READ_PATH_REPEATED = "tests/SpaceLabs_test_data/spacelabs_repeated.abp"
    WRITE_PATH = "tests/SpaceLabs_test_data/spacelabs_written.abp"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expected_subject = "000002"
        timestamps = pd.to_datetime([
            "1.1.99 17:03",
            "1.1.99 17:05",
            "1.1.99 17:07",
            "1.1.99 17:09",
            "1.1.99 17:11",
            "1.1.99 17:13",
            "1.1.99 17:25",
            "1.1.99 17:28",
            "1.1.99 17:31",
            "1.1.99 17:34",
            "1.1.99 17:36",
            "1.1.99 17:39",
            "1.1.99 23:42",
            "1.1.99 23:59",
            "1.2.99 00:01",
        ])

        timestamps_repeated = pd.to_datetime([
            "1.1.99 17:05",
            "1.1.99 17:05",
            "1.1.99 17:07",
            "1.1.99 17:09",
            "1.1.99 17:11",
            "1.1.99 17:13",
            "1.1.99 17:25",
            "1.1.99 17:28",
            "1.1.99 17:31",
            "1.1.99 17:34",
            "1.1.99 17:36",
            "1.1.99 17:39",
            "1.1.99 23:42",
            "1.1.99 23:59",
            "1.2.99 00:01",
        ])

        self.expected_data = pd.DataFrame({
            "timestamp": timestamps,
            "date": timestamps.map(lambda timestamp: timestamp.date()),
            "time": timestamps.map(lambda timestamp: timestamp.time()),
            "SYS(mmHg)": [11, 142, 152, 151, 145, 3, 4, 164, 154, 149, 153, 148, 148, 148, 148],
            "DIA(mmHg)": [0, 118, 112, 115, 110, 0, 0, 119, 116, 119, 118, 114, 114, 114, 114],
            "UNKNOW_1": [0, 99, 95, 96, 91, 0, 0, 95, 95, 98, 96, 93, 93, 93, 93],
            "UNKNOW_2": [0, 61, 61, 61, 59, 0, 0, 63, 63, 63, 60, 62, 62, 62, 62],
            "UNKNOW_3": 15 * [np.nan],
            "CODE": ["EB", np.nan, np.nan, np.nan, np.nan, "EB", "EB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        })

        self.expected_data.set_index('timestamp', inplace=True)

        self.expected_data_repeated = pd.DataFrame({
            "timestamp": timestamps_repeated,
            "date": timestamps_repeated.map(lambda timestamps_repeated: timestamps_repeated.date()),
            "time": timestamps_repeated.map(lambda timestamps_repeated: timestamps_repeated.time()),
            "SYS(mmHg)": [11, 142, 152, 151, 145, 3, 4, 164, 154, 149, 153, 148, 148, 148, 148],
            "DIA(mmHg)": [0, 118, 112, 115, 110, 0, 0, 119, 116, 119, 118, 114, 114, 114, 114],
            "UNKNOW_1": [0, 99, 95, 96, 91, 0, 0, 95, 95, 98, 96, 93, 93, 93, 93],
            "UNKNOW_2": [0, 61, 61, 61, 59, 0, 0, 63, 63, 63, 60, 62, 62, 62, 62],
            "UNKNOW_3": 15 * [np.nan],
            "CODE": ["EB", np.nan, np.nan, np.nan, np.nan, "EB", "EB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        })

        self.expected_data_repeated.set_index('timestamp', inplace=True)

        self.expected_metadata = {
            "PATIENTINFO": {
                "DOB": "16.09.1966",
                "RACE": "native american"
            },
            "REPORTINFO": {
                "PHYSICIAN": "Dr. Hannibal Lecter",
                "NURSETECH": "admin",
                "STATUS": "NOTCONFIRMED",
                "CALIPERSUMMARY": {
                    "COUNT": "0"
                },
            },
        }

    def setUp(self):
        self.spacelabs_reader = devicely.SpacelabsReader(self.READ_PATH)
        self.spacelabs_reader_repertion = devicely.SpacelabsReader(self.READ_PATH_REPEATED)

    def test_read(self):
        # Tests a basic reading operation.
        pd.testing.assert_frame_equal(self.spacelabs_reader.data,
                                      self.expected_data)

        # Test reading a file with repeated timestamp values.
        pd.testing.assert_frame_equal(self.spacelabs_reader_repertion.data,
                                      self.expected_data_repeated)

        self.assertEqual(self.spacelabs_reader.subject, self.expected_subject)
        self.assertEqual(self.spacelabs_reader.metadata,
                         self.expected_metadata)

    def test_deidentify(self):
        # Tests if the SpacelabsReader.deidentify method removes all patient metadata.

        self.spacelabs_reader.deidentify()

        self.assertEqual(self.spacelabs_reader.subject, "")
        self.assertEqual(
            self.spacelabs_reader.metadata,
            {
                "PATIENTINFO": {
                    "DOB": "",
                    "RACE": ""
                },
                "REPORTINFO": {
                    "PHYSICIAN": "",
                    "NURSETECH": "",
                    "STATUS": "",
                    "CALIPERSUMMARY": {
                        "COUNT": ""
                    },
                },
            },
        )

    def test_write(self):
        # Tests the SpacelabsReader.write operation by writing, reading again and comparing the old and new signals.

        self.spacelabs_reader.write(self.WRITE_PATH)
        new_reader = devicely.SpacelabsReader(self.WRITE_PATH)

        pd.testing.assert_frame_equal(new_reader.data,
                                      self.spacelabs_reader.data)
        self.assertEqual(new_reader.metadata, self.spacelabs_reader.metadata)
        self.assertEqual(new_reader.subject, self.spacelabs_reader.subject)

        os.remove(self.WRITE_PATH)

    def test_random_timeshift(self):
        earliest_possible_shifted_time_col = pd.to_datetime([
            '1997-01-01 17:03:00',
            '1997-01-01 17:05:00',
            '1997-01-01 17:07:00',
            '1997-01-01 17:09:00',
            '1997-01-01 17:11:00',
            '1997-01-01 17:13:00',
            '1997-01-01 17:25:00',
            '1997-01-01 17:28:00',
            '1997-01-01 17:31:00',
            '1997-01-01 17:34:00',
            '1997-01-01 17:36:00',
            '1997-01-01 17:39:00',
            '1997-01-01 23:42:00',
            '1997-01-01 23:59:00',
            '1997-01-02 00:01:00'
        ])
        latest_possible_shifted_time_col = pd.to_datetime([
            '1998-12-02 17:03:00',
            '1998-12-02 17:05:00',
            '1998-12-02 17:07:00',
            '1998-12-02 17:09:00',
            '1998-12-02 17:11:00',
            '1998-12-02 17:13:00',
            '1998-12-02 17:25:00',
            '1998-12-02 17:28:00',
            '1998-12-02 17:31:00',
            '1998-12-02 17:34:00',
            '1998-12-02 17:36:00',
            '1998-12-02 17:39:00',
            '1998-12-02 23:42:00',
            '1998-12-02 23:59:00',
            '1998-12-03 00:01:00'
        ])

        self.spacelabs_reader.timeshift()
        new_timestamp_column = pd.Series(self.spacelabs_reader.data.index)

        self.assertTrue((earliest_possible_shifted_time_col <= new_timestamp_column).all())
        self.assertTrue((new_timestamp_column <= latest_possible_shifted_time_col).all())

        new_date_column = self.spacelabs_reader.data["date"]
        new_time_column = self.spacelabs_reader.data["time"]
        testing_timestamp_column = pd.Series([
            dt.datetime.combine(new_date_column[i], new_time_column[i])
            for i in range(len(self.spacelabs_reader.data))
        ])

        pd.testing.assert_series_equal(new_timestamp_column, testing_timestamp_column, check_names=False)

if __name__ == "__main__":
    unittest.main()
