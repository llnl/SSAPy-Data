# NASA NTRS Digitized Thrust Curves

This directory contains small thrust-curve datasets digitized from public,
export-clear NASA Technical Reports Server (NTRS) plot figures.

Use these curves as engineering examples and regression references, not as
authoritative flight certification data. The source reports did not provide
machine-readable time-thrust tables for these curves. The CSV values were
extracted from rendered plot figures with calibrated axes, and each sidecar JSON
records the figure citation, rights metadata, estimated digitization
uncertainty, units, and validation notes.

Files:
- `index.csv`: summary of packaged digitized curves and their sidecar metadata.
- `ntrs_19730015083_te_m_521_5_axial_thrust_digitized.csv`: TE-M-521-5 apogee
  kick motor axial thrust from NTRS 19730015083, Figure 7.
- `ntrs_19900003335_rsrm_3b_reconstructed_vacuum_thrust_digitized.csv`:
  RSRM-3B reconstructed vacuum thrust from NTRS 19900003335, Figure 2.1.
- `ntrs_20090026004_rs18_startup_normalized_thrust_digitized.csv`: RS-18
  normalized startup/shutdown thrust shape from NTRS 20090026004, Figure 8.

The source PDFs and rendered plot images are not redistributed in this package.
