from __future__ import annotations

import csv
import fnmatch
import hashlib
import json

import pytest

from ssapy_data import (
    DataResourceNotFoundError,
    data_path,
    data_resource,
    iter_data_files,
    manifest,
    open_text,
    read_binary,
    read_text,
)


def test_known_resources_are_packaged():
    assert data_resource("README.md").is_file()
    assert data_resource("sources.json").is_file()
    assert data_resource("bright_stars_mag9.csv").is_file()
    assert data_resource("bright_stars_mag11.csv").is_file()
    assert data_resource("earth_day_2048.jpg").is_file()
    assert data_resource("earth_clouds_2048.png").is_file()
    assert data_resource("earth_map.npz").is_file()
    assert data_resource("propulsion/throttle_maps/electric/next_tt10_thrust_comparison.csv").is_file()
    assert data_resource("propulsion/throttle_maps/electric/hermes_tdu3_throttle_map.csv").is_file()
    assert data_resource("propulsion/throttle_maps/electric/aeps_etu2_throttle_map.csv").is_file()
    assert data_resource("propulsion/throttle_maps/electric/spt140_performance_map.csv").is_file()


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
    actual_count = sum(1 for _ in iter_data_files())

    assert payload["schema_version"] == 1
    assert payload["data_root"] == "data"
    assert len(entry_paths) == actual_count
    assert {"README.md", "bright_stars_mag9.csv", "earth_day_2048.jpg", "earth_map.npz"}.issubset(entry_paths)
    assert {
        "propulsion/README.md",
        "propulsion/source_audit.md",
        "propulsion/sources.json",
        "propulsion/thrust_curves/digitized/nasa_ntrs/README.md",
        "propulsion/thrust_curves/digitized/nasa_ntrs/index.csv",
        "propulsion/thrust_curves/solid_motor_pd/thrustcurve_org/index.csv",
        "propulsion/throttle_maps/electric/next_tt10_thrust_comparison.csv",
        "propulsion/throttle_maps/electric/hermes_tdu3_throttle_map.csv",
        "propulsion/throttle_maps/electric/aeps_etu2_throttle_map.csv",
        "propulsion/throttle_maps/electric/spt140_performance_map.csv",
    }.issubset(entry_paths)

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


def test_thrustcurve_public_domain_index_is_packaged():
    with open_text("propulsion/thrust_curves/solid_motor_pd/thrustcurve_org/index.csv") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 596
    assert {row["license"] for row in rows} == {"PD"}
    assert {row["format"] for row in rows} == {"RASP", "RockSim"}

    first = rows[0]
    csv_resource = f"propulsion/thrust_curves/solid_motor_pd/thrustcurve_org/{first['csv_path']}"
    metadata_resource = f"propulsion/thrust_curves/solid_motor_pd/thrustcurve_org/{first['metadata_path']}"
    assert read_text(csv_resource).startswith("time_s,thrust_n")
    metadata = json.loads(read_text(metadata_resource))
    assert metadata["simfile"]["license"] == "PD"
    assert str(metadata["simfile"]["simfileId"]) == first["simfile_id"]


def test_aeps_etu2_throttle_map_is_packaged():
    with open_text("propulsion/throttle_maps/electric/aeps_etu2_throttle_map.csv") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 12
    assert {row["dataset"] for row in rows} == {"nominal_aeps_rfc", "ppe_aeps_rfc"}
    assert {float(row["thrust_tolerance_mn"]) for row in rows} == {5.0}
    assert any(
        row["dataset"] == "ppe_aeps_rfc"
        and row["discharge_voltage_v"] == "600"
        and row["cathode_flow_fraction_percent"] == "14"
        and row["average_thrust_mn"] == "594"
        for row in rows
    )


def test_propulsion_sources_include_packaged_tables():
    sources = json.loads(read_text("propulsion/sources.json"))["sources"]
    by_id = {source["id"]: source for source in sources}

    assert "nasa_aeps_etu2_performance" in by_id
    assert "propulsion/throttle_maps/electric/aeps_etu2_throttle_map.csv" in by_id[
        "nasa_aeps_etu2_performance"
    ]["packaged_files"]
    assert by_id["nasa_aeps_etu2_performance"]["distribution"] == "PUBLIC"
    assert by_id["nasa_aeps_etu2_performance"]["export_control"] == "NO ITAR, NO EAR"
    assert "propulsion/throttle_maps/electric/spt140_performance_map.csv" in by_id[
        "nasa_spt140_performance"
    ]["packaged_files"]


def test_spt140_performance_map_is_packaged():
    with open_text("propulsion/throttle_maps/electric/spt140_performance_map.csv") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 26
    assert {row["dataset"] for row in rows} == {"nasa_lerc_1997", "fakel_1997"}
    assert min(float(row["thrust_mn"]) for row in rows) == 87.0
    assert max(float(row["thrust_mn"]) for row in rows) == 287.0
    assert any(
        row["dataset"] == "nasa_lerc_1997"
        and row["discharge_voltage_v"] == "399"
        and row["specific_impulse_s"] == "1929"
        for row in rows
    )


def test_digitized_nasa_ntrs_thrust_curves_are_packaged():
    with open_text("propulsion/thrust_curves/digitized/nasa_ntrs/index.csv") as handle:
        index_rows = list(csv.DictReader(handle))

    assert len(index_rows) == 3
    assert {row["ntrs_id"] for row in index_rows} == {
        "19730015083",
        "19900003335",
        "20090026004",
    }
    assert {row["distribution"] for row in index_rows} == {"PUBLIC"}

    for row in index_rows:
        csv_resource = f"propulsion/thrust_curves/digitized/nasa_ntrs/{row['csv_path']}"
        metadata_resource = f"propulsion/thrust_curves/digitized/nasa_ntrs/{row['metadata_path']}"
        metadata = json.loads(read_text(metadata_resource))
        assert metadata["source"]["ntrs_id"] == row["ntrs_id"]
        assert metadata["source"]["export_control"] == "NO ITAR, NO EAR"
        assert metadata["digitization"]["method"].startswith("Manual curve digitization")

        with open_text(csv_resource) as handle:
            curve_rows = list(csv.DictReader(handle))
        assert curve_rows
        times = [float(curve_row["time_s"]) for curve_row in curve_rows]
        assert times == sorted(times)

        if "thrust_lbf" in curve_rows[0]:
            thrust_lbf = [float(curve_row["thrust_lbf"]) for curve_row in curve_rows]
            thrust_n = [float(curve_row["thrust_n"]) for curve_row in curve_rows]
            assert min(thrust_lbf) >= 0.0
            assert max(thrust_lbf) > 0.0
            assert min(thrust_n) >= 0.0
        else:
            measured = [float(curve_row["measured_fraction_steady_state"]) for curve_row in curve_rows]
            filtered = [float(curve_row["filtered_fraction_steady_state"]) for curve_row in curve_rows]
            assert max(measured) > 1.0
            assert min(filtered) >= -0.2


def test_root_sources_cite_packaged_non_document_data():
    source_payload = json.loads(read_text("sources.json"))
    propulsion_payload = json.loads(read_text("propulsion/sources.json"))
    root_patterns = [
        pattern
        for source in source_payload["sources"]
        for pattern in source.get("packaged_files", [])
    ]
    propulsion_patterns = [
        pattern
        for source in propulsion_payload["sources"]
        for pattern in source.get("packaged_files", [])
    ]

    assert "bright_stars.csv" in root_patterns
    assert "propulsion/**" in root_patterns
    assert "propulsion/thrust_curves/digitized/nasa_ntrs/*.csv" in propulsion_patterns

    uncited = []
    for entry in manifest()["files"]:
        path = entry["path"]
        if (
            path.endswith("README.md")
            or path.endswith("source_audit.md")
            or path.endswith("sources.json")
        ):
            continue
        patterns = propulsion_patterns if path.startswith("propulsion/") else root_patterns
        if not any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns):
            uncited.append(path)

    assert uncited == []
