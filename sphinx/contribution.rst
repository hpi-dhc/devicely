How to contribute
=================

Whether you would like to add a new sensor, fix a bug or help with packaging, we would love for you to contribute!
To make a contribution, please fork `our repository <https://github.com/hpi-dhc/devicely>`_ and open a pull request when you are done with your changes.

If you wonder why we do not have a ``setup.py``, ``setup.cfg`` or ``requirements.txt``, it is because we use `poetry <https://python-poetry.org/>`_ for packaging, building and dependency management.

The following steps illustrate what you need to do to add a new sensor class to devicely:

Add a sensor class
------------------

Your sensor class needs to have its own module in the devicely package:

.. image:: devicely_structure.png
  :width: 600
  :alt: devicely package structure

Please create a class member for each signal that your sensor records. To provide an example, if your sensor contains heart rate and acceleration data,
use uppercase attribute names like ``reader.ACC`` and ``reader.HR``. These attributes should be dataframes, indexed by time of measurement.
For metadata, you can use basic data structures such as dictionaries.
Apart from the individual signal dataframes, your sensor should have an attribute ``reader.data`` which is a joined dataframe of all individual signal dataframes.

The ``timeshift`` method should accept three types of parameters: nothing, a ``pandas.Timestamp`` or a ``pandas.Timedelta``.
With no parameter, all time-related data attributes are shifted between one month and two years to the past.
With a ``pandas.Timedelta``, all attributes are shifted by adding the timedelta to them.
With a ``pandas.Timestamp``, all attributes are shifted such that the provided timestamp is the earliest data entry and all other data entries keep the same distance to it.

Timeshifting is not the only way to anonymize data. If your sensor uses other metadata such as a patient id, please add a method ``deidentify`` to clear such metadata.
You can look at ``devicely.SpacelabsReader.deidentify`` for an example.

With the ``reader.write`` method, users can write the identified data to be persistent, ideally in the same original sensor format.
Keeping the original format is not strictly necessary, just make sure that your reader class can be instantiated with the written data.

Write unit tests
----------------

Unit tests ensure that our sensor classes work the way we expect them to, which is why we aim for a high test coverage.
The existing test cases are a good example to see how your test case should be structured.
In general, have one test case for your sensor and one directory with data for testing.
Write test methods for the most important use cases of your sensor, e.g. reading, timeshifting and writing.
Please make sure that your test cases run fairly quickly as this helps us run tests locally and keep the GitHub Actions jobs fast.
It helps to use small sensor files for testing, e.g. only 30 seconds long.


Write documentation
-------------------

At devicely, we live by the motto **Docs or it didn't happen**.

Therefore, all sensor classes need to be documented well.
Most importantly, you need to add the following docstrings to your class:

1. a docstring on top of the class definition containing information about the sensor and what the most important class attributes are
2. a docstring for each method that users are meant to call specifying the syntax, parameters and return values

Apart from docstrings, all you need to do is add example code to the `example notebook <https://github.com/hpi-dhc/devicely/blob/docs/example.ipynb>`_.
Not only is this notebook meant to be run by users themselves, but it is also rendered in our :doc:`example` documentation section.

The docstrings and the notebook are basically all you have to do to document your sensor class. Feel free to look at the existing sensors as a guide!


Provide example data
--------------------

If you want people to try out your reader class, you need to provide example data.
For this purpose we maintain this `example data repository <https://github.com/jostmorgenstern/devicely-documentation-sample-data>`_,
to which you can create a PR to supply example data for your sensor.