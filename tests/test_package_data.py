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
    assert data_resource("README.md").is_file()


def test_text_and_binary_read_helpers():
    text = read_text("README.md")
    assert "SSAPy Data Payload Directory" in text
    assert read_binary("README.md").startswith(b"# SSAPy Data")


def test_data_path_yields_filesystem_path():
    with data_path("README.md") as path:
        assert path.exists()
        assert path.name == "README.md"
        assert path.stat().st_size > 0


def test_manifest_matches_packaged_files():
    payload = manifest()
    entries = payload["files"]
    entry_paths = {entry["path"] for entry in entries}
    actual_paths = {resource.name for resource in iter_data_files()}

    assert payload["schema_version"] == 1
    assert payload["data_root"] == "data"
    assert entry_paths == {"README.md"}
    assert actual_paths == {"README.md"}

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
