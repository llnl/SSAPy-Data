# CelesTrak space-weather inputs

`SW-All.csv` is a frozen CelesTrak Space Weather data snapshot containing
daily solar-flux and geomagnetic indices from 1957-10-01 through the current
observed/predicted interval. SSATK uses the adjusted F10.7 value, centered
81-day adjusted F10.7 average, daily Ap, and eight 3-hour Ap values required
by the Naval Research Laboratory Mass Spectrometer and Incoherent Scatter
(NRLMSISE-00) atmosphere model.

The source retains observed (`OBS`), interpolated (`INT`), predicted daily
(`PRD`), and predicted monthly (`PRM`) records. Consumers must opt in before
using predicted records. The original CSV is retained without transformation;
the sidecar JSON records the retrieval, checksum, field mapping, and source
terms.

Source and format documentation:

- https://celestrak.org/SpaceData/SW-All.csv
- https://celestrak.org/SpaceData/SpaceWx-format.php
