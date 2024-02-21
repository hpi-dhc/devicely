"""
Spacelabs (SL 90217) is an oscillometric blood pressure (BP) monitor which can be used to
automatically track a person's BP in specificed time intervals.

"""
import csv
import datetime as dt
import random
from xml.etree import ElementTree as ET

import pandas as pd

from ._compat import _to_csv_line_terminator


class SpacelabsReader:
    """
    Read, timeshift, deidentify and write data
    generated by Spacelabs(SL90217).

    Attributes
    ----------
    data : DataFrame
        DataFrame with the values that were read from the abp file.

    subject : str
        Contain the sujbect's id. Can be changed for
        deidentification.

    valid_measurements : str
        Contain the number of valid measurements in the
        abp file.

    metadata : dict
        The measurements' metadata. Read from the xml at the bottom
        of the abp file. Can be erased for deidentification.
    """

    def __init__(self, path):
        """
        Reads the abp file generated by the Spacelabs device and saves the
        parsed DataFrame.

        Parameters
        ----------
        path : str
            Path of the abp file.
        """

        # Metadata Definition
        metadata = pd.read_csv(path, nrows=5, header=None)
        self.subject = str(metadata.loc[0, 0])
        base_date = dt.datetime.strptime(metadata.loc[2, 0], '%d.%m.%Y').date()
        if metadata.loc[4, 0] != 'Unknown Line':
            self.valid_measurements = str(metadata.loc[4, 0])
        else:
            metadata = pd.read_csv(path, nrows=6, header=None)
            self.valid_measurements = str(metadata.loc[5, 0])

        column_names = ['hour', 'minutes', 'SYS(mmHg)', 'DIA(mmHg)', 'UNKNOW_1', 'UNKNOW_2', 'CODE', 'UNKNOW_3']
        self.data = pd.read_csv(path, sep=',', skiprows=51, skipfooter=1, header=None, names=column_names, engine='python')

        # Adjusting Date
        dates = [base_date]
        times = [dt.time(hour=self.data.loc[i, 'hour'], minute=self.data.loc[i, 'minutes']) for i in range(len(self.data))]
        current_date = base_date
        for i in range(1, len(times)):
            if times[i] < times[i-1]:
                current_date += dt.timedelta(days=1)
            dates.append(current_date)

        self.data.reset_index(inplace=True)
        self.data['timestamp'] = pd.to_datetime([dt.datetime.combine(dates[i], times[i]) for i in range(len(dates))])
        self.data['date'] = dates
        self.data['time'] = times

        order = ['timestamp', 'date', 'time', 'SYS(mmHg)', 'DIA(mmHg)', 'UNKNOW_1', 'UNKNOW_2', 'UNKNOW_3', 'CODE']
        self.data = self.data[order]

        try:
            self.data.set_index('timestamp', inplace=True)
        except KeyError:
            print('Timestamp can not be set as an index:')
            print(KeyError)

        xml_line = open(path, 'r').readlines()[-1]
        xml_root = ET.fromstring(xml_line)
        self.metadata = self._etree_to_dict(xml_root)['XML']


    def deidentify(self, subject_id=None):
        """
        Deidentify the data by removing the original XML metadata and
        subject id.

        Parameters
        ----------
        subject_id : str, optional
            New subject id to be written in the
            deidentified file, by default None.
        """
        # Changing subject id
        if subject_id:
            self.subject = subject_id
        else:
            self.subject = ''

        self.metadata = {
            'PATIENTINFO' : {'DOB' : '',
                             'RACE' : ''},
            'REPORTINFO' : {'PHYSICIAN' : '',
                            'NURSETECH' : '',
                            'STATUS' : '',
                            'CALIPERSUMMARY' : {'COUNT' : ''}}
        }

    def write(self, path):
        """
        Write the signals and metadata to the
        writing path in the same format as it was read.

        Parameters
        ----------
        path : str
            Path to writing file. Writing mode: 'w'.
            Use the file extension 'abp' to keep the SpaceLabs standard.
        """

        with open(path, 'w') as file:
            file.write(f"\n{self.subject}")
            file.write(8 * '\n')
            file.write("0")
            file.write(8 * '\n')
            file.write(self.data.date[0].strftime("%d.%m.%Y"))
            file.write(7 * '\n')
            file.write("Unknown Line")
            file.write(26 * '\n')
            file.write(self.valid_measurements + "\n")
            printing_df = self.data.drop(columns=['date', 'time'])
            printing_df['hours'] = self.data.time.map(lambda x: x.strftime("%H"))
            printing_df['minutes'] = self.data.time.map(lambda x: x.strftime("%M"))
            order = ['hours', 'minutes', 'SYS(mmHg)', 'DIA(mmHg)', 'UNKNOW_1', 'UNKNOW_2', 'CODE', 'UNKNOW_3']
            printing_df = printing_df[order]
            printing_df.fillna(-9999, inplace=True)
            printing_df.replace('EB', -9998, inplace=True)
            printing_df.replace('AB', -9997, inplace=True)
            printing_df[['SYS(mmHg)', 'DIA(mmHg)', 'UNKNOW_1', 'UNKNOW_2', 'CODE', 'UNKNOW_3']] = printing_df[
                ['SYS(mmHg)', 'DIA(mmHg)', 'UNKNOW_1', 'UNKNOW_2', 'CODE', 'UNKNOW_3']].astype(int).astype(str)
            printing_df.replace('-9999', '""', inplace=True)
            printing_df.replace('-9998', '"EB"', inplace=True)
            printing_df.replace('-9997', '"AB"', inplace=True)
            printing_df.to_csv(file, header=None, index=None, quoting=csv.QUOTE_NONE,
                               **{_to_csv_line_terminator: '\n'})

            xml_node = ET.Element('XML')
            xml_node.extend(self._dict_to_etree(self.metadata))
            xml_line = ET.tostring(xml_node, encoding="unicode")
            file.write(xml_line)

    def _etree_to_dict(self, etree_node):
        children = list(iter(etree_node))
        if len(children) == 0:
            return {etree_node.tag: etree_node.text}
        else:
            dict_ = dict()
            for child in children:
                dict_ = {**dict_, **self._etree_to_dict(child)}
            return {etree_node.tag: dict_}

    def _dict_to_etree(self, dict_):
        def rec(key, value):
            node = ET.Element(key)
            if isinstance(value, dict):
                for child_key in value:
                    node.append(rec(child_key, value[child_key]))
            else:
                node.text = str(value) if value else ''
            return node

        return [rec(k, v) for k, v in dict_.items()]

    def timeshift(self, shift='random'):
        """
        Timeshift the data by shifting all time related columns.

        Parameters
        ----------
        shift : None/'random', pd.Timestamp or pd.Timedelta
            If shift is not specified, shifts the data by a random time interval
            between one month and two years to the past.

            If shift is a timdelta, shifts the data by that timedelta.

            If shift is a timestamp, shifts the data such that the earliest entry
            has that timestamp. The remaining values will mantain the same
            time difference to the first entry.
        """

        if shift == 'random':
            one_month = pd.Timedelta('30 days').value
            two_years = pd.Timedelta('730 days').value
            random_timedelta = - pd.Timedelta(random.uniform(one_month, two_years)).round('min')
            self.timeshift(random_timedelta)

        if not self.data.index.empty:
            if isinstance(shift, pd.Timestamp):
                timedeltas = self.data.index - self.data.index[0]
                self.data.index = shift.round('min') + timedeltas
            if isinstance(shift, pd.Timedelta):
                self.data.index += shift.round('min')
            self.data['date'] = self.data.index.map(lambda timestamp: timestamp.date())
            self.data['time'] = self.data.index.map(lambda timestamp: timestamp.time())
        else:
            if isinstance(shift, pd.Timestamp):
                timedeltas = self.data['timestamp'] - self.data['timestamp'].min()
                self.data['timestamp'] = shift.round('min') + timedeltas
            if isinstance(shift, pd.Timedelta):
                self.data['timestamp'] += shift.round('min')
            self.data['date'] = self.data['timestamp'].map(lambda timestamp: timestamp.date())
            self.data['time'] = self.data['timestamp'].map(lambda timestamp: timestamp.time())
