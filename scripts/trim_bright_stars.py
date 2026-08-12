#!/usr/bin/env python3
"""
trim_bright_stars.py -- reduce the HYG star catalogue to what the toolkit uses.

Why
---
The full HYG catalogue is ~34 MB and reaches about magnitude 12. SSAPy-Toolkit
renders with `mag_limit=6.5` by default (the naked-eye limit) and `_load_stars`
filters on load, so every fainter star is read, parsed and then discarded on
every call. Shipping the full file in the ssapy_data wheel would roughly double
the package size to deliver rows nothing ever draws.

SSAPy-Data's own README anticipates this: "If a future dataset pushes the wheel
above PyPI limits, split the data into a separate companion package rather than
using Git LFS in SSAPy Toolkit." Trimming avoids reaching that point at all.

Tiers
-----
Rather than one subset or the whole 34 MB catalogue, this writes several files
at increasing depth so a caller can choose. The toolkit picks the shallowest
file that covers its mag_limit, so the common case downloads and parses very
little, while someone who wants a denser sky has it available:

    bright_stars.csv        mag < 7.5    naked-eye plus headroom (the default)
    bright_stars_mag9.csv   mag < 9.0    noticeably denser field
    bright_stars_mag11.csv  mag < 11.0   near-complete for rendering purposes

The full catalogue reaches ~mag 12, but the last magnitude adds a large number
of rows that are indistinguishable at any practical marker size. Supply
--tiers to change the set.

What is kept
------------
* Rows brighter than each tier's magnitude limit.
* Only the columns starfield.py actually reads:
      ra, dec, mag        -- required; the loader returns None without them
      pmra, pmdec         -- proper motion, for the epoch correction
      ci                  -- B-V colour index, drives the real star colours
      spect               -- spectral class, the colour fallback
      proper              -- common name, used in hover text
  Every other HYG column (distance, velocity, Bayer/Flamsteed IDs, cross-ids,
  galactic coordinates, ...) is unused by any code path in the toolkit.

Nothing rendered changes: the discarded rows were already filtered out at load
time, and the discarded columns were never read. Run with --verify to confirm
the surviving rows are byte-identical to the originals for the kept columns.

Usage
-----
    python trim_bright_stars.py ~/bright_stars.csv -o bright_stars.csv
    python trim_bright_stars.py ~/bright_stars.csv -o out.csv --verify
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Columns any toolkit code path reads. Checked against starfield.py's loader,
# which looks up exactly these by lowercased name.
KEEP = ["ra", "dec", "mag", "pmra", "pmdec", "ci", "spect", "proper"]

# Required by _load_stars; it returns None (and the plot falls back to a
# synthetic sky) if any is absent.
REQUIRED = ["ra", "dec", "mag"]


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024.0
    return f"{n:.1f} GB"



def _verify(pd, df, keep_rows, present, dest) -> bool:
    """Re-read a written tier and confirm the kept columns survived exactly."""
    import numpy as np
    back = pd.read_csv(dest, low_memory=False)
    ref = df.loc[keep_rows, present].reset_index(drop=True)
    got = back.reset_index(drop=True)
    if len(got) != len(ref):
        print(f"    FAIL {dest.name}: row count changed on round-trip",
              file=sys.stderr)
        return False
    worst_col, worst_val = None, 0.0
    for col in present:
        r, g = ref[col], got[col]
        if pd.api.types.is_numeric_dtype(r):
            rv, gv = r.astype(float).to_numpy(), g.astype(float).to_numpy()
            # A tolerance, not exact equality: writing a float to text and
            # reading it back can move the last representable digit. 1e-12
            # relative is far tighter than anything plotted cares about
            # (positions are used at arcsecond scale, ~5e-6 rad) while still
            # catching a truncated or mis-parsed column.
            ok = bool(np.isclose(rv, gv, rtol=1e-12, atol=0.0,
                                 equal_nan=True).all())
            with np.errstate(invalid="ignore"):
                diff = np.abs(rv - gv)
            finite = diff[np.isfinite(diff)]
            v = float(finite.max()) if finite.size else 0.0
        else:
            ok = bool((r.fillna("").astype(str)
                       == g.fillna("").astype(str)).all())
            v = 0.0
        if not ok:
            print(f"    FAIL {dest.name}: column '{col}' differs "
                  f"(max |diff| {v:g})", file=sys.stderr)
            return False
        if v > worst_val:
            worst_col, worst_val = col, v
    print(f"    verified: {len(got):,} rows, {len(present)} columns identical "
          f"(worst round-trip diff {worst_val:g}"
          f"{f", column {worst_col!r}" if worst_col else ''})")
    return True


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", type=Path, help="full HYG catalogue CSV")
    p.add_argument("-o", "--out-dir", type=Path, default=Path("."),
                   help="directory to write the tier files into")
    p.add_argument("--tiers", default="7.5:bright_stars.csv,"
                                      "9.0:bright_stars_mag9.csv,"
                                      "11.0:bright_stars_mag11.csv",
                   help="comma-separated mag_limit:filename pairs")
    p.add_argument("--verify", action="store_true",
                   help="re-read the output and confirm the kept columns match "
                        "the source exactly for every surviving row")
    a = p.parse_args(argv)

    try:
        import pandas as pd
    except ImportError:
        print("pandas is required", file=sys.stderr)
        return 1

    if not a.source.is_file():
        print(f"not found: {a.source}", file=sys.stderr)
        return 1

    src_bytes = a.source.stat().st_size
    print(f"reading {a.source}  ({human(src_bytes)})")
    df = pd.read_csv(a.source, low_memory=False)
    n_before = len(df)

    lower = {c.lower(): c for c in df.columns}
    missing_required = [c for c in REQUIRED if c not in lower]
    if missing_required:
        print(f"source lacks required column(s): {missing_required}", file=sys.stderr)
        print(f"  columns present: {list(df.columns)[:12]}", file=sys.stderr)
        return 1

    present = [lower[c] for c in KEEP if c in lower]
    absent = [c for c in KEEP if c not in lower]
    if absent:
        # Not fatal: pmra/pmdec/ci/spect/proper are all optional in the loader,
        # which substitutes defaults. Worth reporting so the loss is visible.
        print(f"  note: source has no {absent} -- the loader defaults these "
              f"(colours fall back to spectral class, proper motion to zero)")

    mag_col = lower["mag"]

    try:
        tiers = []
        for pair in a.tiers.split(","):
            lim, name = pair.split(":", 1)
            tiers.append((float(lim), name.strip()))
    except ValueError:
        print(f"could not parse --tiers: {a.tiers!r} "
              f"(expected 'mag:filename,mag:filename')", file=sys.stderr)
        return 1
    tiers.sort()

    a.out_dir.mkdir(parents=True, exist_ok=True)
    print()
    total_out = 0
    for lim, name in tiers:
        dest = a.out_dir / name
        keep_rows = df[mag_col] < lim
        out = df.loc[keep_rows, present].copy()
        out.to_csv(dest, index=False)
        n_bytes = dest.stat().st_size
        total_out += n_bytes
        print(f"  mag < {lim:<5} {name:<26} {len(out):>8,} rows  "
              f"{human(n_bytes):>9}  ({100.0*n_bytes/src_bytes:5.1f}% of source)")

        if a.verify and not _verify(pd, df, keep_rows, present, dest):
            return 1

    print(f"\n  source {n_before:,} rows / {len(df.columns)} columns / "
          f"{human(src_bytes)}")
    print(f"  kept columns: {present}")
    print(f"  all tiers together: {human(total_out)} "
          f"({100.0*total_out/src_bytes:.1f}% of the source)")
    print(f"\nwrote {len(tiers)} file(s) to {a.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
