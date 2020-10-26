import unittest
import pandas as pd
import numpy as np
import devicely


class SpacelabsTestCase(unittest.TestCase):
    READ_PATH = 'SpaceLabs_test_data_read/spacelabs.abp'

    def setUp(self):
        timestamps = ['2019-03-01 16:18:00', '2019-03-01 16:19:00', '2019-03-01 16:22:00', '2019-03-01 16:23:00',
                      '2019-03-01 16:25:00', '2019-03-01 16:33:00', '2019-03-01 16:35:00', '2019-03-01 16:37:00',
                      '2019-03-01 16:38:00', '2019-03-01 23:59:00', '2019-03-02 00:00:00', '2019-03-02 00:01:00',
                      '2019-03-02 04:20:00', '2019-03-02 05:27:00']

        sys = [107, 96, 100, 103, 101, 107, 104, 105, 100, 100, 100, 100, 100, 100]
        dia = [76, 62, 68, 68, 67, 67, 71, 52, 68, 68, 68, 68, 68, 68]
        x = [78, 63, 64, 68, 65, 77, 70, 76, 68, 68, 68, 68, 68, 68]
        y = [78, 63, 64, 68, 65, 77, 70, 76, 68, 68, 68, 68, 68, 68]
        error = z = stress_test = 14 * [np.nan]

        self.data = pd.DataFrame({
            'timestamp': pd.to_datetime(timestamps),
            'SYS(mmHg)': sys,
            'DIA(mmHg)': dia,
            'x': x,
            'y': y,
            'z': z,
            'error': error,
            'stress_test': stress_test
        })
        self.data.set_index('timestamp', inplace=True)

        self.subject = '001V0'

        self.xml = {'PATIENTINFO': {'DOB': '16.09.1966', 'RACE': 'native american'},
                    'REPORTINFO': {'PHYSICIAN': 'Dr. Hannibal Lecter',
                                   'NURSETECH': 'admin',
                                   'STATUS': 'NOTCONFIRMED',
                                   'CALIPERSUMMARY': {'COUNT': '0'}}}

        self.spacelabs_reader = devicely.SpacelabsReader(self.READ_PATH)

    def test_read(self):
        pd.testing.assert_frame_equal(self.spacelabs_reader.data, self.data)
        #self.assertEquals(self.spacelabs_reader.subject, self.subject)
        #self.assertEquals(self.spacelabs_reader.metadata, self.xml)

if __name__ == '__main__':
    unittest.main()
