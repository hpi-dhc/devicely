import operator
import os
import pandas as pd
from collections import OrderedDict

def create_df(signal_names, signals, sample_freqs, start_timestamps):
    base_freq_key = max(sample_freqs.items(), key=operator.itemgetter(1))[0]
    max_freq = sample_freqs[base_freq_key]
    min_start_timestamp = start_timestamps[base_freq_key]
    data_frame = pd.DataFrame(index=pd.date_range(start=pd.to_datetime(min_start_timestamp, unit='s'),
                                                  periods=len(signals[base_freq_key]),
                                                  freq='{}N'.format(int(1e9 / max_freq))))
    for signal in signal_names:
        date_index = pd.date_range(start=pd.to_datetime(start_timestamps[signal], unit='s'),
                                   periods=len(signals[signal]),
                                   freq='{}N'.format(int(1e9 / sample_freqs[signal])))
        signal_data_frame = pd.DataFrame(data=signals[signal],
                                         index=date_index,
                                         columns=[signal])
        data_frame = data_frame.join(signal_data_frame, how='outer', sort=True)
    return data_frame

def recursive_ordered_dict_to_dict(ordered_dict):
        if isinstance(ordered_dict, OrderedDict):
            ordered_dict = dict(ordered_dict)
            for k, v in ordered_dict.items():
                ordered_dict[k] = recursive_ordered_dict_to_dict(v)
        return ordered_dict

def file_empty_or_not_existing(path):
    return not os.path.isfile(path) or os.stat(path).st_size == 0