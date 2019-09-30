import pandas as pd
import numpy as np

class SpacelabsReader:

    def __init__(self, path, timeshift=0):
        # Metadata Definition
        metadata = pd.read_csv(path, nrows=3, header=None, names=['info'])
        metadata = metadata.loc[metadata['info'] != '0']
        subject = metadata.loc[[0]]['info'].item()
        date = metadata.iloc[[1]]['info'].item()

        # Column Names
        names = ['hour','minutes','SYS(mmHg)','DIA(mmHg)','x','y','error','z','biking_timepoint']

        # Reading File
        self.data = pd.read_csv(path, sep=',', skiprows=51, skipfooter=1, header=None,
                                names=names,
                                parse_dates={'time' : ['hour', 'minutes']},
                                date_parser = lambda x: pd.to_datetime(x, format='%H %M'), engine='python')

        # Droping NAs and Errors
        self.data.dropna(subset=['DIA(mmHg)', 'SYS(mmHg)', 'x'], inplace=True)
        self.data = self.data[self.data['error'] != 'EB']

        # Adding Date and Subject
        self.data['date'] = date
        self.data['subject'] = subject

        # Adjusting Timestamp
        self.data['time'] = pd.to_datetime(self.data['time'], format='%H %M').dt.time
        self.data['date'] = pd.to_datetime(self.data['date'], format='%d.%m.%Y').dt.date
        self.data['datetime'] = self.data.apply(lambda x : pd.datetime.combine(x['date'], x['time']),1)

        # Adjusting Date
        count = 0
        new = {}
        previous = '23'
        for n, row in self.data.iterrows():
            if (str(row['time']) >= '00:00:00' and str(row['time']) <= '00:59:59' and previous != '00'):
                count += 1
            previous = str(row['time'])[2:]
            new[row.name] = count

        days = pd.DataFrame.from_dict(new, orient='index', columns=['days'])

        # Updating timestamp
        days = pd.DataFrame.from_dict(new, orient='index', columns=['days'])
        self.data = pd.concat([self.data, days], axis=1, sort=False, join='inner')
        diff = self.data['days'].apply(np.ceil).apply(lambda x: pd.Timedelta(x, unit='D'))
        self.data['datetime'] = self.data['datetime'] + diff
        self.data['date'] = self.data['datetime'].dt.date
        self.data.drop(['days'], axis=1, inplace=True)

        order = ['datetime','date','time','subject','SYS(mmHg)','DIA(mmHg)','x','y','z','error','biking_timepoint']

        self.data = self.data[order]
        self.data.set_index('datetime', inplace=True, verify_integrity=True)
        self.data.index = self.data.index.shift(periods=-timeshift, freq='1H')

    def set_window(self, window_size):
        self.data['window_start'] = self.data.index - window_size // 2
        self.data['window_end'] = self.data.index + window_size // 2
