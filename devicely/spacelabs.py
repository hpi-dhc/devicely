import pandas as pd
import datetime as dt
import xmltodict
import random
from .helpers import recursive_ordered_dict_to_dict

class SpacelabsReader:
    def __init__(self, path):
        # Metadata Definition
        metadata = pd.read_csv(path, nrows=3, header=None)
        self.subject = metadata.loc[0, 0]
        base_date = dt.datetime.strptime(metadata.loc[2, 0], '%d.%m.%Y').date()

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
        self.data['date'] = dates

        order = ['date', 'time', 'timestamp', 'SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'z', 'error', 'stress_test']
        self.data = self.data[order]
        self.data.set_index('timestamp', inplace=True, verify_integrity=True)
        numeric_columns = ['SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'z', 'error', 'stress_test']
        self.data[numeric_columns] = self.data[numeric_columns].astype('float')

        xml_line = open(path, 'r').readlines()[-1]
        xml_dict = recursive_ordered_dict_to_dict(xmltodict.parse(xml_line))
        self.metadata = xml_dict['XML']

    def write(self, path):
        with open(path, 'w') as f:
            f.write(f"\n{self.subject}")
            f.write(8 * '\n')
            f.write("0")
            f.write(8 * '\n')
            f.write(self.data.index[0].date().strftime("%d.%m.%Y"))
            f.write(7 * '\n')
            f.write("Unknown Line")
            f.write(26 * '\n')
            f.write(str(len(self.data)) + "\n")
            adjusted_df = self.data.drop(columns=['date', 'time'])
            adjusted_df['hours'] = self.data.time.map(lambda x: x.hour)
            adjusted_df['minutes'] = self.data.time.map(lambda x: x.minute)
            order = ['hours','minutes','SYS(mmHg)','DIA(mmHg)','x','y','error','z']
            adjusted_df = adjusted_df[order]
            adjusted_df.to_csv(f, header=None, index=None)
            f.write(xmltodict.unparse({'XML': self.metadata}).split('\n')[1])
            f.write('\n')

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = pd.Timedelta(random.uniform(one_month, two_years))
            self.data.index -= random_timedelta
        if isinstance(shift, pd.Timestamp):
            timedeltas = self.data.index - self.data.index[0]
            shifted_index = shift + timedeltas
            self.data.index = shifted_index
        if isinstance(shift, pd.Timedelta):
            self.data.index += shift
        self.data.date = self.data.index.map(lambda timestamp: timestamp.date())
        self.data.time = self.data.index.map(lambda timestamp: timestamp.time())

    def set_window(self, window_size, type):
        if (type == 'bffill'):
            self.data['window_start'] = self.data.index - window_size // 2
            self.data['window_end'] = self.data.index + window_size // 2
        elif (type == 'bfill'):
            self.data['window_start'] = self.data.index - window_size
            self.data['window_end'] = self.data.index
