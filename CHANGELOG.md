# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0]
- removed acceleration magnitude from devicely.EmpaticaReader and devicely.FarosReader since it was out of the scope of the package
- added more flexibility to missing files (e.g. ACC.csv, EDA.csv) to devicely.EmpaticaReader
- changed TagsReader to TimeStampReader to be more consistent with the class naming structure in devicely
- deprecated methods in devicely.SpacelabsReader: set_window and drop_EB
- fixed issue with the timestamp index and fixed column names in devicely.SpacelabsReader

## [1.0.0] - 2021-07-19
### Added
- devicely.FarosReader can both read from and write to EDF files and directories
- devicely.FarosReader has as attributes the individual dataframes (ACC, ECG, ...) and not only the joined dataframe

### Changed
- in devicely.SpacelabsReader, use xml.etree from the standard library instead of third-party "xmltodict"
- switch from setuptools to Poetry

### Removed
- removed setup.py because static project files such as pyproject.toml are preferred