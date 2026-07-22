"""Manifest helpers for packaged SSAPy data."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

PACKAGE = "ssapy_data"
MANIFEST_NAME = "manifest.json"


def manifest() -> dict[str, Any]:
    """Return the packaged data manifest."""

    resource = files(PACKAGE).joinpath(MANIFEST_NAME)
    return json.loads(resource.read_text(encoding="utf-8"))


def manifest_entries() -> list[dict[str, Any]]:
    """Return file entries from the packaged data manifest."""

    return list(manifest()["files"])
