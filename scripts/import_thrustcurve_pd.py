#!/usr/bin/env python3
"""Import public-domain ThrustCurve.org motor thrust samples.

This script intentionally imports only records whose API metadata reports
``license == "PD"``. RASP and RockSim files are both normalized to simple
``time_s,thrust_n`` CSV files when the API provides sample pairs. Run it
manually when SSAPy-Data is ready to package a curated motor-curve snapshot,
then run ``scripts/update_manifest.py``.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "src" / "ssapy_data" / "data" / "propulsion" / "thrust_curves" / "solid_motor_pd" / "thrustcurve_org"
API = "https://www.thrustcurve.org/api/v1"
FORMATS = ("RASP", "RockSim")
INDEX_FIELDS = [
    "csv_path",
    "metadata_path",
    "format",
    "manufacturer",
    "manufacturer_abbrev",
    "designation",
    "common_name",
    "motor_id",
    "simfile_id",
    "type",
    "impulse_class",
    "diameter_mm",
    "length_mm",
    "burn_time_s",
    "avg_thrust_n",
    "max_thrust_n",
    "total_impulse_ns",
    "sample_count",
    "sampled_duration_s",
    "sampled_avg_thrust_n",
    "sampled_peak_thrust_n",
    "sampled_total_impulse_ns",
    "license",
    "source",
    "info_url",
    "data_url",
]


def api_get(endpoint: str) -> dict:
    request = Request(API + endpoint, headers={"User-Agent": "SSAPy-Data importer"})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def api_post(endpoint: str, payload: dict) -> dict:
    request = Request(
        API + endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "SSAPy-Data importer"},
    )
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def safe_name(*parts: object) -> str:
    text = "_".join(str(part) for part in parts if part is not None and part != "").lower()
    return "".join(char if char.isalnum() else "_" for char in text).strip("_")


def manufacturer_motors() -> dict[str, dict]:
    motors: dict[str, dict] = {}
    for manufacturer in api_get("/metadata.json")["manufacturers"]:
        result = api_post("/search.json", {"manufacturer": manufacturer["abbrev"], "maxResults": 1000})
        for motor in result.get("results", []):
            if motor.get("dataFiles", 0) > 0:
                motors[motor["motorId"]] = motor
        time.sleep(0.05)
    return motors


def sample_stats(samples: list[dict]) -> dict[str, float]:
    time_values = [float(row["time"]) for row in samples]
    thrust_values = [float(row["thrust"]) for row in samples]
    duration = max(time_values) - min(time_values) if time_values else 0.0
    impulse = (
        sum(
            0.5 * (thrust_values[index] + thrust_values[index - 1])
            * (time_values[index] - time_values[index - 1])
            for index in range(1, len(samples))
        )
        if len(samples) > 1
        else 0.0
    )
    return {
        "sample_count": len(samples),
        "sampled_duration_s": duration,
        "sampled_avg_thrust_n": impulse / duration if duration > 0.0 else 0.0,
        "sampled_peak_thrust_n": max(thrust_values) if thrust_values else 0.0,
        "sampled_total_impulse_ns": impulse,
    }


def import_pd_curves(limit: int | None = None, dry_run: bool = False) -> tuple[int, int]:
    motors = manufacturer_motors()
    motor_ids = list(motors)
    written = 0
    considered = 0
    index_rows: list[dict[str, object]] = []
    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for path in OUT_DIR.glob("*.csv"):
            path.unlink()
        for path in OUT_DIR.glob("*.json"):
            path.unlink()

    for file_format in FORMATS:
        for index in range(0, len(motor_ids), 100):
            response = api_post(
                "/download.json",
                {
                    "motorIds": motor_ids[index : index + 100],
                    "format": file_format,
                    "license": "PD",
                    "data": "samples",
                    "maxResults": 1000,
                },
            )
            for item in response.get("results", []):
                if item.get("license") != "PD" or item.get("format") != file_format:
                    continue
                samples = item.get("samples") or []
                if not samples:
                    continue
                considered += 1
                if dry_run and limit is not None and considered >= limit:
                    return considered, written
                if not dry_run and limit is not None and written >= limit:
                    break
                motor = motors[item["motorId"]]
                stem = safe_name(
                    motor.get("manufacturerAbbrev"),
                    motor.get("designation"),
                    item.get("format"),
                    item.get("simfileId"),
                )
                csv_name = f"{stem}.csv"
                metadata_name = f"{stem}.json"
                stats = sample_stats(samples)
                index_rows.append(
                    {
                        "csv_path": csv_name,
                        "metadata_path": metadata_name,
                        "format": item.get("format"),
                        "manufacturer": motor.get("manufacturer"),
                        "manufacturer_abbrev": motor.get("manufacturerAbbrev"),
                        "designation": motor.get("designation"),
                        "common_name": motor.get("commonName"),
                        "motor_id": motor.get("motorId"),
                        "simfile_id": item.get("simfileId"),
                        "type": motor.get("type"),
                        "impulse_class": motor.get("impulseClass"),
                        "diameter_mm": motor.get("diameter"),
                        "length_mm": motor.get("length"),
                        "burn_time_s": motor.get("burnTimeS"),
                        "avg_thrust_n": motor.get("avgThrustN"),
                        "max_thrust_n": motor.get("maxThrustN"),
                        "total_impulse_ns": motor.get("totImpulseNs"),
                        **stats,
                        "license": item.get("license"),
                        "source": item.get("source"),
                        "info_url": item.get("infoUrl"),
                        "data_url": item.get("dataUrl"),
                    }
                )
                if not dry_run:
                    csv_path = OUT_DIR / csv_name
                    metadata_path = OUT_DIR / metadata_name
                    with csv_path.open("w", newline="", encoding="utf-8") as handle:
                        writer = csv.DictWriter(handle, fieldnames=["time_s", "thrust_n"])
                        writer.writeheader()
                        writer.writerows({"time_s": row["time"], "thrust_n": row["thrust"]} for row in samples)
                    metadata = {
                        "motor": motor,
                        "simfile": {key: value for key, value in item.items() if key != "samples"},
                    }
                    metadata_path.write_text(
                        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                written += 1
            if not dry_run and limit is not None and written >= limit:
                break
            time.sleep(0.05)
    if not dry_run:
        with (OUT_DIR / "index.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=INDEX_FIELDS)
            writer.writeheader()
            writer.writerows(sorted(index_rows, key=lambda row: str(row["csv_path"])))
    return considered, written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="maximum number of curves to write")
    parser.add_argument("--dry-run", action="store_true", help="query sources without writing files")
    args = parser.parse_args()
    considered, written = import_pd_curves(limit=args.limit, dry_run=args.dry_run)
    print(f"considered_pd_files={considered} written={written} output={OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
