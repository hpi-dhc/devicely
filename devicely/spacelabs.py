import pandas as pd
import datetime as dt
import xmltodict
from .helpers import recursive_ordered_dict_to_dict

class SpacelabsReader:
    def __init__(self, path, timeshift=0):
        # Metadata Definition
        metadata = pd.read_csv(path, nrows=3, header=None)
        self.subject = metadata.loc[0, 0]
        base_date = dt.datetime.strptime(metadata.loc[2, 0], '%d.%m.%Y')

        column_names = ['hour','minutes','SYS(mmHg)','DIA(mmHg)','x','y','error','z','stress_test']
        self.data = pd.read_csv(path, sep=',', skiprows=51, skipfooter=1, header=None,
                                names=column_names,
                                parse_dates={'time': ['hour', 'minutes']},
                                date_parser=lambda hours, minutes: dt.time(hour=int(hours), minute=int(minutes)),
                                engine='python')

        # Droping NAs and Errors
        self.data.dropna(subset=['DIA(mmHg)', 'SYS(mmHg)', 'x'], inplace=True)
        self.data = self.data[self.data['error'] != 'EB']

        # Adjusting Date
        dates = [base_date]
        current_date = base_date
        for i in range(1, len(self.data)):
            previous_row = self.data.iloc[i - 1]
            current_row = self.data.iloc[i]
            if previous_row.time > current_row.time:
                current_date += dt.timedelta(days=1)
            dates.append(current_date)

        self.data.reset_index(inplace=True)
        self.data['timestamp'] = [dt.datetime.combine(dates[i], self.data.time[i]) for i in range(len(dates))]
        self.data.drop(columns=['time'], inplace=True)

        order = ['timestamp','SYS(mmHg)','DIA(mmHg)','x','y','z','error','stress_test']
        self.data = self.data[order]
        self.data.set_index('timestamp', inplace=True, verify_integrity=True)

        xml_line = open(path, 'r').readlines()[-1]
        xml_dict = recursive_ordered_dict_to_dict(xmltodict.parse(xml_line))
        self.metadata = xml_dict['XML']

    def set_window(self, window_size, type):
        if (type == 'bffill'):
            self.data['window_start'] = self.data.index - window_size // 2
            self.data['window_end'] = self.data.index + window_size // 2
        elif (type == 'bfill'):
            self.data['window_start'] = self.data.index - window_size
            self.data['window_end'] = self.data.index
