"""Resource helpers for data packaged in ``ssapy_data`` wheels."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import as_file, files
try:
    from importlib.resources.abc import Traversable
except ImportError:  # Python 3.10
    from importlib.abc import Traversable
from os import PathLike
from pathlib import Path, PurePosixPath
from typing import Iterator

DATA_ROOT = "data"
PACKAGE = "ssapy_data"


class DataResourceNotFoundError(FileNotFoundError):
    """Raised when a requested packaged data resource is absent."""


def data_resource(
    relative_path: str | PathLike[str] = "",
    *,
    data_root: str | PathLike[str] = DATA_ROOT,
    must_exist: bool = True,
) -> Traversable:
    """Return an ``importlib.resources`` object for packaged SSAPy data.

    Parameters
    ----------
    relative_path
        POSIX-style path below ``data_root``. Absolute paths and ``..`` traversal
        are rejected.
    data_root
        Directory inside ``ssapy_data`` that contains data resources.
    must_exist
        If ``True``, raise :class:`DataResourceNotFoundError` when the resource
        is missing.
    """

    resource = files(PACKAGE)
    for part in _safe_parts(data_root):
        resource = resource.joinpath(part)
    for part in _safe_parts(relative_path):
        resource = resource.joinpath(part)

    if must_exist and not resource.exists():
        requested = _display_path(data_root, relative_path)
        raise DataResourceNotFoundError(
            f"Data resource '{requested}' was not found in package '{PACKAGE}'."
        )

    return resource


@contextmanager
def data_path(
    relative_path: str | PathLike[str],
    *,
    data_root: str | PathLike[str] = DATA_ROOT,
) -> Iterator[Path]:
    """Yield a filesystem path for a packaged data file.

    Use this when a downstream library requires a real path instead of a file
    object. The yielded path may be a temporary extraction path for zipped wheels,
    so callers should use it only inside the context manager.
    """

    resource = data_resource(relative_path, data_root=data_root)
    if not resource.is_file():
        requested = _display_path(data_root, relative_path)
        raise DataResourceNotFoundError(f"Data resource '{requested}' is not a file.")

    with as_file(resource) as path:
        yield path


@contextmanager
def open_binary(relative_path: str | PathLike[str], *, data_root: str | PathLike[str] = DATA_ROOT):
    """Open a packaged data file in binary mode."""

    resource = data_resource(relative_path, data_root=data_root)
    if not resource.is_file():
        requested = _display_path(data_root, relative_path)
        raise DataResourceNotFoundError(f"Data resource '{requested}' is not a file.")

    with resource.open("rb") as file_handle:
        yield file_handle


@contextmanager
def open_text(
    relative_path: str | PathLike[str],
    *,
    data_root: str | PathLike[str] = DATA_ROOT,
    encoding: str = "utf-8",
):
    """Open a packaged data file in text mode."""

    resource = data_resource(relative_path, data_root=data_root)
    if not resource.is_file():
        requested = _display_path(data_root, relative_path)
        raise DataResourceNotFoundError(f"Data resource '{requested}' is not a file.")

    with resource.open("r", encoding=encoding) as file_handle:
        yield file_handle


def read_binary(relative_path: str | PathLike[str], *, data_root: str | PathLike[str] = DATA_ROOT) -> bytes:
    """Read a packaged binary data file."""

    with open_binary(relative_path, data_root=data_root) as file_handle:
        return file_handle.read()


def read_text(
    relative_path: str | PathLike[str],
    *,
    data_root: str | PathLike[str] = DATA_ROOT,
    encoding: str = "utf-8",
) -> str:
    """Read a packaged text data file."""

    with open_text(relative_path, data_root=data_root, encoding=encoding) as file_handle:
        return file_handle.read()


def iter_data_files(relative_path: str | PathLike[str] = "") -> Iterator[Traversable]:
    """Yield packaged data files recursively below ``relative_path``."""

    root = data_resource(relative_path)
    if root.is_file():
        yield root
        return

    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_file():
            yield child
        elif child.is_dir():
            child_relative = _display_path(relative_path, child.name)
            yield from iter_data_files(child_relative)


def _safe_parts(path: str | PathLike[str]) -> tuple[str, ...]:
    path_string = str(path)
    if path_string in {"", "."}:
        return ()

    pure_path = PurePosixPath(path_string)
    if pure_path.is_absolute():
        raise ValueError(f"Packaged data paths must be relative, got '{path_string}'.")

    parts = tuple(part for part in pure_path.parts if part not in {"", "."})
    if ".." in parts:
        raise ValueError(f"Packaged data paths cannot contain '..', got '{path_string}'.")
    return parts


def _display_path(*paths: str | PathLike[str]) -> str:
    parts: list[str] = []
    for path in paths:
        parts.extend(_safe_parts(path))
    return "/".join(parts)
