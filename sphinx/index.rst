devicely, a python package for reading, timeshifting and writing sensor data
============================================================================

The devicely package is made for reading, writing and de-identifying health sensor data from several sensors:

* `Empatica E4 <https://e4.empatica.com/e4-wristband/>`_ is a wearable device that offers real-time physiological data acquisition such as blood volume pulse, electrodermal activity (EDA), heart rate, interbeat intervals, 3-axis acceleration and skin temperature.
* `Biovotion Everion <https://www.biovotion.com/everion/>`_ is a wearable device used for the continuous monitoring of vital signs. Currently, it measures the following vital signs: heart rate, blood pulse wave, heart rate variability, activity, SPO2, blood perfusion, respiration rate, steps, energy expenditure, skin temperature, EDA / galvanic skin response (GSR), barometric pressure and sleep.
* `1-lead ECG monitor Faros<sup>TM</sup> 180 from Bittium <https://shop.bittium.com/product/36/bittium-faros-180-solution-pack>`_ is a one channel ECG monitor with sampling frequency up to 1000 Hz and a 3D acceleration sampling up to 100Hz.
* `Spacelabs (SL 90217) <https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/>`_ is an oscillometric blood pressure (BP) monitor which can be used to automatically track a person's BP in specificed time intervals.
* `TimeStamp for Android <https://play.google.com/store/apps/details?id=gj.timestamp&hl=en>`_ allows you to record the timestamp of an event at the time it occurs. It also allows you to create specific tags such as "Running" or "Walking" and timestamp those specific activities.
* `Shimmer Consensys GSR <https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab>`_ is a device that is used to collect sensor data in real time and it contains sensors such as GSR / EDA, photoplethysmography (PPG), 3-axis accelerometer, 3-axis gyroscope, 3-axis magnetometer & integrated altimeter.

devicely makes it easy to read sensor data and access it in common formats such as dataframes.

We provide a custom reader class for each sensor which has three core methods: read, timeshift and write.
The timeshift method changes the time of measurement, thereby automatically
helping to de-identify the data.

After timeshifting, you can write the data in the original data format.
Now you have one more safety measure in place that will facilitate data sharing.


Usage
-----

- :doc:`example`
- :doc:`moduleref`


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


