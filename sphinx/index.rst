devicely, a Python package for accessing health sensor data
===========================================================

The devicely package is made for reading, writing and anonymizing health sensor data from several sensors:

* `Empatica E4 (Firmware 2.1.0.4911) <https://e4.empatica.com/e4-wristband/>`_
* `Biovotion Everion (Firmware 03.06) <https://www.biovotion.com/everion/>`_
* `1-lead ECG monitor FarosTM 180 from Bittium (Firmware 3.5.1) <https://shop.bittium.com/product/36/bittium-faros-180-solution-pack/>`_
* `Spacelabs (SL 90217) <https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/>`_
* `Tags (obtained from the app: TimeStamp for Android Version 1.36) <https://play.google.com/store/apps/details?id=gj.timestamp&hl=en/>`_
* `Shimmer Consensys GSR (Shimmer3 GSR Development Kit) <https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab/>`_


devicely makes it easy to read sensor data and access it in common formats such as dataframes.

We provice a custom reader class for each sensor which provides three core methods: read, timeshift and anonymize.
The timeshift method changes the time of measurement, thereby automatically anonymizing the data.

After timeshifting, you can write the data in the same original sensor format.
Now you are safe to distribute the data with others.


Usage
-----

- :doc:`example`
- :doc:`moduleref`
- :doc:`Example data <https://github.com/hpi-dhc/devicely-documentation-sample-data>`

About devicely
--------------

- `GitHub <https://github.com/hpi-dhc/devicely>`_
- `PyPi <https://pypi.org/project/devicely/>`_
- :doc:`contribution`


.. toctree::
   :hidden:

   Quick Start Guide <example>
   moduleref
   contribution


