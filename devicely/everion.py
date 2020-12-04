import os
import glob
import time

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
        data_signals = self.read_file(self.filelist['signals'], self.selected_signal_tags, self.SIGNAL_TAGS)

        if feature_tags is not None:
            self.selected_feature_tags = feature_tags
        data_features = self.read_file(self.filelist['features'], self.selected_feature_tags, self.FEATURE_TAGS)
        data_features.rename(columns={'inter_pulse_interval_quality': 'inter_pulse_interval_deviation'})

        # Raw data is contained in the the sensor file
        if 'sensors' in self.filelist:
            if sensor_tags is not None:
                self.selected_sensor_tags = sensor_tags
            data_sensors = self.read_file(self.filelist['sensors'], self.selected_sensor_tags, self.SENSOR_TAGS)
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

    def _split_values_column(df, tag_name):
        try:
            df[tag_name] = df['values'].astype(float)
        except ValueError:
            df[[tag_name, f"{tag_name}_quality"]] = df['values'].str.split(';', expand=True).astype(float)
        df.drop(columns=['values'], inplace=True)
        return df

    def read_file(self, path, selected_tags, tag_names):
        raw_signals = pd.read_csv(path)
        raw_signals = raw_signals.drop_duplicates()
        raw_signals = raw_signals[raw_signals['tag'].isin(selected_tags)]

        timestamps_min_and_count = raw_signals.groupby('time').agg(
            count_min=pd.NamedAgg(column='count', aggfunc='min'),
            count_range=pd.NamedAgg(column='count', aggfunc=lambda series: series.max() - series.min() + 1),
        )
        raw_signals = raw_signals.merge(timestamps_min_and_count.reset_index(), on='time')
        raw_signals['time'] += (raw_signals['count'] - raw_signals['count_min']) / raw_signals['count_range']
        raw_signals['time'] = pd.to_datetime(raw_signals['time'], unit='s')

        data = pd.DataFrame()
        for tag, group_df in raw_signals.groupby('tag'):
            tag_name = tag_names[tag]
            sub_df = EverionReader._split_values_column(group_df, tag_name)
            if sub_df.empty or (sub_df[tag_name] == 0).all():
                continue
            sub_df = sub_df.set_index('time', verify_integrity=True)
            sub_df = sub_df.sort_index()
            data = data.join(sub_df[tag_name], how='outer')

        return data