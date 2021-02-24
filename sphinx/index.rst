.. devicely documentation master file, created by
   sphinx-quickstart on Wed Nov 25 00:15:47 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============

The devicely package is made for reading, writing and anonymizing (timeshifting) health sensor data from

* `Empatica E4 (Firmware 2.1.0.4911) <https://e4.empatica.com/e4-wristband/>`_
* `Biovotion Everion (Firmware 03.06) <https://www.biovotion.com/everion/>`_
* `1-lead ECG monitor FarosTM 180 from Bittium (Firmware 3.5.1) <https://shop.bittium.com/product/36/bittium-faros-180-solution-pack/>`_
* `Spacelabs (SL 90217) <https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/>`_
* `Tags (obtained from the app: TimeStamp for Android Version 1.36) <https://play.google.com/store/apps/details?id=gj.timestamp&hl=en/>`_
* `Shimmer Consensys GSR (Shimmer3 GSR Development Kit) <https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab/>`_


Examples
========

Empatica
########

The Empatice E4 wristband can be used to obtain data for inter-beat intervals, electrodermal activity, heart rate, temperature and blood volume pulse.
The wristband outputs its measurements in `this directory structure <https://github.com/jostmorgenstern/devicely-documentation-sample-data/tree/main/Empatica/>`_.

Create an :code:`EmpaticaReader` object, passing as a parameter a path of the same directory structure:

.. code-block:: Python

   >>> import devicely
   >>> empatica_reader = devicely.EmpaticaReader('path/to/empatica/dir')

Accessing the individual signal dataframes

.. code-block:: Python

   >>> empatica_reader.ACC.head(3)
                              acc_x  acc_y  acc_z    acc_mag
   2020-10-16 17:04:29.000000     -3     11     60  61.073726
   2020-10-16 17:04:29.031250     -3     11     60  61.073726
   2020-10-16 17:04:29.062500     -2     11     60  61.032778

You can also access :code:`empatica_reader.IBI` (inter-beat intervals), :code:`empatica_reader.EDA` (electrodermal activity), :code:`empatica_reader.HR` (heart rate), :code:`empatica_reader.TEMP` (temperature) and :code:`empatica_reader.BVP` (blood volume pulse).

An EmpaticaReader object also contains a dataframe of all signals, joined by time of sampling. Because of varying sampling frequencies across signals, expect to see a lot of nan values.

.. code-block:: Python

   >>> empatica_reader.data.head(3)
                              bvp  eda  hr   temp  acc_x  acc_y  acc_z    acc_mag  timedelta  ibi
   2020-10-16 17:04:29.000000 -0.0  0.0 NaN  31.13   -3.0   11.0   60.0  61.073726        NaN  NaN
   2020-10-16 17:04:29.015625 -0.0  NaN NaN    NaN    NaN    NaN    NaN        NaN        NaN  NaN
   2020-10-16 17:04:29.031250 -0.0  NaN NaN    NaN   -3.0   11.0   60.0  61.073726        NaN  NaN

You can access the sampling frequency of each signal:

.. code-block:: Python

   >>> empatica_reader.sample_freqs
   {'bvp': 64.0, 'eda': 4.0, 'hr': 1.0, 'temp': 4.0, 'acc': 32.0}

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`EmpaticaReader.timeshift()`.

.. code-block:: Python

   >>> empatica_reader.start_times
   {'bvp': Timestamp('2020-10-16 17:04:29'),
    'eda': Timestamp('2020-10-16 17:04:29'),
    'hr': Timestamp('2020-10-16 17:04:39'),
    'temp': Timestamp('2020-10-16 17:04:29'),
    'acc': Timestamp('2020-10-16 17:04:29'),
    'ibi': Timestamp('2020-10-16 17:04:29')}

   >>> empatica_reader.timeshift()

   >>> empatica_reader.start_times
   {'bvp': Timestamp('2020-03-07 03:02:16.693659368'),
   'eda': Timestamp('2020-03-07 03:02:16.693659368'),
   'hr': Timestamp('2020-03-07 03:02:26.693659368'),
   'temp': Timestamp('2020-03-07 03:02:16.693659368'),
   'acc': Timestamp('2020-03-07 03:02:16.693659368'),
   'ibi': Timestamp('2020-03-07 03:02:16.693659368')}
   

Write the data back to csv files. The written data keeps the format of the original data, so you can use an :code:`EmpaticaReader` to read your written data.

.. code-block:: Python

   >>> empatica_reader.write('write_path')
   >>> os.listdir('write_path')
   ['HR.csv', 'BVP.csv', 'TEMP.csv', 'EDA.csv', 'tags.csv', 'ACC.csv', 'IBI.csv']


SpaceLabs
#########

Look `here <https://github.com/jostmorgenstern/devicely-documentation-sample-data/blob/main/Spacelabs/spacelabs.abp/>`_ for an example file created by the Spacelabs ABPM monitoring system.

Creating a :code:`SpacelabsReader` object, passing such a file as a parameter:

.. code-block:: Python

   >>> spacelabs_reader = devicely.SpacelabsReader('path/to/spacelabsfile.abp')

Accessing the data:

.. code-block:: Python

   >>> spacelabs_reader.metadata
   {'PATIENTINFO': {'DOB': None, 'RACE': None},
   'REPORTINFO': {'PHYSICIAN': None, 
                  'NURSETECH': 'admin', 
                  'STATUS': 'NOTCONFIRMED', 
                  'CALIPERSUMMARY': {'COUNT': '0'}}}
   >>> spacelabs_reader.subject 
   '005F3'
   >>> spacelabs_reader.data.head(6)
               timestamp        date      time  SYS(mmHg)  DIA(mmHg)     x     y   z error
   0 2019-03-01 16:18:00  2019-03-01  16:18:00        107         76  78.0  78.0 NaN   NaN
   1 2019-03-01 16:19:00  2019-03-01  16:19:00         96         62  63.0  63.0 NaN   NaN
   2 2019-03-01 16:22:00  2019-03-01  16:22:00        100         68  64.0  64.0 NaN   NaN
   3 2019-03-01 16:23:00  2019-03-01  16:23:00        103         68  68.0  68.0 NaN   NaN
   4 2019-03-01 16:25:00  2019-03-01  16:25:00        101         67  65.0  65.0 NaN   NaN
   5 2019-03-01 16:31:00  2019-03-01  16:31:00         11          0   0.0   0.0 NaN    EB

EB-errors can be dropped using :code:`drop_EB`.

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`SpaceLabsReader.timeshift()`.

.. code-block:: Python

   >>> spacelabs_reader.data.head(3)
                              date      time  SYS(mmHg)  DIA(mmHg)     x     y   z error
   timestamp                                                                            
   2019-03-01 16:18:00  2019-03-01  16:18:00        107         76  78.0  78.0 NaN   NaN
   2019-03-01 16:19:00  2019-03-01  16:19:00         96         62  63.0  63.0 NaN   NaN
   2019-03-01 16:22:00  2019-03-01  16:22:00        100         68  64.0  64.0 NaN   NaN

   >>> spacelabs_reader.timeshift()

   >>> spacelabs_reader.data.head(3)
                              date      time  SYS(mmHg)  DIA(mmHg)     x     y   z error
   timestamp                                                                            
   2017-12-17 11:12:00  2017-12-17  11:12:00        107         76  78.0  78.0 NaN   NaN
   2017-12-17 11:13:00  2017-12-17  11:13:00         96         62  63.0  63.0 NaN   NaN
   2017-12-17 11:16:00  2017-12-17  11:16:00        100         68  64.0  64.0 NaN   NaN

Write the data back to disk. The written data keeps the same format as the original file, so you can use a SpacelabsReader to read it again.

.. code-block:: Python

   >>> spacelabs_reader.write('spacelabs_write_file.abp')
   >>> 'spacelabs_write_file.abp' in os.listdir()
   True

Everion
#########

Look `here <https://github.com/jostmorgenstern/devicely-documentation-sample-data/tree/main/Everion/>`_ for an example directory.
To read this data, create an :code:`EverionReader` object with such a path. Feel free to remove files you are not interested in from the directory before reading.

.. code-block:: Python

   >>> import devicely
   >>> reader = devicely.EverionReader("/home/jost/DHC/sample_data/devicely_documentation_sample_data/Everion")
   >>> reader.data.head()
                                 heart_rate  heart_rate_quality  oxygen_saturation  oxygen_saturation_quality  ...  accx_data  accy_data  accz_data      acc_mag
   time                                                                                                         ...                                              
   2019-03-01 13:23:05.000000000         NaN                 NaN                NaN                        NaN  ...      368.0     2096.0    -3536.0  4126.976617
   2019-03-01 13:23:05.019607808         NaN                 NaN                NaN                        NaN  ...      256.0     2016.0    -3808.0  4316.324362
   2019-03-01 13:23:05.039215872         NaN                 NaN                NaN                        NaN  ...      144.0     2288.0    -3728.0  4376.489918
   2019-03-01 13:23:05.058823680         NaN                 NaN                NaN                        NaN  ...       96.0     2352.0    -3600.0  4301.292829
   2019-03-01 13:23:05.078431488         NaN                 NaN                NaN                        NaN  ...        0.0     2384.0    -3904.0  4574.349353

You can access all different tags via :code:`EverionReader.SIGNAL_TAGS`, :code:`EverionReader.SENSOR_TAGS` and :code:`EverionReader.FEATURE_TAGS`.
By default, the tags :code:`EverionReader.default_signal_tags`, :code:`EverionReader.default_sensor_tags` and :code:`EverionReader.default_feature_tags` are used but you can provide custom tags while creating the reader.

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`EverionReader.timeshift()`.

.. code-block:: Python

   >>> reader.timeshift()
   >>> reader.data.head()
                                 heart_rate  heart_rate_quality  oxygen_saturation  oxygen_saturation_quality  ...  accx_data  accy_data  accz_data      acc_mag
   time                                                                                                         ...                                              
   2017-03-14 11:00:54.000000000         NaN                 NaN                NaN                        NaN  ...      368.0     2096.0    -3536.0  4126.976617
   2017-03-14 11:00:54.019607808         NaN                 NaN                NaN                        NaN  ...      256.0     2016.0    -3808.0  4316.324362
   2017-03-14 11:00:54.039215872         NaN                 NaN                NaN                        NaN  ...      144.0     2288.0    -3728.0  4376.489918
   2017-03-14 11:00:54.058823680         NaN                 NaN                NaN                        NaN  ...       96.0     2352.0    -3600.0  4301.292829
   2017-03-14 11:00:54.078431488         NaN                 NaN                NaN                        NaN  ...        0.0     2384.0    -3904.0  4574.349353

Write the data back, maintaing the original directory structure:

.. code-block:: Python

   >>> reader.write('write_path')
   >>> os.listdir('write_path')
   ['features.csv', 'everion_events.csv', 'attributes_dailys.csv', 'analytics_events.csv', 'sensor_data.csv', 'aggregates.csv', 'signals.csv']


Faros
#####

The `Faros ECG monitor <https://shop.bittium.com/product/36/bittium-faros-180-solution-pack/>`_ creates data in the EDF file format. See `this file <https://github.com/jostmorgenstern/devicely-documentation-sample-data/blob/main/Faros/faros.EDF/>`_ for an example.

Create a :code:`FarosReader` object:

.. code-block:: Python

   >>> reader = devicely.FarosReader("path/to/faros.EDF")
   >>> reader.start_time
   Timestamp('2019-03-01 16:12:43')
   >>> reader.sample_freqs
   {'ECG': <DateOffset: seconds=0.001>, 'Accelerometer_X': <DateOffset: seconds=0.01>, 'Accelerometer_Y': <DateOffset: seconds=0.01>, 'Accelerometer_Z': <DateOffset: seconds=0.01>, 'Marker': <DateOffset: seconds=1.0>, 'HRV': <DateOffset: seconds=0.2>, 'acc_mag': <DateOffset: seconds=0.01>}
   >>> reader.data.head()
                           ECG  Accelerometer_X  Accelerometer_Y  Accelerometer_Z  Marker  HRV     acc_mag
   time                                                                                                     
   2019-03-01 16:12:43.000  26.0            164.0             23.0          -1172.0     0.0  0.0  1183.64226
   2019-03-01 16:12:43.001  -6.0              NaN              NaN              NaN     NaN  NaN         NaN
   2019-03-01 16:12:43.002 -31.0              NaN              NaN              NaN     NaN  NaN         NaN
   2019-03-01 16:12:43.003 -39.0              NaN              NaN              NaN     NaN  NaN         NaN
   2019-03-01 16:12:43.004 -17.0              NaN              NaN              NaN     NaN  NaN         NaN

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`FarosReader.timeshift()`.

.. code-block:: Python

   >>> reader.timeshift()
   >>> reader.start_time
   Timestamp('2017-11-01 08:52:44')
   >>> reader.data.head()
                           ECG  Accelerometer_X  Accelerometer_Y  Accelerometer_Z  Marker  HRV     acc_mag
   time                                                                                                     
   2017-11-01 08:52:44.000  26.0            164.0             23.0          -1172.0     0.0  0.0  1183.64226
   2017-11-01 08:52:44.001  -6.0              NaN              NaN              NaN     NaN  NaN         NaN
   2017-11-01 08:52:44.002 -31.0              NaN              NaN              NaN     NaN  NaN         NaN
   2017-11-01 08:52:44.003 -39.0              NaN              NaN              NaN     NaN  NaN         NaN
   2017-11-01 08:52:44.004 -17.0              NaN              NaN              NaN     NaN  NaN         NaN

Write the data to csv. You can read the written data using a :code:`FarosReader`.

.. code-block:: Python

   >>> reader.write("write_path.csv")
   >>> "write_path.csv" in os.listdir()
   True


Shimmer
#######

The `Shimmer Consensys GSR (Shimmer3 GSR Development Kit) <https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab/>`_ uses a :code:`csv` format as seen `here <https://github.com/jostmorgenstern/devicely-documentation-sample-data/blob/main/Shimmer/shimmer.csv/>`_

To create a :code:`ShimmerPlusReader`, simply pass the path to the csv file:

.. code-block:: Python

   >>> reader = devicely.ShimmerPlusReader("path/to/shimmer.csv")
   >>> reader.data.head()
                           Shimmer_40AC_Accel_LN_X_CAL  Shimmer_40AC_Accel_LN_Y_CAL  ...  Shimmer_40AC_Temperature_BMP280_CAL    acc_mag
   time                                                                               ...                                                
   2020-07-28 10:56:50.034                    -1.434783                         10.0  ...                            33.365878  10.117604
   2020-07-28 10:56:50.057                    -1.402174                         10.0  ...                            33.365878  10.113031
   2020-07-28 10:56:50.074                    -1.434783                         10.0  ...                            33.365878  10.117604
   2020-07-28 10:56:50.099                    -1.413043                         10.0  ...                            33.365878  10.112809
   2020-07-28 10:56:50.111                    -1.445652                         10.0  ...                            33.365878  10.116862

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`ShimmerPlusReader.timeshift()`.

.. code-block:: Python

   >>> reader.timeshift()
   >>> reader.data.head()
                           Shimmer_40AC_Accel_LN_X_CAL  Shimmer_40AC_Accel_LN_Y_CAL  ...  Shimmer_40AC_Temperature_BMP280_CAL    acc_mag
   time                                                                               ...                                                
   2018-11-06 11:13:05.814                    -1.434783                         10.0  ...                            33.365878  10.117604
   2018-11-06 11:13:05.837                    -1.402174                         10.0  ...                            33.365878  10.113031
   2018-11-06 11:13:05.854                    -1.434783                         10.0  ...                            33.365878  10.117604
   2018-11-06 11:13:05.879                    -1.413043                         10.0  ...                            33.365878  10.112809
   2018-11-06 11:13:05.891                    -1.445652                         10.0  ...                            33.365878  10.116862

Write the anonymized data to file, maintaining the original format:

.. code-block:: Python

   >>> reader.write("write_file.csv")
   >>> "write_file.csv" in os.listdir()
   True


Tags
####

Tags are timestamps that are important to the measuring process, like the start and finishing time of measurements.
The tag files can be obtained using the Android App `TimeStamp <https://play.google.com/store/apps/details?id=jp.m_c8bit.timestamp/>`_.

Read and access tags

.. code-block:: Python

   >>> tag_reader = devicely.TagReader('path/to/readfile')
   >>> tag_reader.data.head(3)
                        tag_number                tag
   time                                              
   2019-03-01 16:16:37           1              Shake
   2019-03-01 16:17:43           2              Start
   2019-03-01 16:18:20           3     BP Measurement

Anonymize the data by timeshifting the time of sampling by a random interval between one month and two years to the past.
If you would like to keep control over the shifting interval, you can provide either a :code:`pandas.Timedelta` or a :code:`pandas.Timestamp` object as a parameter to :code:`TagReader.timeshift()`.

.. code-block:: Python

   >>> tag_reader.timeshift()
   >>> tag_reader.data.head(3)
                        tag_number                tag
   time                                              
   2018-07-25 01:48:47           1              Shake
   2018-07-25 01:49:53           2              Start
   2018-07-25 01:50:30           3     BP Measurement

Write the data to file

.. code-block:: Python

   >>> tag_reader.write('path/to/writingfile')
   >>> 'writingfile' in os.listdir('path/to')
   True


Module Reference
================

:ref:`modindex`

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: devicely.empatica
    :members:

.. automodule:: devicely.spacelabs
    :members: