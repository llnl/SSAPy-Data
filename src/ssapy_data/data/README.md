# SSAPy Data Payload Directory

Add new reusable datasets for SSAPy Toolkit under this directory. Base SSAPy's own data (ephemerides, gravity models, textures) lives under `ssapy/`; it is imported from SSAPy with `scripts/import_ssapy_core_data.py`.

Source and citation records live in `sources.json`. Propulsion-specific source
records live in `propulsion/sources.json`. Every new data file should have an
entry in one of those ledgers before it is merged.

Environment inputs are grouped below `environment/`; the first bundle is the
frozen IERS Finals2000A Earth orientation series used for reproducible GCRF /
ITRF and UT1-aware workflows.

The `environment/space_weather/` bundle supplies solar-flux and geomagnetic
indices for the optional NRLMSISE-00 atmosphere adapter in SSATK.

After changing files here, run:

```bash
python scripts/update_manifest.py
```
