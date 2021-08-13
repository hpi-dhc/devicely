"""
Tests for the Everion module
"""
import datetime as dt
import glob
import os
import shutil
import unittest

import numpy as np
import pandas as pd
import devicely


class EverionTestCase(unittest.TestCase):
    READ_PATH = 'tests/Everion_test_data'
    BROKEN_READ_PATH = 'tests/Everion_test_data_broken' # for testing with missing files
    WRITE_PATH = 'tests/Everion_test_data_write'

    def setUp(self):
        self.reader = devicely.EverionReader(self.READ_PATH)

    def test_basic_read(self):
        self._test_read_individual_dataframes(self.reader)

        expected_signal_tags = ['heart_rate', 'respiration_rate', 'heart_rate_variability',
                                'oxygen_saturation', 'gsr_electrode', 'temperature_object',
                                'barometer_pressure', 'temperature_local', 'ctemp',
                                'temperature_barometer']
        expected_signal_quality_tags = ['heart_rate_quality', 'respiration_rate_quality',
                                        'heart_rate_variability_quality', 'oxygen_saturation_quality',
                                        'ctemp_quality']
        expected_sensor_tags = ['accz_data', 'led2_data', 'led1_data', 'led4_data',
                                'accy_data', 'accx_data', 'led3_data', 'acc_mag']
        expected_feature_tags = ['inter_pulse_interval', 'inter_pulse_interval_deviation']

        expected_columns = set(expected_signal_tags + expected_signal_quality_tags +
                               expected_sensor_tags + expected_feature_tags)

        self.assertEqual(set(self.reader.data.columns), expected_columns)

    def test_read_with_non_default_tags(self):
        signal_tags = [12, 15, 19, 119, 134]
        sensor_tags = [80, 83, 84, 85, 92]
        feature_tags = [17]
        reader = devicely.EverionReader(self.READ_PATH,
                                        signal_tags=signal_tags,
                                        sensor_tags=sensor_tags,
                                        feature_tags=feature_tags)

        # The individual should dataframes contain all tags, regardless of the initialization parameters.
        self._test_read_individual_dataframes(reader)

        expected_singal_columns = ['respiration_rate', 'temperature_local',
                                   'ctemp', 'temperature_barometer']
        expected_signal_quality_columns = ['respiration_rate_quality', 'ctemp_quality']
        # no acc_mag because 86 (accz_data) is missing
        expected_sensor_columns = ['led1_data', 'led4_data', 'accy_data', 'accx_data']
        #17 is a valid feature column, but it is not present in the testing csv
        expected_feature_columns = []
        expected_columns = set(expected_singal_columns + expected_signal_quality_columns +
                               expected_sensor_columns + expected_feature_columns)

        self.assertEqual(set(reader.data.columns), expected_columns)

    def test_read_with_invalid_tags(self):
        signal_tags = [12, 15, 19, 119, 134, 80] #80 is not a signal tag
        sensor_tags = [80, 83, 84, 85, 92, 70] #70 is not a sensor tag
        feature_tags = [17, 86] #86 is not a sensor tag

        call = lambda: devicely.EverionReader(self.READ_PATH,
                                              signal_tags=signal_tags,
                                              sensor_tags=sensor_tags,
                                              feature_tags=feature_tags)
        self.assertRaises(KeyError, call)

    def test_read_with_missing_files(self):
        print(os.listdir())
        shutil.copytree(self.READ_PATH, self.BROKEN_READ_PATH)
        signals_path = glob.glob(os.path.join(self.BROKEN_READ_PATH, f"*signals*")).pop()
        attributes_dailys_path = glob.glob(os.path.join(self.BROKEN_READ_PATH, f"*attributes_dailys*")).pop()
        os.remove(signals_path)
        os.remove(attributes_dailys_path)
        reader = devicely.EverionReader(self.BROKEN_READ_PATH)

        self.assertIsNone(reader.signals)
        self.assertIsNone(reader.attributes_dailys)

        expected_sensor_tags = ['accz_data', 'led2_data', 'led1_data', 'led4_data',
                                'accy_data', 'accx_data', 'led3_data', 'acc_mag']
        expected_feature_tags = ['inter_pulse_interval', 'inter_pulse_interval_deviation']

        expected_columns = set(expected_sensor_tags + expected_feature_tags)
        self.assertEqual(set(reader.data.columns), expected_columns)

        shutil.rmtree(self.BROKEN_READ_PATH)

    def test_read_with_all_join_files_missing(self):
        #The signals-, sensors-, and features files are the three join files.
        shutil.copytree(self.READ_PATH, self.BROKEN_READ_PATH)
        signals_path = glob.glob(os.path.join(self.BROKEN_READ_PATH, f"*signals*")).pop()
        sensors_path = glob.glob(os.path.join(self.BROKEN_READ_PATH, f"*sensor_data*")).pop()
        features_path = glob.glob(os.path.join(self.BROKEN_READ_PATH, f"*features*")).pop()
        os.remove(signals_path)
        os.remove(sensors_path)
        os.remove(features_path)

        reader = devicely.EverionReader(self.BROKEN_READ_PATH)

        self.assertIsNone(reader.signals)
        self.assertIsNone(reader.sensors)
        self.assertIsNone(reader.features)
        pd.testing.assert_frame_equal(reader.data, pd.DataFrame())

        shutil.rmtree(self.BROKEN_READ_PATH)

    def test_timeshift_to_timestamp(self):
        expected_aggregates_head = pd.DataFrame({
            'count': 5 * [4468],
            'streamType': 5 * [5],
            'tag': [40, 18, 21, 7, 100],
            'time':  pd.to_datetime(5 * [1525200281], unit='s'),
            'values': [-2.0, 0.76, 21.0, 60.0, 0.0],
            'quality': [np.nan, 13.0, np.nan, 0.0, np.nan]
        })
        expected_analytics_events_head = pd.DataFrame({
            "count": [5622, 5621, 5620, 5619, 5618],
            "streamType": 5 * [7],
            "tag": 5 * [1],
            "time": pd.to_datetime([1525204397, 1525204397, 1525204148, 1525204131, 1525203790], unit='s'),
            "values": [22.0, 2.0, 22.0, 22.0, 2.0]
        })
        expected_attributes_dailys_head = pd.DataFrame({
            "count": [14577, 14576, 14575, 14574, 14573],
            "streamType": 5 * [8],
            "tag": 5 * [67],
            "time": pd.to_datetime(5 * [1525207721], unit='s'),
            "values": [2.0, 4.0, 3.0, 11.0, 12.0],
            "quality": [15.0, 9.0, 8.0, 6.0, 5.0]
        })
        expected_everion_events_head = pd.DataFrame({
            "count": 5 * [46912],
            "streamType": 5 * [6],
            "tag": [128, 131, 129, 132, 126],
            "time": pd.to_datetime(5 * [1525192729], unit='s'),
            "values": [65295.0, 900.0, 44310.0, 4096.0, 0.0]
        })
        expected_features_head = pd.DataFrame({
            "count": [787000, 787001, 787002, 787003, 787004],
            "streamType": 5 * [4],
            "tag": 5 * [14],
            "time": pd.to_datetime([1525192675, 1525192675, 1525192676, 1525192677, 1525192678], unit='s'),
            "values": [950.0, 1085.0, 1074.0, 1021.0, 1056.0],
            "quality": [12.0, 11.0, 12.0, 10.0, 11.0]
        })
        expected_sensors_head = pd.DataFrame({
            "count": 5 * [22917264],
            "streamType": 5 * [16],
            "tag": [86, 81, 80, 83, 85],
            "time": pd.to_datetime(5 * [1525192361], unit='s'),
            "values": [2176.0, 51612.0, 668.0, 26377.0, 1232.0]
        })
        expected_signals_head = pd.DataFrame({
            'count': 5 * [806132],
            'streamType': 5 * [2],
            'tag': [71, 13, 6, 66, 12],
            'time': pd.to_datetime(5 * [1525192381], unit='s'),
            'values': [0.0, 21.86422, 65.0, 1.5686275, 18.0],
            'quality': [np.nan, 100.0, 85.0, np.nan, 93.0]
        })

        timestamp = pd.Timestamp('1 May 2018 16:32:41')
        self.reader.timeshift(timestamp)

        pd.testing.assert_frame_equal(self.reader.aggregates.head(), expected_aggregates_head)
        pd.testing.assert_frame_equal(self.reader.analytics_events.head(), expected_analytics_events_head)
        pd.testing.assert_frame_equal(self.reader.attributes_dailys.head(), expected_attributes_dailys_head)
        pd.testing.assert_frame_equal(self.reader.everion_events.head(), expected_everion_events_head)
        pd.testing.assert_frame_equal(self.reader.features.head(), expected_features_head)
        pd.testing.assert_frame_equal(self.reader.signals.head(), expected_signals_head)
        pd.testing.assert_frame_equal(self.reader.sensors.head(), expected_sensors_head)

        new_joined_data_time_col = self.reader.data.index
        self.assertTrue((new_joined_data_time_col.date == dt.date(2018, 5, 1)).all())

    def test_timeshift_by_timedelta(self):
        expected_aggregates_head = pd.DataFrame({
            'count': 5 * [4468],
            'streamType': 5 * [5],
            'tag': [40, 18, 21, 7, 100],
            'time':  pd.to_datetime(5 * [1532216847], unit='s'),
            'values': [-2.0, 0.76, 21.0, 60.0, 0.0],
            'quality': [np.nan, 13.0, np.nan, 0.0, np.nan]
        })
        expected_analytics_events_head = pd.DataFrame({
            "count": [5622, 5621, 5620, 5619, 5618],
            "streamType": 5 * [7],
            "tag": 5 * [1],
            "time": pd.to_datetime([1532220716, 1532220716, 1532220467, 1532220450, 1532220109], unit='s'),
            "values": [22.0, 2.0, 22.0, 22.0, 2.0]
        })
        expected_attributes_dailys_head = pd.DataFrame({
            "count": [14577, 14576, 14575, 14574, 14573],
            "streamType": 5 * [8],
            "tag": 5 * [67],
            "time": pd.to_datetime(5 * [1532220709], unit='s'),
            "values": [2.0, 4.0, 3.0, 11.0, 12.0],
            "quality": [15.0, 9.0, 8.0, 6.0, 5.0]
        })
        expected_everion_events_head = pd.DataFrame({
            "count": 5 * [46912],
            "streamType": 5 * [6],
            "tag": [128, 131, 129, 132, 126],
            "time": pd.to_datetime(5 * [1532220837], unit='s'),
            "values": [65295.0, 900.0, 44310.0, 4096.0, 0.0]
        })
        expected_features_head = pd.DataFrame({
            "count": [787000, 787001, 787002, 787003, 787004],
            "streamType": 5 * [4],
            "tag": 5 * [14],
            "time": pd.to_datetime([1532216891, 1532216891, 1532216892, 1532216893, 1532216894], unit='s'),
            "values": [950.0, 1085.0, 1074.0, 1021.0, 1056.0],
            "quality": [12.0, 11.0, 12.0, 10.0, 11.0]
        })
        expected_sensors_head = pd.DataFrame({
            "count": 5 * [22917264],
            "streamType": 5 * [16],
            "tag": [86, 81, 80, 83, 85],
            "time": pd.to_datetime(5 * [1532220108], unit='s'),
            "values": [2176.0, 51612.0, 668.0, 26377.0, 1232.0]
        })
        expected_signals_head = pd.DataFrame({
            'count': 5 * [806132],
            'streamType': 5 * [2],
            'tag': [71, 13, 6, 66, 12],
            'time': pd.to_datetime(5 * [1532216905], unit='s'),
            'values': [0.0, 21.86422, 65.0, 1.5686275, 18.0],
            'quality': [np.nan, 100.0, 85.0, np.nan, 93.0]
        })

        timedelta = - pd.Timedelta('222 days, 15 hours, 51 minutes, 33 seconds')
        old_joined_data_time_col = self.reader.data.index.copy()
        self.reader.timeshift(timedelta)

        pd.testing.assert_frame_equal(self.reader.aggregates.head(), expected_aggregates_head)
        pd.testing.assert_frame_equal(self.reader.analytics_events.head(), expected_analytics_events_head)
        pd.testing.assert_frame_equal(self.reader.attributes_dailys.head(), expected_attributes_dailys_head)
        pd.testing.assert_frame_equal(self.reader.everion_events.head(), expected_everion_events_head)
        pd.testing.assert_frame_equal(self.reader.features.head(), expected_features_head)
        pd.testing.assert_frame_equal(self.reader.signals.head(), expected_signals_head)
        pd.testing.assert_frame_equal(self.reader.sensors.head(), expected_sensors_head)

        new_joined_data_time_col = self.reader.data.index.copy()
        pd.testing.assert_index_equal(old_joined_data_time_col + timedelta, new_joined_data_time_col)

    def test_random_timeshift(self):
        old_dataframes = [self.reader.aggregates.copy(),
                          self.reader.analytics_events.copy(),
                          self.reader.attributes_dailys.copy(),
                          self.reader.everion_events.copy(),
                          self.reader.features.copy(),
                          self.reader.signals.copy(),
                          self.reader.sensors.copy()]
        old_joined_data_time_col = self.reader.data.index.copy()
        self.reader.timeshift()
        new_dataframes = [self.reader.aggregates,
                          self.reader.analytics_events,
                          self.reader.attributes_dailys,
                          self.reader.everion_events,
                          self.reader.features,
                          self.reader.signals,
                          self.reader.sensors]

        for old_df, new_df in zip(old_dataframes, new_dataframes):
            old_time_col = old_df['time']
            new_time_col = new_df['time']
            one_month = pd.Timedelta('30 days')
            two_years = pd.Timedelta('730 days')

            #All time columns should be shifted at least one month and at most two years to the past.
            self.assertTrue(((old_time_col - two_years) < new_time_col).all())
            self.assertTrue((new_time_col < (old_time_col - one_month)).all())

        new_joined_data_time_col = self.reader.data.index
        self.assertTrue(((old_joined_data_time_col - two_years) < new_joined_data_time_col).all())
        self.assertTrue((new_joined_data_time_col < (old_joined_data_time_col - one_month)).all())

    def test_basic_write(self):
        old_dataframes = [self.reader.aggregates.copy(),
                          self.reader.analytics_events.copy(),
                          self.reader.attributes_dailys.copy(),
                          self.reader.everion_events.copy(),
                          self.reader.features.copy(),
                          self.reader.signals.copy(),
                          self.reader.sensors.copy(),
                          self.reader.data.copy()]
        self.reader.write(self.WRITE_PATH)
        reader = devicely.EverionReader(self.WRITE_PATH)
        new_dataframes = [reader.aggregates,
                          reader.analytics_events,
                          reader.attributes_dailys,
                          reader.everion_events,
                          reader.features,
                          reader.signals,
                          reader.sensors,
                          reader.data]

        for old_df, new_df in zip(old_dataframes, new_dataframes):
            pd.testing.assert_frame_equal(old_df, new_df)

        shutil.rmtree(self.WRITE_PATH)

    def _test_read_individual_dataframes(self, reader):
        expected_aggregates_head = pd.DataFrame({
            'count': 5 * [4468],
            'streamType': 5 * [5],
            'tag': [40, 18, 21, 7, 100],
            'time':  pd.to_datetime(5 * [1551454740], unit='s'),
            'values': [-2.0, 0.76, 21.0, 60.0, 0.0],
            'quality': [np.nan, 13.0, np.nan, 0.0, np.nan]
        })
        expected_analytics_events_head = pd.DataFrame({
            "count": [5622, 5621, 5620, 5619, 5618],
            "streamType": 5 * [7],
            "tag": 5 * [1],
            "time": pd.to_datetime(2 * [1551458609] + [1551458360, 1551458343, 1551458002], unit='s'),
            "values": [22.0, 2.0, 22.0, 22.0, 2.0]
        })
        expected_attributes_dailys_head = pd.DataFrame({
            "count": [14577, 14576, 14575, 14574, 14573],
            "streamType": 5 * [8],
            "tag": 5 * [67],
            "time": pd.to_datetime(5 * [1551458602], unit='s'),
            "values": [2.0, 4.0, 3.0, 11.0, 12.0],
            "quality": [15.0, 9.0, 8.0, 6.0, 5.0]
        })
        expected_everion_events_head = pd.DataFrame({
            "count": 5 * [46912],
            "streamType": 5 * [6],
            "tag": [128, 131, 129, 132, 126],
            "time": pd.to_datetime(5 * [1551458730], unit='s'),
            "values": [65295.0, 900.0, 44310.0, 4096.0, 0.0]
        })
        expected_features_head = pd.DataFrame({
            "count": [787000, 787001, 787002, 787003, 787004],
            "streamType": 5 * [4],
            "tag": 5 * [14],
            "time": pd.to_datetime([1551454784, 1551454784, 1551454785, 1551454786, 1551454787], unit='s'),
            "values": [950.0, 1085.0, 1074.0, 1021.0, 1056.0],
            "quality": [12.0, 11.0, 12.0, 10.0, 11.0]
        })
        expected_sensors_head = pd.DataFrame({
            "count": 5 * [22917264],
            "streamType": 5 * [16],
            "tag": [86, 81, 80, 83, 85],
            "time": pd.to_datetime(5 * [1551458001], unit='s'),
            "values": [2176.0, 51612.0, 668.0, 26377.0, 1232.0]
        })
        expected_signals_head = pd.DataFrame({
            'count': 5 * [806132],
            'streamType': 5 * [2],
            'tag': [71, 13, 6, 66, 12],
            'time': pd.to_datetime(5 * [1551454798], unit='s'),
            'values': [0.0, 21.86422, 65.0, 1.5686275, 18.0],
            'quality': [np.nan, 100.0, 85.0, np.nan, 93.0]
        })

        pd.testing.assert_frame_equal(reader.aggregates.head(), expected_aggregates_head)
        pd.testing.assert_frame_equal(reader.analytics_events.head(), expected_analytics_events_head)
        pd.testing.assert_frame_equal(reader.attributes_dailys.head(), expected_attributes_dailys_head)
        pd.testing.assert_frame_equal(reader.everion_events.head(), expected_everion_events_head)
        pd.testing.assert_frame_equal(reader.features.head(), expected_features_head)
        pd.testing.assert_frame_equal(reader.signals.head(), expected_signals_head)
        pd.testing.assert_frame_equal(reader.sensors.head(), expected_sensors_head)

if __name__ == '__main__':
    unittest.main()
