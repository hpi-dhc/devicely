---
title: 'Devicely: A Python package for reading, time-shifting and writing sensor data'
tags:
  - Python
  - Wearables
  - Sensors
authors:
  - name: Ariane Morassi Sasso^[ariane.morassi-sasso@hpi.de]
    orcid: 0000-0002-3669-4599
    affiliation: 1
 - name: Jost Morgenstern^[your@email.com]
    orcid: 0000-0000-0000-0000
    affiliation: 1
- name: Felix Musmann^[felix.musmann@student.hpi.uni-potsdam.de]
  orcid: 0000-0001-5365-0785
  affiliation: 1
affiliations:
 - name: Digital Health Center, Hasso Plattner Institute, University of Potsdam
   index: 1
date: 08 March 2021
bibliography: paper.bib
---

# Summary

Wearable devices can track a multitude of parameters such as heart rate, body
temperature, blood oxygen saturation, acceleration, blood glucose and much more
`[@Kamisalic2018:2018]`. Moreover, they are becoming increasingly popular with a steeping
increase in market presence in 2020 alone `[@IDC2020:2020]`. Applications for wearable
devices varies from tracking cardiovascular risks `[@Bayoumy2021:2021]` to identifying
COVID-19 onset `[@Mishra2020:2020]`. Therefore, there is a great need for scientists to
easily go through data acquired from different wearables in an easy manner.
In order to solve this problem and empower scientists working with biosignals,
we developed the **devicely** package. It represent the data in a science-friendly
format and let scientists focus on what they want: the analysis of biosignals.

# Statement of need

Every wearable company has a different data format and reading this data is
usually a challenge for scientists. Therefore, we developed the **devicely** package
in order for researchers to read different sensor data in a an easily and
friendly way. We also added two methods to help with data _deidentification_, one
is called timeshift and the other is a write method. The idea behind them is
that you can timeshift all your time series to a different time from the one the
actual experiments occurred and them write this new deidentified dataset back to
the original data format. This will empower scientists to keep patient privacy
and hopefully share more data to increase research reproducibility.


# Design

Jost: Explain how people could extend the package, e.g. adding a new sensor.

# Functionalities

Jost: Explain the basic functionalities of reading, time-shifting and writing sensor data.

# Mention

This package was used in the following paper:

Morassi Sasso, A., Datta, S., Jeitler, M., Steckhan, N., Kessler, C. S.,
Michalsen, A., Arnrich, B., & Böttinger, E. (2020).
HYPE: Predicting Blood Pressure from Photoplethysmograms in a Hypertensive
Population. In M. Michalowski & R. Moskovitch (Eds.), Artificial Intelligence in
Medicine. AIME 2020. Lecture Notes in Computer Science, volume 12299 (pp.
325–335). Springer, Cham. https://doi.org/10.1007/978-3-030-59137-3_29

GitHub: https://github.com/arianesasso/aime-2020

# Acknowledgements

We acknowledge contributions from Arpita Kappattanavar, Pascal Hecker, Bjarne Pfitzner and Lin
Zhou during the genesis and testing of this package.

# References