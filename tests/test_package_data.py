from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ssapy_data import (
    DataResourceNotFoundError,
    data_path,
    data_resource,
    iter_data_files,
    manifest,
    read_binary,
    read_text,
)


def test_known_resources_are_packaged():
    assert data_resource("earth.png").is_file()
    assert data_resource("moon.png").is_file()
    assert data_resource("moon_pa_de440_200625.bpc").is_file()
    assert data_resource("Earth_graphics/ne_50m_ocean.shp").is_file()


def test_text_and_binary_read_helpers():
    assert "Name" in read_text("egm84.egm")
    assert read_binary("earth.png").startswith(b"\x89PNG")


def test_data_path_yields_filesystem_path():
    with data_path("egm96.egm.cof") as path:
        assert path.exists()
        assert path.name == "egm96.egm.cof"
        assert path.stat().st_size > 1_000_000


def test_manifest_matches_packaged_files():
    payload = manifest()
    entries = payload["files"]
    entry_paths = {entry["path"] for entry in entries}
    actual_paths = {resource.name for resource in iter_data_files() if "/" not in resource.name}

    assert payload["schema_version"] == 1
    assert payload["data_root"] == "data"
    assert "earth.png" in entry_paths
    assert "moon_pa_de440_200625.bpc" in entry_paths
    assert {"earth.png", "moon.png", "egm84.egm"}.issubset(actual_paths)

    for entry in entries:
        resource = data_resource(entry["path"])
        with data_path(entry["path"]) as path:
            assert path.stat().st_size == entry["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        assert resource.is_file()


def test_missing_and_unsafe_paths_are_rejected():
    with pytest.raises(DataResourceNotFoundError, match="missing.dat"):
        data_resource("missing.dat")
    with pytest.raises(ValueError, match="must be relative"):
        data_resource("/earth.png")
    with pytest.raises(ValueError, match="cannot contain"):
        data_resource("Earth_graphics/../earth.png")
