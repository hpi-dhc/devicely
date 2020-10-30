import unittest
import pandas as pd
import numpy as np
import devicely
import os
import datetime as dt


class SpacelabsTestCase(unittest.TestCase):
    READ_PATH = 'SpaceLabs_test_data_read/spacelabs.abp'
    WRITE_PATH = 'SpaceLabs_test_data_write/spacelabs_written.abp'

    def setUp(self):
        timestamps = ['2019-03-01 16:18:00', '2019-03-01 16:19:00', '2019-03-01 16:22:00', '2019-03-01 16:23:00',
                      '2019-03-01 16:25:00', '2019-03-01 16:33:00', '2019-03-01 16:35:00', '2019-03-01 16:37:00',
                      '2019-03-01 16:38:00', '2019-03-01 23:59:00', '2019-03-02 00:00:00', '2019-03-02 00:01:00',
                      '2019-03-02 04:20:00', '2019-03-02 05:27:00']
        timestamps = pd.to_datetime(timestamps)
        dates = timestamps.date
        times = timestamps.time

        sys = [107, 96, 100, 103, 101, 107, 104, 105, 100, 100, 100, 100, 100, 100]
        dia = [76, 62, 68, 68, 67, 67, 71, 52, 68, 68, 68, 68, 68, 68]
        x = [78, 63, 64, 68, 65, 77, 70, 76, 68, 68, 68, 68, 68, 68]
        y = [78, 63, 64, 68, 65, 77, 70, 76, 68, 68, 68, 68, 68, 68]
        error = z = stress_test = 14 * [np.nan]

        self.data = pd.DataFrame({
            'date': dates,
            'time': times,
            'timestamp': timestamps,
            'SYS(mmHg)': sys,
            'DIA(mmHg)': dia,
            'x': x,
            'y': y,
            'z': z,
            'error': error,
            'stress_test': stress_test
        })
        numeric_columns = ['SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'z', 'error', 'stress_test']
        self.data.set_index('timestamp', inplace=True)
        self.data[numeric_columns] = self.data[numeric_columns].astype('float')

        self.subject = '001V0'

        self.xml = {'PATIENTINFO': {'DOB': '16.09.1966', 'RACE': 'native american'},
                    'REPORTINFO': {'PHYSICIAN': 'Dr. Hannibal Lecter',
                                   'NURSETECH': 'admin',
                                   'STATUS': 'NOTCONFIRMED',
                                   'CALIPERSUMMARY': {'COUNT': '0'}}}

        self.spacelabs_reader = devicely.SpacelabsReader(self.READ_PATH)

    def test_read(self):
        pd.testing.assert_frame_equal(self.spacelabs_reader.data, self.data)
        self.assertEquals(self.spacelabs_reader.subject, self.subject)
        self.assertEquals(self.spacelabs_reader.metadata, self.xml)

    def test_write(self):
        self.spacelabs_reader.write(self.WRITE_PATH)
        written_file_contents = open(self.WRITE_PATH, 'r').readlines()
        self.assertEquals(written_file_contents[1], "001V0\n")
        self.assertEquals(written_file_contents[9], "0\n")
        self.assertEquals(written_file_contents[17], '01.03.2019\n')
        self.assertEquals(written_file_contents[24], "Unknown Line\n")

        os.remove(self.WRITE_PATH)


    def test_random_timeshift(self):
        old_index = self.spacelabs_reader.data.index
        old_date_column = self.spacelabs_reader.data.date
        old_time_column = self.spacelabs_reader.data.time
        self.spacelabs_reader.timeshift()
        new_index = self.spacelabs_reader.data.index
        new_date_column = self.spacelabs_reader.data.date
        new_time_column = self.spacelabs_reader.data.time

        self.assertTrue((old_index - pd.Timedelta('730 days') <= new_index).all())
        self.assertTrue((new_index <= old_index - pd.Timedelta('30 days')).all())

        testing_index = pd.Index([dt.datetime.combine(new_date_column[i], new_time_column[i]) for i in
                                  range(len(self.spacelabs_reader.data))])

        pd.testing.assert_index_equal(new_index, testing_index)



if __name__ == '__main__':
    unittest.main()
