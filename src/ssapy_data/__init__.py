"""Packaged data resources for SSAPy and SSAPy Toolkit."""

from __future__ import annotations

from ._manifest import manifest, manifest_entries
from ._resources import (
    DataResourceNotFoundError,
    data_path,
    data_resource,
    iter_data_files,
    open_binary,
    open_text,
    read_binary,
    read_text,
)

__version__ = "0.1.0"

__all__ = [
    "DataResourceNotFoundError",
    "data_path",
    "data_resource",
    "iter_data_files",
    "manifest",
    "manifest_entries",
    "open_binary",
    "open_text",
    "read_binary",
    "read_text",
]
