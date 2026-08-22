# SSAPy Propulsion Data

This directory stores redistributable propulsion data for SSAPy Toolkit.

Policy:
- Store reusable propulsion data here, not in `SSAPy-Toolkit`.
- Prefer normalized CSV for small tables and original source files only when their license explicitly permits redistribution.
- Record source, license, retrieval date, and transformation notes in `sources.json`.
- Do not add manufacturer datasheets, extracted images, or unknown-license curves.

Current layout:
- `throttle_maps/electric/`: electric-propulsion throttle maps and benchmark performance tables.
- `thrust_curves/solid_motor_pd/`: public-domain solid/hybrid motor time-thrust curves suitable for finite-burn examples.

ThrustCurve.org data should be imported only when the API reports `license="PD"`. Other categories (`free`, `other`, or missing) need manual legal/provenance review before packaging.
