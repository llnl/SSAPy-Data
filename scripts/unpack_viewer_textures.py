#!/usr/bin/env python3
"""
unpack_viewer_textures.py -- split satellite_viewer_textures.npz into files.

Why
---
The four Earth textures used by the Three.js satellite viewer shipped bundled
in a single .npz holding raw encoded image bytes (plus a "<key>_ext" array per
texture recording its extension). That was chosen to match earth_map.npz's
convention and to avoid needing an image library at build time.

Both reasons have lapsed: earth_map.npz is being dropped (its 512x1024
classification raster is too coarse to use), and no image library is needed to
write the files either -- the archive already holds encoded JPEG/PNG bytes, so
unpacking is a byte copy.

Unpacking is worth doing because:

  * Every other asset in SSAPy-Data is a plain, individually named file with
    its own manifest entry and sha256. A bundle hides four assets behind one
    checksum, so a corrupted texture cannot be identified.
  * Bundled, only the viewer can read them. As ordinary images the other plot
    modules can use the night and cloud layers too, which is the whole reason
    the viewer's output looks better than the static plots.
  * load_textures() gets simpler: base64-encoding a file's bytes directly,
    with no numpy round-trip.

Naming
------
The viewer's textures are 2048x1024, sized for a GPU and to keep the inlined
base64 HTML manageable. SSAPy-Data separately holds earth.png at 5400x2700 for
the matplotlib/Plotly plots. These are different assets, not duplicates, so the
output names carry the resolution to make "which Earth texture" unambiguous:

    earth_day_2048.jpg
    earth_night_2048.jpg
    earth_specular_2048.jpg
    earth_clouds_2048.png

Usage
-----
    python unpack_viewer_textures.py path/to/satellite_viewer_textures.npz \\
        -o path/to/SSAPy-Data/src/ssapy_data/data --verify
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

KEYS = ("day", "night", "specular", "clouds")

# Output name per texture key. The extension is taken from the archive's
# "<key>_ext" entry rather than hardcoded, so a re-encoded archive (say, clouds
# switched from PNG to WEBP) still produces a correctly-named file.
STEMS = {
    "day": "earth_day_2048",
    "night": "earth_night_2048",
    "specular": "earth_specular_2048",
    "clouds": "earth_clouds_2048",
}


def human(n: float) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} MB"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archive", type=Path, help="satellite_viewer_textures.npz")
    p.add_argument("-o", "--out-dir", type=Path, default=Path("."))
    p.add_argument("--verify", action="store_true",
                   help="re-read each written file and confirm the bytes match "
                        "the archive exactly")
    a = p.parse_args(argv)

    try:
        import numpy as np
    except ImportError:
        print("numpy is required to read the archive", file=sys.stderr)
        return 1

    if not a.archive.is_file():
        print(f"not found: {a.archive}", file=sys.stderr)
        return 1

    a.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"reading {a.archive}  ({human(a.archive.stat().st_size)})\n")

    written = []
    with np.load(a.archive) as z:
        missing = [k for k in KEYS if k not in z.files]
        if missing:
            print(f"archive lacks texture(s): {missing}", file=sys.stderr)
            print(f"  keys present: {z.files}", file=sys.stderr)
            return 1

        for key in KEYS:
            raw = z[key].tobytes()

            ext_key = f"{key}_ext"
            if ext_key in z.files:
                ext = bytes(z[ext_key]).decode("ascii", "replace").strip()
            else:
                # Fall back to sniffing the magic bytes rather than guessing.
                ext = (".png" if raw[:8] == b"\x89PNG\r\n\x1a\n"
                       else ".jpg" if raw[:2] == b"\xff\xd8"
                       else ".bin")
                print(f"  note: no {ext_key} in archive; inferred {ext} "
                      f"from the file signature")
            if not ext.startswith("."):
                ext = "." + ext

            dest = a.out_dir / (STEMS[key] + ext)
            dest.write_bytes(raw)
            written.append((key, dest, len(raw)))
            print(f"  {key:9s} -> {dest.name:28s} {human(len(raw)):>9}")

            if a.verify:
                back = dest.read_bytes()
                if back != raw:
                    print(f"    FAIL: {dest.name} differs from the archive "
                          f"({len(back)} vs {len(raw)} bytes)", file=sys.stderr)
                    return 1

    if a.verify:
        print(f"\n  verified: all {len(written)} files byte-identical to the "
              f"archive")

    total = sum(n for _, _, n in written)
    print(f"\nwrote {len(written)} file(s), {human(total)} total, to {a.out_dir}")
    print("\nNext: update load_textures() in build_satellite_viewer.py to read "
          "these\n      individually, then re-run scripts/update_manifest.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
