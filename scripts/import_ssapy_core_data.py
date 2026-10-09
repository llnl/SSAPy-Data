#!/usr/bin/env python3
"""Import base SSAPy's data files into ``src/ssapy_data/data/ssapy``.

SSAPy (``llnl-ssapy``) shipped its ephemerides, gravity models and textures in
``ssapy/data`` through Git LFS. This script moves that dependency here. It
reads an SSAPy data directory with the real files (an SSAPy clone after
``git lfs pull``, or ``site-packages/ssapy/data`` of an installed
``llnl-ssapy <= 1.1.10``), checks every file against the SHA-256 recorded in
SSAPy's Git LFS pointers, and copies it.

Two planetary ephemerides are packaged, each over a short span; SSAPy
downloads the full-span kernels from NAIF when an epoch needs them.

* JPL DE440 (SSAPy's default): ``de440s.bsp`` (32.7 MB, 1849-12-26 to
  2150-01-22), consistent with the DE440 lunar orientation kernel. It is
  downloaded from NAIF (or read from ``--de440s``) and checked against the
  SHA-256 below.
* JPL DE430 (SSAPy <= 1.1.10): SSAPy's ``de430.bsp`` (119.7 MB) exceeds
  GitHub's 100 MB file limit, so it is cut to 1900-2150 with
  ``python -m jplephem excerpt`` (``de430_1900_2150.bsp``, 27.2 MB). The
  excerpt keeps DE430's Chebyshev records for that span; positions agree
  with the full kernel to 4e-13 relative (float64 rounding).

Usage::

    python scripts/import_ssapy_core_data.py /path/to/SSAPy/ssapy/data
    python scripts/update_manifest.py
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "ssapy_data" / "data" / "ssapy"

DE430_SOURCE = "de430.bsp"
DE430_EXCERPT = "de430_1900_2150.bsp"
DE430_START, DE430_END = "1900/1/1", "2150/1/1"

EPHEMERIS = "de440s.bsp"
EPHEMERIS_URL = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp"
EPHEMERIS_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
EPHEMERIS_BYTES = 32726016

# SHA-256 and size of each file as recorded in SSAPy's Git LFS pointers
# (identical to the llnl-ssapy 1.1.10 wheel).
EXPECTED = {
    "Earth_graphics/ne_50m_ocean.README.html": ("f6987c4011e6215c45bcb9a9e7a62fa417a4f8a91f629be9e13b5f29f1c72d4c", 22174),
    "Earth_graphics/ne_50m_ocean.VERSION.txt": ("0874a8fe36effb87780f431845b5a7d85be657f2bd998ce8eeace717860d3b78", 7),
    "Earth_graphics/ne_50m_ocean.cpg": ("3ad3031f5503a4404af825262ee8232cc04d4ea6683d42c5dd0a2f2a27ac9824", 5),
    "Earth_graphics/ne_50m_ocean.dbf": ("162d515911b17e35d36e22c5757e75fd37bdd38db2bc0011b9c79888a28bb4f5", 176),
    "Earth_graphics/ne_50m_ocean.prj": ("98aaf3d1c0ecadf1a424a4536de261c3daf4e373697cb86c40c43b989daf52eb", 143),
    "Earth_graphics/ne_50m_ocean.shp": ("6ff1190e8430e493cf8eed99393f021b7562b600b9a7a11aa23ce45b6035d8b8", 978340),
    "Earth_graphics/ne_50m_ocean.shx": ("449353f638399c48c4cfe59e8f945e5c3025a4e412e9bcd0eeba64ba137ae7c1", 108),
    "de430.bsp": ("6e1b277c5f07135a84950604b83e56b736be696a7f3560bcddb1d4aeb944fca1", 119741440),
    "earth.png": ("6e8a1296caef991dcdba963fdc72816e4095720d005e7af6688b060e5fb85aa4", 8825662),
    "egm2008.egm": ("031ecae647986faadf3f3a0177ba07ffcb73a2504b084c2e1c82b97cd9e61c75", 790),
    "egm2008.egm.cof": ("ebed5b09e3da7aeae37ac49e7b8c803fda0a525462bba374f762d6345624d132", 75755304),
    "egm84.egm": ("549e21625b71a0f0daec8477e0f4928338885ed2269ff70e351b15c3e6e0d43e", 800),
    "egm84.egm.cof": ("f95fa2967091b9a0630ae7f34934446f17a02f73e5b648ea919db4174b047633", 262112),
    "egm96.egm": ("cdf0896bb34c1f8ad7ea1c4126cf949fe5069ad9df17c2a66cf3d81da096970e", 753),
    "egm96.egm.cof": ("fd427a88a944e2df46d3a3e1aefdb17a68e892e3decdf1382f3ca14de9b6f2ae", 2085160),
    "gggrx_1200a_sha.lbl": ("8d46351c2e73db699d4669a98da1f47551086cbee321d8f9baa3fdb6b65d3d5f", 10637),
    "gggrx_1200a_sha.tab": ("fa04c3dce9376948ad243f3df74144e2602f12d183ea4d179604ed0a79da7ded", 88059844),
    "moon.png": ("4d9e6eebd180262aefe7555a0231927e5142954144cfcf2c4a10876b7c218027", 13728894),
    "moon_pa_de440_200625.bpc": ("60cd55aa401ea2ea97360636f567554bfe4e37bb829f901b4460a455dfaf783f", 12863488),
    "wgs84.egm": ("594ff1c9dc2363e50d663003deb9baca2e144d096d70fc9b7a6c1c86f5b781f0", 724),
    "wgs84.egm.cof": ("aeedf849678826d171b731eb7a783ab5d7e47552413da551418d21445fc3a2ec", 192),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_ephemeris(source: Path | None, destination: Path) -> None:
    if source is None:
        from urllib.request import urlopen

        with urlopen(EPHEMERIS_URL) as response, destination.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    else:
        shutil.copyfile(source, destination)
    if destination.stat().st_size != EPHEMERIS_BYTES or sha256(destination) != EPHEMERIS_SHA256:
        destination.unlink()
        raise SystemExit(f"{EPHEMERIS} does not match the recorded NAIF checksum")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="SSAPy data directory containing the real (non-LFS-pointer) files")
    parser.add_argument("--de440s", type=Path, default=None,
                        help=f"local copy of {EPHEMERIS} (default: download from NAIF)")
    args = parser.parse_args(argv)

    problems = []
    for relative, (digest, size) in EXPECTED.items():
        path = args.source / relative
        if not path.is_file():
            problems.append(f"missing: {path}")
        elif path.stat().st_size != size or sha256(path) != digest:
            problems.append(f"checksum mismatch (Git LFS pointer or modified file?): {path}")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1

    TARGET.mkdir(parents=True, exist_ok=True)
    for relative in EXPECTED:
        if relative == DE430_SOURCE:
            continue
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.source / relative, destination)
    subprocess.run(
        [sys.executable, "-m", "jplephem", "excerpt", DE430_START, DE430_END,
         str(args.source / DE430_SOURCE), str(TARGET / DE430_EXCERPT)],
        check=True, stdout=subprocess.DEVNULL,
    )
    fetch_ephemeris(args.de440s, TARGET / EPHEMERIS)
    print(f"Imported {len(EXPECTED) - 1} files, {DE430_EXCERPT} and {EPHEMERIS} into {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
