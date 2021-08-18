[![PyPI version](https://badge.fury.io/py/devicely.svg)](https://badge.fury.io/py/devicely)
[![Actions Status: test](https://github.com/hpi-dhc/devicely/workflows/test/badge.svg)](https://github.com/hpi-dhc/devicely/actions/workflows/test.yml)
![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jostmorgenstern/270a0114dfad9251945a146dd6d29fa6/raw/devicely_coverage_main.json)
[![DOI](https://zenodo.org/badge/279395106.svg)](https://zenodo.org/badge/latestdoi/279395106)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hpi-dhc/devicely/HEAD)

![Devicely Logo](/imgs/logo/devicely-logo.png)

devicely is a Python package for reading, de-identifying and writing data from various health monitoring sensors.
With devicely, you can read sensor data and have it easily accessible in dataframes.
You can also de-identify data and write them back using their original data format. This makes it convenient to share sensor data with other researchers while mantaining people's privacy.

[Documentation](https://hpi-dhc.github.io/devicely/)

[PyPi](https://pypi.org/project/devicely/)

## Sneak Peek

Installing devicely is as easy as executing: 

`pip install devicely`

All devices contain the following methods as exemplified through Empatica:

```
empatica_reader = devicely.EmpaticaReader(path_to_empatica_files)
empatica_reader.timeshift()
empatica_reader.write(path_to_write_files)
```

You can also try this [notebook](https://github.com/hpi-dhc/devicely/blob/main/example.ipynb) with examples or check our binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hpi-dhc/devicely/HEAD) (don't forget to upload the example data)

The example data can be obtained by cloning [this repository](https://github.com/hpi-dhc/devicely-documentation-sample-data).

## Quick Start

To get started quickly, follow our [quick-start guide](https://hpi-dhc.github.io/devicely/example.html#).

Or check the full documentation: https://hpi-dhc.github.io/devicely/


## Supported Sensors

- [Empatica E4](https://e4.empatica.com/e4-wristband) is a wearable device that offers real-time physiological data acquisition such as blood volume pulse, electrodermal activity (EDA), heart rate, interbeat intervals, 3-axis acceleration and skin temperature.

- [Biovotion Everion](https://www.biovotion.com/everion/) is a wearable device used for the continuous monitoring of vital signs. Currently, it measures the following vital signs: heart rate, blood pulse wave, heart rate variability, activity, SPO2, blood perfusion, respiration rate, steps, energy expenditure, skin temperature, EDA / galvanic skin response (GSR), barometric pressure and sleep.

- [1-lead ECG monitor Faros<sup>TM</sup> 180 from Bittium](https://shop.bittium.com/product/36/bittium-faros-180-solution-pack) is a one channel ECG monitor with sampling frequency up to 1000 Hz and a 3D acceleration sampling up to 100Hz.

- [Spacelabs (SL 90217)](https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/) is an oscillometric blood pressure (BP) monitor which can be used to automatically track a person's BP in specificed time intervals.

- [TimeStamp for Android](https://play.google.com/store/apps/details?id=gj.timestamp&hl=en) allows you to record the timestamp of an event at the time it occurs. It also allows you to create specific tags such as "Running" or "Walking" and timestamp those specific activities.

- [Shimmer Consensys GSR](https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab) is a device that is used to collect sensor data in real time and it contains sensors such as GSR / EDA, photoplethysmography (PPG), 3-axis accelerometer, 3-axis gyroscope, 3-axis magnetometer & integrated altimeter. 

## How to Contribute

If you want to be part of this mission, please check our documentation on how to contribute [here](https://hpi-dhc.github.io/devicely/contribution.html).

## Contributors

```
* Ariane Sasso
* Arpita Kappattanavar
* Bjarne Pfitzner
* Felix Musmann
* Jost Morgenstern
* Lin Zhou
* Pascal Hecker
* Philipp Hildebrandt
* Sidratul Moontaha
```
