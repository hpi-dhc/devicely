import os
import glob
import numpy as np
import pandas as pd

class EverionReader:

    SIGNAL_TAGS = {
        6: 'heart_rate',
        7: 'oxygen_saturation',
        8: 'perfusion_index',
        9: 'motion_activity',
        10: 'activity_classification',
        11: 'heart_rate_variability',
        12: 'respiration_rate',
        13: 'energy',
        15: 'ctemp',
        19: 'temperature_local',
        20: 'barometer_pressure',
        21: 'gsr_electrode',
        22: 'health_score',
        23: 'relax_stress_intensity_score',
        24: 'sleep_quality_index_score',
        25: 'training_effect_score',
        26: 'activity_score',
        66: 'richness_score',
        68: 'heart_rate_quality',
        69: 'oxygen_saturation_quality',
        70: 'blood_pulse_wave',
        71: 'number_of_steps',
        72: 'activity_classification_quality',
        73: 'energy_quality',
        74: 'heart_rate_variability_quality',
        75: 'respiration_rate_quality',
        76: 'ctemp_quality',
        118: 'temperature_object',
        119: 'temperature_barometer',
        133: 'perfusion_index_quality',
        134: 'blood_pulse_wave_quality'
    }

    SENSOR_TAGS = {
        80: 'led1_data',
        81: 'led2_data',
        82: 'led3_data',
        83: 'led4_data',
        84: 'accx_data',
        85: 'accy_data',
        86: 'accz_data',
        88: 'led2_current',
        89: 'led3_current',
        90: 'led4_current',
        91: 'current_offset',
        92: 'compressed_data'
    }

    FEATURE_TAGS = {
        14: 'inter_pulse_interval',
        17: 'pis',
        18: 'pid',
        77: 'inter_pulse_deviation',
        78: 'pis_quality',
        79: 'pid_quality'
    }

    selected_signal_tags = [6, 7, 11, 12, 15, 19, 20, 21, 118, 119]
    selected_sensor_tags = [80, 81, 82, 83, 84, 85, 86]
    selected_feature_tags = [14]

    ACC_NAMES = ['accx_data', 'accy_data', 'accz_data']

    def __init__(self, path, signal_tags=None, sensor_tags=None, feature_tags=None):
        self.init_filelist(path)

        if signal_tags is not None:
            self.selected_signal_tags = signal_tags
        data_signals = self.read_signals()

        if feature_tags is not None:
            self.selected_feature_tags = feature_tags
        data_features = self.read_features()

        # Raw data is contained in the the sensor file
        if 'sensors' in self.filelist:
            if sensor_tags is not None:
                self.selected_sensor_tags = sensor_tags
            data_sensors = self.read_sensors()

            data_all = data_signals.join([data_sensors, data_features], how='outer')
        else:
            data_all = data_signals.join([data_features], how='outer')

        if all(x in set(data_all.columns) for x in self.ACC_NAMES):
            data_all['acc_mag'] = np.linalg.norm(data_all[self.ACC_NAMES], axis='1')

        self.data = data_all


    def init_filelist(self, path):
        self.filelist = {
            'signals': glob.glob(path+r'/*signals*').pop(),
            'aggregates': glob.glob(path+r'/*aggregates*').pop(),
            'analytics': glob.glob(path+r'/*analytics_events*').pop(),
            'events': glob.glob(path+r'/*everion_events*').pop(),
            'features': glob.glob(path+r'/*features*').pop()
        }

        try:
            self.filelist['sensors'] = glob.glob(path+r'/*sensor*').pop()
            print('Reading processed and raw data.')
        except IndexError:
            print('No sensors file. Reading processed data only.')

    def read_signals(self):
        raw_signals = pd.read_csv(self.filelist['signals'])
        raw_signals = raw_signals.drop_duplicates()

        data = pd.DataFrame()
        for tag in np.sort(raw_signals['tag'].unique()):
            if tag not in self.selected_signal_tags:
                continue
            tag_name = self.SIGNAL_TAGS[tag]
            sub_df = raw_signals.loc[raw_signals['tag'] == tag].copy()
            columns_to_join = [tag_name]
            # Check if signal includes quality value
            sub_df_values = sub_df.loc[sub_df.first_valid_index(), 'values']
            if sub_df_values.find(';') != -1:
                quality_name = '{}_quality'.format(tag_name)
                columns_to_join = columns_to_join + [quality_name]
                sub_df.loc[:, quality_name] = sub_df['values'].apply(lambda val: val[val.find(';')+1:]).astype(float)
                sub_df.loc[:, tag_name] = sub_df['values'].apply(lambda val: val[:val.find(';')]).astype(float)
            else:
                sub_df.loc[:, tag_name] = sub_df['values'].astype(float)
            sub_df.loc[:, 'time'] = pd.to_datetime(sub_df.loc[:, 'time'], unit='s')
            if sub_df.empty or (sub_df[tag_name] == 0).all():
                continue
            sub_df = sub_df.set_index('time', verify_integrity=True)
            sub_df = sub_df.sort_index()
            data = data.join(sub_df[columns_to_join], how='outer')

        return data

    def read_sensors(self):
        raw_sensors = pd.read_csv(self.filelist['sensors'])
        raw_sensors = raw_sensors.drop_duplicates()

        min_count_dict = {}
        count_ts_dict = {}
        data = pd.DataFrame()
        sub_df = raw_sensors.loc[raw_sensors['tag'] == self.selected_sensor_tags[0]]
        for ts in raw_sensors['time'].unique():
            min_count_dict[ts] = sub_df.loc[sub_df['time'] == ts].loc[:, 'count'].min()
            count_ts_dict[ts] = sub_df.loc[sub_df['time'] == ts].loc[:, 'count'].max() - min_count_dict[ts] + 1
        for tag in np.sort(raw_sensors['tag'].unique()):
            if tag not in self.selected_sensor_tags:
                continue
            tag_name = self.SENSOR_TAGS[tag]
            sub_df = raw_sensors.loc[raw_sensors['tag'] == tag].copy()

            sub_df.loc[:, 'time'] = pd.to_datetime(sub_df.apply(lambda x: x['time'] + (x['count'] - min_count_dict[x['time']]) / count_ts_dict[x['time']], axis=1), unit='s')
            sub_df.loc[:, tag_name] = sub_df['values']
            if sub_df.empty or (sub_df[tag_name] == 0).all():
                continue
            sub_df = sub_df.set_index('time', verify_integrity=True)
            sub_df = sub_df.sort_index()
            data = data.join(sub_df[tag_name], how='outer')

        return data

    def read_features(self):
        raw_features = pd.read_csv(self.filelist['features'])
        raw_features = raw_features.drop_duplicates()

        min_count_dict = {}
        count_ts_dict = {}
        data = pd.DataFrame()
        sub_df = raw_features.loc[raw_features['tag'] == self.selected_feature_tags[0]]
        for ts in raw_features['time'].unique():
            min_count_dict[ts] = sub_df.loc[sub_df['time'] == ts].loc[:, 'count'].min()
            count_ts_dict[ts] = sub_df.loc[sub_df['time'] == ts].loc[:, 'count'].max() - min_count_dict[ts] + 1

        for tag in np.sort(raw_features['tag'].unique()):
            if tag not in self.selected_feature_tags:
                continue
            tag_name = self.FEATURE_TAGS[tag]
            sub_df = raw_features.loc[raw_features['tag'] == tag]

            columns_to_join = [tag_name]
            # Check if signal includes quality value
            sub_df_values = sub_df.loc[sub_df.first_valid_index(), 'values']
            if sub_df_values.find(';') != -1:
                if tag == 14: # inter pulse interval quality is given as deviation
                    quality_name = '{}_deviation'.format(tag_name)
                else:
                    quality_name = '{}_quality'.format(tag_name)
                columns_to_join = columns_to_join + [quality_name]
                sub_df.loc[:, quality_name] = sub_df['values'].apply(lambda val: val[val.find(';')+1:]).astype(float)
                sub_df.loc[:, tag_name] = sub_df['values'].apply(lambda val: val[:val.find(';')]).astype(float)
            else:
                sub_df.loc[:, tag_name] = sub_df['values'].astype(float)
            sub_df.loc[:, 'time'] = pd.to_datetime(sub_df.apply(lambda x: x['time'] + (x['count'] - min_count_dict[x['time']]) / count_ts_dict[x['time']], axis=1), unit='s')
            if sub_df.empty or (sub_df[tag_name] == 0).all():
                continue
            sub_df = sub_df.set_index('time', verify_integrity=True)
            sub_df = sub_df.sort_index()
            data = data.join(sub_df[columns_to_join], how='outer')

        return data