[![Actions Status: test](https://github.com/hpi-dhc/devicely/workflows/test/badge.svg)](https://github.com/hpi-dhc/devicely/actions/workflows/test.yml)

![Devicely Logo](/imgs/logo/devicely-logo.png)

## Documentation

https://hpi-dhc.github.io/devicely/

## Description

Package containing `readers` for reading data from different devices.
You can also `timeshift` the data to a specified interval and `write` the data back.

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

## Basic Usage

To use the package, after cloning this repository:

```
pip install .
```

Then:
```
import devicely
```

### Example

```
shift = pd.Timedelta(15,unit='d')
```

#### **Tags**
Reading Tags from the TimeStamp App

Timeshifting and Writing them back
```
tags = devicely.TagReader(tags_path)
tags.data.head()

tags.timeshift(shift)
tags.data.head()

tags.write(join(write_path, 'tags.csv'))
```

#### **Empatica**
Reading Empatica E4 Data

Timeshifting and Writing them back
```
empatica = devicely.EmpaticaReader(empatica_path)
empatica.data.head()

empatica.timeshift(shift)
empatica.data.head()

empatica.write(join(write_path, 'Empatica'))
```

#### **Faros**
Reading Bittium Faros 180 Data

Timeshifting and Writing them back
```
faros = devicely.FarosReader(faros_path)
faros.data.head()

faros.timeshift(shift)
faros.data.head()

faros.write(join(write_path, 'faros.csv'))
```

#### **Biovotion**
Reading Biovotion Everion Data

Timeshifting and Writing them back

* The reader method detects automatically if the `sensors` file is present or not.
```
everion = devicely.EverionReader(everion_path)
everion.data.head()

everion.timeshift(shift)
everion.data.head()

everion.write(join(write_path, 'Everion'))
```

#### **Spacelabs**
Reading Spacelabs Data

Timeshifting, Deidentifying and Writing them back

* The method deidentify generates a `random` subject id or you can specify one (e.g. 001)

* The method `drop_EB` will drop lines with an `EB` error

* The method `set_window` will create a `timedelta` window around the blood pressure measurement (e.g. 30 secs)

    * The type of window is defined by: `bfill` (before the start of the measurement),
`bffil` (half before and half after) of `ffill` (after the start of the measurement)
```
spacelabs = devicely.SpacelabsReader(spacelabs_path)
spacelabs.data.head()

spacelabs.timeshift(shift)
spacelabs.deidentify('001')
spacelabs.drop_EB()
spacelabs.data.head()

spacelabs.set_window(timedelta(seconds=30), 'bfill')
spacelabs.data.head()

spacelabs.write(join(write_path, 'spacelabs.abp'))
```

#### **Shimmer**
Reading Shimmer Consensys GSR (Shimmer3 GSR Development Kit)

Timeshifting and Writing them back

* Please define your `csv` delimiter (e.g. `,` `;` `\t`) in the reader method
```
shimmer_plus = devicely.ShimmerPlusReader(shimmer_file_path, delimiter=';')
shimmer_plus.data.head()

shimmer_plus.timeshift(shift)
shimmer_plus.data.head()

shimmer_plus.write(join(write_path, 'shimmer_plus.csv'))
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
* Pascal Hecker
```
