import pandas as pd
import datetime as dt
import xmltodict
import random
from .helpers import recursive_ordered_dict_to_dict
import csv


class SpacelabsReader:
    def __init__(self, path):
        # Metadata Definition
        metadata = pd.read_csv(path, nrows=3, header=None)
        self.subject = str(metadata.loc[0, 0])
        base_date = dt.datetime.strptime(metadata.loc[2, 0], '%d.%m.%Y').date()

        column_names = ['hour', 'minutes', 'SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'error', 'z']
        self.data = pd.read_csv(path, sep=',', skiprows=51, skipfooter=1, header=None,
                                names=column_names,
                                parse_dates={'time': ['hour', 'minutes']},
                                date_parser=lambda hours, minutes: dt.time(hour=int(hours), minute=int(minutes)),
                                engine='python')

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
        self.data.set_index('timestamp', inplace=True)
        self.data['date'] = dates

        order = ['date', 'time', 'SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'z', 'error']
        self.data = self.data[order]

        xml_line = open(path, 'r').readlines()[-1]
        xml_dict = recursive_ordered_dict_to_dict(xmltodict.parse(xml_line))
        self.metadata = xml_dict['XML']

    def write(self, path):
        with open(path, 'w') as f:
            f.write(f"\n{self.subject}")
            f.write(8 * '\n')
            f.write("0")
            f.write(8 * '\n')
            f.write(self.data.date[0].strftime("%d.%m.%Y"))
            f.write(7 * '\n')
            f.write("Unknown Line")
            f.write(26 * '\n')
            f.write(str(len(self.data)) + "\n")
            printing_df = self.data.drop(columns=['date', 'time'])
            printing_df['hours'] = self.data.time.map(lambda x: x.strftime("%H"))
            printing_df['minutes'] = self.data.time.map(lambda x: x.strftime("%M"))
            order = ['hours', 'minutes', 'SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'error', 'z']
            printing_df = printing_df[order]
            printing_df.fillna(-9999, inplace=True)
            printing_df.replace('EB', -9998, inplace=True)
            printing_df[['SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'error', 'z']] = printing_df[
                ['SYS(mmHg)', 'DIA(mmHg)', 'x', 'y', 'error', 'z']].astype(int).astype(str)
            printing_df.replace('-9999', '""', inplace=True)
            printing_df.replace('-9998', '"EB"', inplace=True)
            printing_df.to_csv(f, header=None, index=None, quoting=csv.QUOTE_NONE)
            f.write(xmltodict.unparse({'XML': self.metadata}).split('\n')[1])

    def timeshift(self, shift='random'):
        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = pd.Timedelta(random.uniform(one_month, two_years)).round('min')
            self.data.index -= random_timedelta
        if isinstance(shift, pd.Timestamp):
            timedeltas = self.data.index - self.data.index[0]
            self.data.index = shift.round('min') + timedeltas
        if isinstance(shift, pd.Timedelta):
            self.data.index += shift.round('min')
        self.data.date = self.data.index.map(lambda timestamp: timestamp.date())
        self.data.time = self.data.index.map(lambda timestamp: timestamp.time())

    def set_window(self, window_size, type):
        if (type == 'bffill'):
            self.data['window_start'] = self.data.index - window_size // 2
            self.data['window_end'] = self.data.index + window_size // 2
        elif (type == 'bfill'):
            self.data['window_start'] = self.data.index - window_size
            self.data['window_end'] = self.data.index
