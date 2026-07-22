#!/usr/bin/env python3
"""Regenerate the SSAPy-Data package manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "src" / "ssapy_data" / "data"
MANIFEST_PATH = ROOT / "src" / "ssapy_data" / "manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def data_entries() -> list[dict[str, str | int]]:
    entries: list[dict[str, str | int]] = []
    for path in sorted(DATA_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(DATA_ROOT).as_posix()
        entries.append(
            {
                "path": relative_path,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return entries


def main() -> int:
    manifest = {
        "schema_version": 1,
        "data_root": "data",
        "generated_by": "scripts/update_manifest.py",
        "files": data_entries(),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)} with {len(manifest['files'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
