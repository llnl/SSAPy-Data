from __future__ import annotations

import hashlib

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
    assert data_resource("README.md").is_file()
    assert data_resource("bright_stars_mag9.csv").is_file()
    assert data_resource("bright_stars_mag11.csv").is_file()
    assert data_resource("earth_day_2048.jpg").is_file()
    assert data_resource("earth_clouds_2048.png").is_file()
    assert data_resource("earth_map.npz").is_file()


def test_text_and_binary_read_helpers():
    text = read_text("README.md")
    assert "SSAPy Data Payload Directory" in text
    assert read_binary("README.md").startswith(b"# SSAPy Data")
    assert read_binary("earth_day_2048.jpg").startswith(b"\xff\xd8")
    assert read_binary("earth_map.npz").startswith(b"PK")


def test_data_path_yields_filesystem_path():
    with data_path("bright_stars_mag9.csv") as path:
        assert path.exists()
        assert path.name == "bright_stars_mag9.csv"
        assert path.stat().st_size > 4_000_000


def test_manifest_matches_packaged_files():
    payload = manifest()
    entries = payload["files"]
    entry_paths = {entry["path"] for entry in entries}
    actual_paths = {resource.name for resource in iter_data_files()}

    assert payload["schema_version"] == 1
    assert payload["data_root"] == "data"
    assert entry_paths == actual_paths
    assert {"README.md", "bright_stars_mag9.csv", "earth_day_2048.jpg", "earth_map.npz"}.issubset(entry_paths)

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
