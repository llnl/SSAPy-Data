#!/usr/bin/env python3
"""Write curated thrust curves digitized from public NASA NTRS plots.

The package does not redistribute source PDFs or plot images. This maintainer
script stores the calibrated curve points used to produce the normalized CSV
files and sidecar metadata. Points were extracted with a WebPlotDigitizer-style
manual workflow: render the public/export-clear NTRS PDF page, calibrate the
plot axes, trace the curve, and record the calibrated values here.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

LBF_TO_N = 4.4482216152605

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = (
    ROOT
    / "src"
    / "ssapy_data"
    / "data"
    / "propulsion"
    / "thrust_curves"
    / "digitized"
    / "nasa_ntrs"
)


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _trapezoid(x: list[float], y: list[float]) -> float:
    return sum(0.5 * (y[i] + y[i - 1]) * (x[i] - x[i - 1]) for i in range(1, len(x)))


def _force_rows(points: list[tuple[float, float]]) -> list[dict[str, object]]:
    rows = []
    for time_s, thrust_lbf in points:
        rows.append(
            {
                "time_s": f"{time_s:.3f}",
                "thrust_lbf": f"{thrust_lbf:.3f}",
                "thrust_n": f"{thrust_lbf * LBF_TO_N:.6f}",
            }
        )
    return rows


def te_m_521_5() -> tuple[str, list[dict[str, object]], dict]:
    points = [
        (0.00, 0.0),
        (0.15, 3200.0),
        (0.40, 3500.0),
        (1.00, 3400.0),
        (2.00, 3200.0),
        (4.00, 2900.0),
        (5.00, 2700.0),
        (6.00, 2600.0),
        (8.00, 2750.0),
        (10.00, 2950.0),
        (12.00, 3150.0),
        (13.00, 3250.0),
        (14.00, 3300.0),
        (15.00, 3300.0),
        (16.00, 3260.0),
        (17.00, 3200.0),
        (18.00, 3160.0),
        (19.00, 3100.0),
        (19.50, 3000.0),
        (19.90, 2800.0),
        (20.10, 600.0),
        (20.30, 0.0),
    ]
    time = [p[0] for p in points]
    thrust = [p[1] for p in points]
    rows = _force_rows(points)
    metadata = {
        "schema_version": 1,
        "title": "TE-M-521-5 apogee kick motor axial thrust curve, digitized from Fig. 7",
        "source": {
            "ntrs_id": "19730015083",
            "title": "Design assurance test of the Thiokol Te-M-521-5 apogee kick motor tested in the spin mode at simulated altitude conditions",
            "url": "https://ntrs.nasa.gov/citations/19730015083",
            "figure": "Figure 7, Variation of Thrust, Chamber Pressure, and Test Cell Pressure during Firing",
            "distribution": "PUBLIC",
            "export_control": "NO ITAR, NO EAR",
            "rights": "GOV_PUBLIC_USE_PERMITTED",
            "retrieved": "2026-08-22",
        },
        "digitization": {
            "method": "Manual curve digitization from a 250 dpi rendered PDF page using calibrated plot axes.",
            "curve": "Current test axial thrust curve, T=40 deg F, spin=46 rpm.",
            "estimated_uncertainty": {
                "time_s": 0.15,
                "thrust_lbf": 150.0,
                "notes": "Aged scan, skew, symbols, labels, and overlapping pressure traces limit precision.",
            },
        },
        "columns": {
            "time_s": "Time after ignition in seconds.",
            "thrust_lbf": "Digitized axial thrust in pounds-force from the source figure.",
            "thrust_n": "Digitized axial thrust converted with 1 lbf = 4.4482216152605 N.",
        },
        "validation": {
            "integrated_digitized_impulse_lbf_s": round(_trapezoid(time, thrust), 3),
            "published_context": "Report text gives vacuum total impulse of 71,469 lbf-s; this CSV digitizes plotted axial thrust, not the vacuum-corrected total impulse.",
        },
    }
    return "ntrs_19730015083_te_m_521_5_axial_thrust_digitized", rows, metadata


def rsrm_3b() -> tuple[str, list[dict[str, object]], dict]:
    points = [
        (0.0, 0.0),
        (0.5, 2_950_000.0),
        (1.0, 3_100_000.0),
        (5.0, 3_180_000.0),
        (10.0, 3_260_000.0),
        (15.0, 3_280_000.0),
        (20.0, 3_310_000.0),
        (22.0, 3_310_000.0),
        (25.0, 3_150_000.0),
        (30.0, 2_950_000.0),
        (35.0, 2_800_000.0),
        (40.0, 2_650_000.0),
        (45.0, 2_550_000.0),
        (50.0, 2_400_000.0),
        (55.0, 2_380_000.0),
        (60.0, 2_450_000.0),
        (65.0, 2_500_000.0),
        (70.0, 2_560_000.0),
        (75.0, 2_580_000.0),
        (80.0, 2_580_000.0),
        (85.0, 2_420_000.0),
        (90.0, 2_200_000.0),
        (95.0, 2_080_000.0),
        (100.0, 1_980_000.0),
        (105.0, 1_850_000.0),
        (110.0, 1_700_000.0),
        (112.0, 1_500_000.0),
        (115.0, 800_000.0),
        (118.0, 350_000.0),
        (120.0, 250_000.0),
        (123.0, 120_000.0),
        (125.0, 60_000.0),
        (128.0, 10_000.0),
        (130.0, 0.0),
    ]
    time = [p[0] for p in points]
    thrust = [p[1] for p in points]
    rows = _force_rows(points)
    metadata = {
        "schema_version": 1,
        "title": "RSRM-3B reconstructed vacuum thrust-time trace, digitized from Fig. 2.1",
        "source": {
            "ntrs_id": "19900003335",
            "title": "RSRM-3 (360L003) Ballistics/Mass Properties Report",
            "url": "https://ntrs.nasa.gov/citations/19900003335",
            "figure": "Figure 2.1, RSRM-3A and 3B Reconstructed Vacuum Thrust-Time Trace at Delivered Conditions",
            "distribution": "PUBLIC",
            "export_control": "NO ITAR, NO EAR",
            "rights": "GOV_PUBLIC_USE_PERMITTED",
            "retrieved": "2026-08-22",
        },
        "digitization": {
            "method": "Manual curve digitization from a 250 dpi rendered PDF page using calibrated plot axes.",
            "curve": "Solid RSRM-3B trace.",
            "estimated_uncertainty": {
                "time_s": 1.0,
                "thrust_lbf": 50_000.0,
                "notes": "Scan skew, thick gridlines, legend overlap near 10-50 s, and overplotted RSRM-3A/3B traces limit precision.",
            },
        },
        "columns": {
            "time_s": "Time in seconds from the source figure.",
            "thrust_lbf": "Digitized reconstructed vacuum thrust in pounds-force.",
            "thrust_n": "Digitized reconstructed vacuum thrust converted with 1 lbf = 4.4482216152605 N.",
        },
        "validation": {
            "integrated_digitized_impulse_lbf_s": round(_trapezoid(time, thrust), 3),
            "published_standard_nominal_impulse_gates_lbf_s": {
                "20_s": 64.5e6,
                "60_s": 172.5e6,
                "action_time": 296.3e6,
            },
            "notes": "Integrated digitized curve is close to the report's standard-nominal impulse gates, but the plot is delivered-condition reconstructed thrust.",
        },
    }
    return "ntrs_19900003335_rsrm_3b_reconstructed_vacuum_thrust_digitized", rows, metadata


def rs18_startup() -> tuple[str, list[dict[str, object]], dict]:
    points = [
        (0.20, 0.02, 0.00),
        (0.23, 0.01, -0.15),
        (0.25, 0.05, 0.15),
        (0.265, 0.20, 0.50),
        (0.275, 2.40, 2.00),
        (0.285, 1.10, 1.35),
        (0.300, 1.45, 1.10),
        (0.320, 1.05, 1.00),
        (0.350, 0.90, 0.92),
        (0.380, 1.10, 1.05),
        (0.400, 0.95, 0.94),
        (0.440, 1.02, 1.02),
        (0.480, 0.98, 0.98),
        (0.520, 1.02, 1.01),
        (0.600, 1.00, 1.00),
        (0.700, 1.00, 1.00),
        (0.800, 1.00, 1.00),
        (0.900, 0.99, 0.99),
        (0.975, 0.98, 0.98),
        (1.000, 0.50, 0.65),
        (1.020, 0.22, 0.20),
        (1.060, 0.20, 0.15),
        (1.100, 0.12, 0.08),
        (1.160, 0.08, 0.03),
        (1.200, 0.06, 0.00),
    ]
    rows = []
    for time_s, measured_fraction, filtered_fraction in points:
        rows.append(
            {
                "time_s": f"{time_s:.3f}",
                "measured_fraction_steady_state": f"{measured_fraction:.4f}",
                "filtered_fraction_steady_state": f"{filtered_fraction:.4f}",
                "measured_percent_steady_state": f"{100.0 * measured_fraction:.2f}",
                "filtered_percent_steady_state": f"{100.0 * filtered_fraction:.2f}",
            }
        )
    metadata = {
        "schema_version": 1,
        "title": "RS-18 LOX/LCH4 startup and shutdown normalized thrust shape, digitized from Fig. 8",
        "source": {
            "ntrs_id": "20090026004",
            "title": "Liquid Oxygen/Liquid Methane Test Results of the RS-18 Lunar Ascent Engine at Simulated Altitude Conditions at NASA White Sands Test Facility",
            "url": "https://ntrs.nasa.gov/citations/20090026004",
            "figure": "Figure 8, Example non-dimensionalized thrust output from RS-18 test",
            "distribution": "PUBLIC",
            "export_control": "NO ITAR, NO EAR",
            "rights": "GOV_PUBLIC_USE_PERMITTED",
            "retrieved": "2026-08-22",
        },
        "digitization": {
            "method": "Manual curve digitization from a 250 dpi rendered PDF page using calibrated plot axes.",
            "curves": [
                "Measured thrust, normalized to steady state and read from the left axis.",
                "Filtered thrust, normalized to steady state and read from the right axis.",
            ],
            "estimated_uncertainty": {
                "time_s": 0.01,
                "fraction_steady_state": 0.03,
                "notes": "Source figure is color and clear, but high-frequency measured oscillations are under-sampled by this compact CSV.",
            },
        },
        "columns": {
            "time_s": "Time in seconds.",
            "measured_fraction_steady_state": "Measured thrust divided by steady-state thrust.",
            "filtered_fraction_steady_state": "Filtered thrust divided by steady-state thrust.",
            "measured_percent_steady_state": "Measured thrust in percent of steady-state thrust.",
            "filtered_percent_steady_state": "Filtered thrust in percent of steady-state thrust.",
        },
        "validation": {
            "published_context": "Report text states valve-open-command to 90% full-thrust response was about 0.28 s and repeatable over 0.25-0.28 s.",
            "notes": "This is a normalized shape curve. Scale it by a chosen steady-state thrust before use as an absolute thrust-time curve.",
        },
    }
    return "ntrs_20090026004_rs18_startup_normalized_thrust_digitized", rows, metadata


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for stem, rows, metadata in (te_m_521_5(), rsrm_3b(), rs18_startup()):
        csv_name = f"{stem}.csv"
        metadata_name = f"{stem}.json"
        _write_csv(OUT_DIR / csv_name, rows, list(rows[0].keys()))
        _write_json(OUT_DIR / metadata_name, metadata)
        index_rows.append(
            {
                "csv_path": csv_name,
                "metadata_path": metadata_name,
                "ntrs_id": metadata["source"]["ntrs_id"],
                "title": metadata["title"],
                "source_figure": metadata["source"]["figure"],
                "distribution": metadata["source"]["distribution"],
                "rights": metadata["source"]["rights"],
                "method": metadata["digitization"]["method"],
            }
        )
    _write_csv(
        OUT_DIR / "index.csv",
        index_rows,
        [
            "csv_path",
            "metadata_path",
            "ntrs_id",
            "title",
            "source_figure",
            "distribution",
            "rights",
            "method",
        ],
    )
    print(f"Wrote {len(index_rows)} digitized curve dataset(s) to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
