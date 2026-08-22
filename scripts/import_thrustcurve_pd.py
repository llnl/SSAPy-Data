#!/usr/bin/env python3
"""Import public-domain ThrustCurve.org motor thrust samples.

This script intentionally imports only records whose API metadata reports
``license == "PD"``. Run it manually when SSAPy-Data is ready to package a
curated motor-curve snapshot, then run ``scripts/update_manifest.py``.
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


def import_pd_curves(limit: int | None = None, dry_run: bool = False) -> tuple[int, int]:
    motors = manufacturer_motors()
    motor_ids = list(motors)
    written = 0
    considered = 0
    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    for index in range(0, len(motor_ids), 100):
        response = api_post(
            "/download.json",
            {
                "motorIds": motor_ids[index : index + 100],
                "format": "RASP",
                "license": "PD",
                "data": "samples",
                "maxResults": 1000,
            },
        )
        for item in response.get("results", []):
            if item.get("license") != "PD" or item.get("format") != "RASP":
                continue
            samples = item.get("samples") or []
            if not samples:
                continue
            considered += 1
            if dry_run and limit is not None and considered >= limit:
                return considered, written
            if not dry_run and limit is not None and written >= limit:
                return considered, written
            motor = motors[item["motorId"]]
            stem = safe_name(motor.get("manufacturerAbbrev"), motor.get("designation"), item.get("simfileId"))
            if not dry_run:
                csv_path = OUT_DIR / f"{stem}.csv"
                metadata_path = OUT_DIR / f"{stem}.json"
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
        time.sleep(0.05)
    return considered, written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="maximum number of curves to write")
    parser.add_argument("--dry-run", action="store_true", help="query sources without writing files")
    args = parser.parse_args()
    considered, written = import_pd_curves(limit=args.limit, dry_run=args.dry_run)
    print(f"considered_pd_rasp={considered} written={written} output={OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
