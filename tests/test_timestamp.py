"""
Tests for the TimeStamp module
"""
import os
import unittest

import pandas as pd

import devicely

class TimeStampTestCase(unittest.TestCase):
    READ_PATH = os.path.join(os.getcwd(), 'tests/Timestamp_test_data/tags.csv')
    WRITE_PATH = os.path.join(os.getcwd(), 'tests/Timestamp_test_data/tags_written.csv')

    def setUp(self):
        tag_number = [1, 2, 3, 4, 5, 6, 7, 8, 8, 12, 13, 14, 16, 17, 18, 19]

        timestamps = pd.to_datetime(['2019-03-01 16:16:37', '2019-03-01 16:17:43',
                                     '2019-03-01 16:18:20', '2019-03-01 16:19:51',
                                     '2019-03-01 16:22:00', '2019-03-01 16:23:34',
                                     '2019-03-01 16:25:07', '2019-03-01 16:26:14',
                                     '2019-03-01 16:31:00', '2019-03-01 16:31:56',
                                     '2019-03-01 16:33:39', '2019-03-01 16:35:16',
                                     '2019-03-01 16:37:00', '2019-03-01 16:38:39',
                                     '2019-03-01 16:38:48', '2019-03-01 16:39:32'])

        tags = ['Shake', 'Start', 'BP Measurement', 'BP Measurement', 'BP Measurement', 'BP Measurement',
                'BP Measurement', 'Stress Test Start', 'Stress Test End', 'BP Measurement', 'BP Measurement',
                'BP Measurement', 'BP Measurement', 'BP Measurement', 'End', 'Shake']

        self.data = pd.DataFrame({'tag_number': tag_number, 'time': timestamps, 'tag': tags}).set_index('time')

        self.tag_reader = devicely.TimeStampReader(self.READ_PATH)

    def test_read(self):
        pd.testing.assert_frame_equal(self.tag_reader.data, self.data)

    def test_write(self):
        with open(self.READ_PATH, 'r') as f:
            read_file_contents = f.readlines()
        self.tag_reader.write(self.WRITE_PATH)
        with open(self.WRITE_PATH, 'r') as f:
            write_file_contents = f.readlines()
        self.assertEqual(read_file_contents, write_file_contents)

        os.remove(self.WRITE_PATH)

    def test_random_timeshift(self):
        old_time_column = self.tag_reader.data.index.copy()
        self.tag_reader.timeshift()
        new_time_column = self.tag_reader.data.index

        self.assertTrue((old_time_column - pd.Timedelta('730 days') <= new_time_column).all())
        self.assertTrue((new_time_column <= old_time_column - pd.Timedelta('30 days')).all())



if __name__ == '__main__':
    unittest.main()
