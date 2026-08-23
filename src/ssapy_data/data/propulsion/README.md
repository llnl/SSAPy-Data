# SSAPy Propulsion Data

This directory stores redistributable propulsion data for SSAPy Toolkit.

Policy:
- Store reusable propulsion data here, not in `SSAPy-Toolkit`.
- Prefer normalized CSV for small tables and original source files only when their license explicitly permits redistribution.
- Record source, license, retrieval date, and transformation notes in `sources.json`.
- Do not add manufacturer datasheets, extracted images, or unknown-license curves.

Current layout:
- `throttle_maps/electric/`: electric-propulsion throttle maps and benchmark steady-state performance tables.
- `thrust_curves/digitized/nasa_ntrs/`: NASA NTRS plot-only curves that were digitized with calibrated axes and packaged with per-curve metadata.
- `thrust_curves/solid_motor_pd/`: public-domain solid/hybrid motor time-thrust curves suitable for finite-burn examples.

ThrustCurve.org data should be imported only when the API reports `license="PD"`. Other categories (`free`, `other`, or missing) need manual legal/provenance review before packaging. The packaged `thrustcurve_org/index.csv` file summarizes the imported public-domain curves and links each normalized CSV to its metadata JSON.

Electric propulsion files in `throttle_maps/electric/` are steady-state operating points, not transient start-up or shutdown curves. Use them for throttle selection, thrust/Isp interpolation, and propulsion-system benchmarks.

Digitized NASA NTRS thrust curves are derived from plotted figures, not source
tables. Treat them as benchmark/examples with stated uncertainty. Each file has
a neighboring JSON sidecar with the NTRS citation, figure number, rights
metadata, extraction notes, and validation checks.

See `source_audit.md` for reviewed propulsion sources that were packaged,
rejected, or deferred.
