SSAPy-Data
==========

SSAPy-Data stores reusable data resources for `SSAPy <https://github.com/llnl/SSAPy>`_
and `SSAPy Toolkit <https://github.com/llnl/SSAPy-Toolkit>`_. The repository is
packaged as the ``llnl-ssapy-data`` Python distribution and exposes the
``ssapy_data`` import package. Data files live under ``src/ssapy_data/data`` so
users can receive the required data through normal ``pip`` installation without
Git LFS, git submodules, or runtime GitHub downloads.

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

Adding data
-----------

Add new reusable data below ``src/ssapy_data/data``. Preserve source filenames
when possible, and use subdirectories when a dataset has multiple sidecar files.
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

The current wheel is well below the usual PyPI per-file upload limit of about
100 MiB. Before adding large datasets, estimate the built wheel size with:

.. code-block:: bash

   python -m build --wheel
   ls -lh dist/*.whl

If a future dataset pushes the wheel above PyPI limits, split the data into a
separate companion package rather than using Git LFS in SSAPy Toolkit.

Data provenance
---------------

The planetary ephemerides (``de430.bsp`` when present) were downloaded from
`NAIF generic SPK kernels <https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/>`_.

Earth gravity models were downloaded from
`GeographicLib gravity models <https://geographiclib.sourceforge.io/html/gravity.html>`_.
GeographicLib is MIT-licensed.

Moon gravity models were downloaded from
`NASA Goddard Planetary Data Archives <https://pgda.gsfc.nasa.gov/products/50>`_.

Future candidate sources include:

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
