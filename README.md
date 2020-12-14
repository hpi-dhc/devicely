![Devicely Logo](/imgs/logo/devicely-logo.png)

## Documentation

https://hpi-dhc.github.io/devicely/

## Description

Package containing `readers` for reading files from different devices.

For a sample dataset go to: https://doi.org/10.6084/m9.figshare.12646217

So far, we have integrated:

Empatica E4 (Firmware 2.1.0.4911)

[Link](https://e4.empatica.com/e4-wristband)

Biovotion Everion (Firmware 03.06)

[Link](https://www.biovotion.com/everion/)

1-lead ECG monitor Faros<sup>TM</sup> 180 from Bittium (Firmware 3.5.1)

[Link](https://shop.bittium.com/product/36/bittium-faros-180-solution-pack)

Spacelabs (SL 90217)

[Link](https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/)

Tags (obtained from the app: TimeStamp for Android Version 1.36)

[Link](https://play.google.com/store/apps/details?id=gj.timestamp&hl=en)

Shimmer Consensys GSR (Shimmer3 GSR Development Kit)

[Link](https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab)

## Usage

To use the package, after cloning this repository:

```
pip install .
```

Then:
```
import devicely
```

**timeshift** is the timeshift in hours from the recording to UTC (1 means: UTC + 1 hour)

Reading Tags from the TimeStamp App
```
tags = devicely.TagReader(tag_file, timeshift=0)
tags.data
```

Reading Empatica E4 Data
```
empatica = devicely.EmpaticaReader(empatica_folder_path)
empatica.data.head()
```

Reading Bittium Faros 180 Data
```
faros = devicely.FarosReader(faros_folder_path, timeshift=0)
faros.data.head()
```

Reading Biovotion Everion Data

The method detects automatically if the `sensors` file is present or not.
```
everion = devicely.EverionReader(everion_folder_path)
everion.data.head()
```


Reading Spacelabs Data

The column `stress_test` was created for adding information on when a stress test happened.

E. g. blood pressure measurements before and after a test.
This is not part of the `abp` file.

The method `set_window` will create a `timedelta` window around the blood pressure measurement (e. g. 30 secs)

The type of window is defined by: `bfill` (before the start of the measurement) or `bffil` (half before and half after)
```
spacelabs = devicely.SpacelabsReader(spacelabs_folder_path)
spacelabs.set_window(timedelta(seconds=30), 'bfill')
spacelabs.data.head()
```


Reading Shimmer Consensys GSR (Shimmer3 GSR Development Kit)

Please define your `csv` delimiter (e. g. `,` `;` `\t`) and `timeshift` if applicable
```
shimmer_plus = devicely.ShimmerPlusReader(shimmer_file_path, delimiter=';')
shimmer_plus.data.head()
```


To run a notebook with examples:
```
pipenv install
pipenv shell
pipenv run jupyter notebook
```

And open `example.ipynb`


## Contributors

```
* Ariane Sasso
* Arpita Kappattanavar
* Bjarne Pfitzner
* Felix Musmann
* Jost Morgenstern
* Lin Zhou
```
