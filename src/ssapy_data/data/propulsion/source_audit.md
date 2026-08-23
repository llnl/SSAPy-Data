# Propulsion Source Audit

Retrieved: 2026-08-22

This file records the current propulsion-data search so future imports do not
repeat the same source review or accidentally package data without clear rights.

## Packaged Sources

- ThrustCurve.org public-domain RASP/RockSim samples: 596 solid/hybrid motor
  time-thrust curves under
  `thrust_curves/solid_motor_pd/thrustcurve_org/`.
- NASA NTRS 20100042402: NEXT TT10 electric-propulsion thrust comparison
  table under `throttle_maps/electric/next_tt10_thrust_comparison.csv`.
- NASA NTRS 20210023838: HERMeS TDU-3 electric-propulsion reference and
  expanded firing-condition table under
  `throttle_maps/electric/hermes_tdu3_throttle_map.csv`.
- NASA NTRS 20210015721: AEPS ETU-2 electric-propulsion reference and Power
  and Propulsion Element firing-condition table under
  `throttle_maps/electric/aeps_etu2_throttle_map.csv`.
- NASA NTRS 19980016322: SPT-140 Hall-thruster steady-state performance
  points under `throttle_maps/electric/spt140_performance_map.csv`.
- NASA NTRS digitized thrust curves: three public/export-clear plotted curves
  under `thrust_curves/digitized/nasa_ntrs/`.
  - NTRS 19730015083, Fig. 7: TE-M-521-5 apogee kick motor axial thrust.
  - NTRS 19900003335, Fig. 2.1: RSRM-3B reconstructed vacuum thrust.
  - NTRS 20090026004, Fig. 8: RS-18 normalized startup/shutdown thrust shape.
  Each CSV has a sidecar JSON with figure citation, uncertainty estimate,
  columns, and validation notes. Source PDFs and rendered plot images are not
  redistributed.

## Reviewed But Not Packaged

- NASA NTRS 19780059628, Space Shuttle SRB thrust shape design: public but
  rights metadata is `OTHER`; do not package without manual rights review.
- NASA NTRS 20100027316, Rocketdyne F-1 Saturn V first-stage engine: public
  historical description with design thrust, specific impulse, and startup
  narrative, but not a numeric curve source.
- NASA NTRS 20100021053, J-2X upper-stage engine: public overview with
  design-level thrust, specific impulse, and duration values, but not a
  numeric curve source.
- NASA NTRS 20140002697, NASA MSFC tri-gas thruster: public and
  export-clear, but the useful table is an `Isp` summary by catalyst
  configuration, not a time-thrust curve.
- NASA NTRS 19720014170, electrothermal hydrazine resistojet model
  specification: public and export-clear, but it provides requirements and
  operating limits rather than measured curves.
- NASA NTRS 20190030438, electrothermal ablation-fed pulsed plasma thruster:
  public and export-clear, but data are plotted impulse-bit trends; no
  tabular per-pulse curve was found in the extracted text.

## Current Gaps

- Redistributable time-thrust curves for flight-like cold-gas,
  monopropellant, bipropellant, and large liquid engines remain unresolved.
- Electric propulsion is represented by steady-state throttle/performance
  maps rather than transient curves, which is normally the more useful input
  for low-thrust orbit propagation.
- Manufacturer datasheets and unlicensed curve files remain excluded even if
  they are easy to find online.
