SSAPy-Data
==========

SSAPy-Data stores reusable data resources for `SSAPy <https://github.com/llnl/SSAPy>`_
and `SSAPy Toolkit <https://github.com/llnl/SSAPy-Toolkit>`_. The repository is
packaged as the ``llnl-ssapy-data`` Python distribution and exposes the
``ssapy_data`` import package. Data files live under ``src/ssapy_data/data`` so
users can receive required data through normal ``pip`` installation without Git
LFS, git submodules, or runtime GitHub downloads.

The initial package intentionally does not duplicate data already packaged by
base SSAPy. New SSAPy Toolkit datasets should be added here when they are needed
by toolkit functions and are not already available from the base ``llnl-ssapy``
wheel.

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

   gravity_header = read_text("egm84.egm")

   with data_path("Earth_graphics/ne_50m_ocean.shp") as path:
       print(path)

``data_path`` yields a real filesystem path for libraries that require paths.
Use the path only inside the context manager because zipped wheels may extract
resources to temporary locations.

Propulsion data
---------------

Reusable propulsion resources live under ``propulsion/``. Electric propulsion
benchmark throttle maps are packaged under ``propulsion/throttle_maps/electric``.
Solid and hybrid motor time-thrust curves should be imported only from sources
with explicit redistribution rights. The helper script
``scripts/import_thrustcurve_pd.py`` imports only ThrustCurve.org records marked
``license="PD"`` and writes normalized ``time_s,thrust_n`` CSV files.

Adding data
-----------

Add new reusable data below ``src/ssapy_data/data``. Preserve source filenames
when possible, and use subdirectories when a dataset has multiple sidecar files.
Do not add files already packaged by base SSAPy unless a later migration
explicitly moves that dependency here.
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

The repository publishes ``llnl-ssapy-data`` to PyPI through GitHub Actions and
PyPI trusted publishing. Configure PyPI before creating the first release:

* Create a PyPI trusted publisher, or pending publisher, for project
  ``llnl-ssapy-data``.
* Set the owner to ``llnl`` and repository to ``SSAPy-Data``.
* Set the workflow filename to ``publish.yml``.
* Set the GitHub environment to ``pypi``.

After PyPI trust is configured, publish by pushing a git tag that matches the
version in ``pyproject.toml``, for example ``v0.1.1``. The ``Publish to PyPI``
workflow builds a clean wheel and source distribution, runs tests, checks the
manifest, and uploads through OpenID Connect (OIDC). No PyPI API token is
required.

Data provenance
---------------

Each data pull request should document the source URL, license, retrieval date,
and any preprocessing steps for new packaged datasets. Candidate sources include:

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
