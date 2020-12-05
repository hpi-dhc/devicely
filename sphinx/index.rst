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

Creating an EmpaticaReader object

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
   >>> empatica_reader.IBI.head(3)
                              timedelta       ibi
   2020-10-16 17:04:41.671875  12.671875  0.734375
   2020-10-16 17:04:42.406250  13.406250  0.734375
   2020-10-16 17:04:43.187500  14.187500  0.781250
   >>> empatica_reader.BVP.head(3)
                              bvp
   2020-10-16 17:04:29.000000 -0.0
   2020-10-16 17:04:29.015625 -0.0
   2020-10-16 17:04:29.031250 -0.0
   >>> empatica_reader.EDA.head(3)
                                 eda
   2020-10-16 17:04:29.000  0.000000
   2020-10-16 17:04:29.250  0.052522
   2020-10-16 17:04:29.500  0.073018
   >>> empatica_reader.HR.head(3)
                        hr
   2020-10-16 17:04:39  51.0
   2020-10-16 17:04:40  51.5
   2020-10-16 17:04:41  51.0
   >>> empatica_reader.TEMP.head(3)
                           temp
   2020-10-16 17:04:29.000  31.13
   2020-10-16 17:04:29.250  31.13
   2020-10-16 17:04:29.500  31.13
   >>> empatica_reader.tags        
                                 0
   0 2020-10-16 17:05:03.589999914
   1 2020-10-16 17:05:14.109999895
   2 2020-10-16 17:05:23.380000114
   3 2020-10-16 17:05:40.559999943
   4 2020-10-16 17:05:52.859999895


Accessing the joined dataframe. It contains NaN values because the individual signals have different sampling frequencies.

.. code-block:: Python

   >>> empatica_reader.data.head(3)
                              bvp  eda  hr   temp  acc_x  acc_y  acc_z    acc_mag  timedelta  ibi
   2020-10-16 17:04:29.000000 -0.0  0.0 NaN  31.13   -3.0   11.0   60.0  61.073726        NaN  NaN
   2020-10-16 17:04:29.015625 -0.0  NaN NaN    NaN    NaN    NaN    NaN        NaN        NaN  NaN
   2020-10-16 17:04:29.031250 -0.0  NaN NaN    NaN   -3.0   11.0   60.0  61.073726        NaN  NaN

Anonymizing the data. This is done by shifting all measuring times. The shift can have different parameters.

.. code-block:: Python

   >>> empatica_reader.start_times
   {'bvp': Timestamp('2020-10-16 17:04:29'),
    'eda': Timestamp('2020-10-16 17:04:29'),
    'hr': Timestamp('2020-10-16 17:04:39'),
    'temp': Timestamp('2020-10-16 17:04:29'),
    'acc': Timestamp('2020-10-16 17:04:29'),
    'ibi': Timestamp('2020-10-16 17:04:29')}
   >>> empatica_reader.ACC.head(3).index
   DatetimeIndex(['2020-10-16 17:04:29',
                  '2020-10-16 17:04:29.031250',
                  '2020-10-16 17:04:29.062500'],
               dtype='datetime64[ns]', freq='31250U')
   >>> empatica_reader.data.head(3).index
   DatetimeIndex(['2020-10-16 17:04:29',
                  '2020-10-16 17:04:29.015625',
                  '2020-10-16 17:04:29.031250'],
               dtype='datetime64[ns]', freq=None)

   >>> empatica_reader.timeshift()

   >>> empatica_reader.start_times
   {'bvp': Timestamp('2020-03-07 03:02:16.693659368'),
   'eda': Timestamp('2020-03-07 03:02:16.693659368'),
   'hr': Timestamp('2020-03-07 03:02:26.693659368'),
   'temp': Timestamp('2020-03-07 03:02:16.693659368'),
   'acc': Timestamp('2020-03-07 03:02:16.693659368'),
   'ibi': Timestamp('2020-03-07 03:02:16.693659368')}
   >>> empatica_reader.ACC.head(3).index
   DatetimeIndex(['2020-03-07 03:02:16.693659368',
                  '2020-03-07 03:02:16.724909368',
                  '2020-03-07 03:02:16.756159368'],
               dtype='datetime64[ns]', freq='31250U')
   >>> empatica_reader.data.head(3).index
   DatetimeIndex(['2020-03-07 03:02:16.693659368',
                  '2020-03-07 03:02:16.709284368',
                  '2020-03-07 03:02:16.724909368'],
               dtype='datetime64[ns]', freq=None)


Writing the data back to csv files. The written data is organized in the same way as the read data. Thus it can be read by another EmpaticaReader.

.. code-block:: Python

   >>> empatica_reader.write('write_path')
   >>> os.listdir('write_path')
   ['HR.csv', 'BVP.csv', 'TEMP.csv', 'EDA.csv', 'tags.csv', 'ACC.csv', 'IBI.csv']


SpaceLabs
#########

Creating a SpacelabsReader object

.. code-block:: Python

   >>> spacelabs_reader = devicely.SpacelabsReader('path/to/spacelabsfile')

Accessing the data

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

The data contains EB-errors which can be dropped using `drop_EB`.
Before dropping, the 'timestamp' column may contain duplicate values. After dropping, however it will be unique and thus used as the index column.

.. code-block:: Python

   >>> spacelabs_reader.data.head(6)
               timestamp        date      time  SYS(mmHg)  DIA(mmHg)     x     y   z error
   0 2019-03-01 16:18:00  2019-03-01  16:18:00        107         76  78.0  78.0 NaN   NaN
   1 2019-03-01 16:19:00  2019-03-01  16:19:00         96         62  63.0  63.0 NaN   NaN
   2 2019-03-01 16:22:00  2019-03-01  16:22:00        100         68  64.0  64.0 NaN   NaN
   3 2019-03-01 16:23:00  2019-03-01  16:23:00        103         68  68.0  68.0 NaN   NaN
   4 2019-03-01 16:25:00  2019-03-01  16:25:00        101         67  65.0  65.0 NaN   NaN
   5 2019-03-01 16:31:00  2019-03-01  16:31:00         11          0   0.0   0.0 NaN    EB
   >>> spacelabs_reader.drop_EB()   
   >>> spacelabs_reader.data.head(6)
                              date      time  SYS(mmHg)  DIA(mmHg)     x     y   z error
   timestamp                                                                            
   2019-03-01 16:18:00  2019-03-01  16:18:00        107         76  78.0  78.0 NaN   NaN
   2019-03-01 16:19:00  2019-03-01  16:19:00         96         62  63.0  63.0 NaN   NaN
   2019-03-01 16:22:00  2019-03-01  16:22:00        100         68  64.0  64.0 NaN   NaN
   2019-03-01 16:23:00  2019-03-01  16:23:00        103         68  68.0  68.0 NaN   NaN
   2019-03-01 16:25:00  2019-03-01  16:25:00        101         67  65.0  65.0 NaN   NaN
   2019-03-01 16:33:00  2019-03-01  16:33:00        107         67  77.0  77.0 NaN   NaN


Anonymizing the data

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

Writing the data using the same formatation as the read data

.. code-block:: Python

   >>> spacelabs_reader.write('spacelabs_write_file.abp')
   >>> 'spacelabs_write_file.abp' in os.listdir()
   True

Tags
####

Creating a TagReader object

.. code-block:: Python

   >>> tag_reader = devicely.TagReader('path/to/readfile')

Accessing the data

.. code-block:: Python
   
   >>> tag_reader.data.head(3)
                        tag_number                tag
   time                                              
   2019-03-01 16:16:37           1              Shake
   2019-03-01 16:17:43           2              Start
   2019-03-01 16:18:20           3     BP Measurement

Anonymizing the data

.. code-block:: Python

   >>> tag_reader.timeshift()
   >>> tag_reader.data.head(3)
                        tag_number                tag
   time                                              
   2018-07-25 01:48:47           1              Shake
   2018-07-25 01:49:53           2              Start
   2018-07-25 01:50:30           3     BP Measurement

Writing the data to file

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