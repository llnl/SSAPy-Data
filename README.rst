SSAPy-Data
==========

SSAPy-Data stores a complete backup of reusable data resources for `SSAPy <https://github.com/llnl/SSAPy>`_
and `SSAPy Toolkit <https://github.com/llnl/SSAPy-Toolkit>`_. The repository is
The archive retains the historical ``ssapy_data`` package layout. Data files live under ``src/ssapy_data/data`` so
The split ``ssatk-data-*`` repositories are the published distributions; this
repository is retained as the complete archival source and is not published to
PyPI. Users can receive required data through the split packages without Git
LFS, git submodules, or runtime GitHub downloads.

Since 0.2.0 this package also carries base SSAPy's own data under ``ssapy/``:
two short planetary ephemerides (JPL DE440's ``de440s.bsp``, 1849-2150, SSAPy's
default, and a 1900-2150 excerpt of DE430, ``de430_1900_2150.bsp``, for
reproducing older SSAPy results; SSAPy downloads the full-span kernels from
NAIF when an epoch needs them), the DE440 lunar orientation kernel, the WGS84/EGM84/EGM96/EGM2008 Earth gravity
models, the GRGM1200A lunar gravity field, the Natural Earth ocean outline and
the Earth/Moon textures. ``llnl-ssapy`` depends on this package and no longer
stores data with Git LFS. ``scripts/import_ssapy_core_data.py`` imports those
files from an SSAPy data directory, checks them against SSAPy's recorded
SHA-256 digests, and downloads ``de440s.bsp`` from NAIF against a pinned
digest.

Installation
------------

Install from a local clone in editable mode:

.. code-block:: bash

   pip install -e .

Build the wheel and source distribution:

.. code-block:: bash

   python -m build
   ls -lh dist/

Using packaged data
-------------------

Access packaged data with ``importlib.resources`` helpers exposed by
``ssapy_data``:

.. code-block:: python

   from ssapy_data import data_path, read_text

   data_readme = read_text("README.md")

   with data_path("earth_day_2048.jpg") as path:
       print(path)

``data_path`` yields a real filesystem path for libraries that require paths.
Use the path only inside the context manager because zipped wheels may extract
resources to temporary locations.

Data organization and submission routing
----------------------------------------

This repository is the complete archival copy. New data should normally be
submitted to the matching public component repository and mirrored here when
the archive is refreshed. Keep each dataset in the narrowest applicable area:

* ``environment/`` — Earth orientation parameters and space-weather records;
  submit to ``Data-Core``.
* ``bright_stars*.csv`` and Earth viewer textures/maps — general sky and Earth
  visualization resources; submit to ``Data-Core``.
* ``ssapy/`` Earth gravity coefficients (EGM84, EGM96, EGM2008, WGS84) —
  submit to ``Data-Gravity``.
* ``ssapy/gggrx_1200a_sha.*`` — the lunar GRGM1200A gravity field; submit to
  ``Data-Lunar-Gravity``.
* ``ssapy/de440s.bsp``, ``ssapy/de430_1900_2150.bsp``, lunar orientation,
  ``moon.png``, and ``moon_dem.npz`` — lunar and planetary ephemeris/visual
  resources; submit to ``Data-Lunar``.
* ``propulsion/`` — electric-thruster maps, digitized NASA curves, and public
  domain solid-motor curves; submit to ``Data-Propulsion``.
* ``benchmarks/`` and ``ssapy_satellites_default.json`` — reference histories,
  comparison outputs, and catalog snapshots; submit to ``Data-Benchmarks``.
* ``sources.json`` and ``propulsion/sources.json`` — provenance ledgers that
  must be updated with every new file, including source URL, license,
  retrieval date, and transformation notes.

Do not add generated plots, caches, downloaded kernels outside the declared
resource set, or files without redistribution rights. Regenerate
``manifest.json`` with ``python scripts/update_manifest.py`` after changing
data, then run the package-data tests. The component packages are published to
PyPI; this repository remains the backup and review record.

Propulsion data
---------------

Reusable propulsion resources live under ``propulsion/``. Electric propulsion
benchmark throttle maps are packaged under ``propulsion/throttle_maps/electric``.
These electric files are steady-state operating-point tables, not transient
start-up or shutdown curves.
Digitized thrust curves from public NASA Technical Reports Server (NTRS) plots
are packaged under ``propulsion/thrust_curves/digitized/nasa_ntrs`` with one
CSV and one sidecar JSON metadata file per curve. These files are derived from
calibrated plot extraction rather than original tabular source data, so use the
recorded uncertainty and validation notes when treating them as benchmarks.
Solid and hybrid motor time-thrust curves should be imported only from sources
with explicit redistribution rights. The helper script
``scripts/import_thrustcurve_pd.py`` imports only ThrustCurve.org records marked
``license="PD"`` from RASP and RockSim simulator files, then writes normalized
``time_s,thrust_n`` CSV files.

The packaged ThrustCurve.org snapshot includes an ``index.csv`` summary under
``propulsion/thrust_curves/solid_motor_pd/thrustcurve_org``. Use the index to
select a curve by manufacturer, designation, impulse class, burn time, thrust,
or total impulse before loading the neighboring normalized CSV.
The propulsion directory also includes ``sources.json`` and
``source_audit.md`` to record source URLs, rights metadata, transformations,
and searched sources that were packaged, rejected, or deferred.

Lunar topography
-----------------

``data/moon_dem.npz`` contains an 8-pixel-per-degree LOLA elevation grid from
NASA's CGI Moon Kit.  The ``elev_km`` array is measured relative to a 1737.4 km
lunar sphere and is an optional offline input to SSAPy Toolkit's Moon texture
baker (``ssapy-bake-moon --dem``), which otherwise downloads the
16-pixel-per-degree source from NASA. The generated WebGL textures are
intentionally not packaged here.  Source,
license, and transformation details are recorded in ``data/sources.json``.

Adding data
-----------

Add new reusable data below ``src/ssapy_data/data``. Preserve source filenames
when possible, and use subdirectories when a dataset has multiple sidecar files.
Base SSAPy's data now lives under ``ssapy/``; add files there only for
base SSAPy, and record their sources in ``sources.json``.
After adding, replacing, or removing data, regenerate the manifest:

.. code-block:: bash

   python scripts/update_manifest.py
   python -m pytest
   python -m build

The manifest records each packaged file path, byte count, and SHA-256 digest in
``src/ssapy_data/manifest.json``. Pull requests that change data should also
update the source/provenance notes in this README when the dataset source or
license differs from the existing entries.

Size guidance
-------------

The initial wheel contains only the package helpers and a data-directory README.
Before adding large datasets, estimate the built wheel size with:

.. code-block:: bash

   python -m build --wheel
   ls -lh dist/*.whl

If a future dataset pushes the wheel above PyPI limits, split the data into a
separate companion package rather than using Git LFS in SSAPy Toolkit.

Publishing
----------

This repository is an archival backup and does not publish to PyPI. Publishable
components live in the public ``ssatk-data-*`` repositories, each with its own
PyPI trusted-publishing workflow.

Data provenance
---------------

Each data pull request should document the source URL, license, retrieval date,
and any preprocessing steps for new packaged datasets. Top-level source records
live in ``src/ssapy_data/data/sources.json``. Propulsion source records live in
``src/ssapy_data/data/propulsion/sources.json``. Candidate sources include:

* Earth gravity fields:
  `ICGEM time-variable gravity fields <http://icgem.gfz-potsdam.de/tom_longtime>`_
* Other celestial bodies:
  `ICGEM celestial gravity fields <http://icgem.gfz-potsdam.de/tom_celestial>`_

Code of Conduct
---------------

Please note that SSAPy-Data has a
`Code of Conduct <https://github.com/LLNL/SSAPy-Data/blob/main/CODE_OF_CONDUCT.md>`_.
By participating in the SSAPy-Data community, you agree to abide by its rules.

License
-------

SSAPy-Data is distributed under the terms of the MIT license. All new
contributions must be made under the MIT license.

See the `license <https://github.com/LLNL/SSAPy-Data/blob/main/LICENSE>`_ and
`NOTICE <https://github.com/LLNL/SSAPy-Data/blob/main/NOTICE>`_ for details.

SPDX-License-Identifier: MIT

LLNL-CODE-862420
