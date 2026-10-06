# Report fixes: data provenance and integrity

Apply this overlay to the complete SSAPy-Data checkout. The orbital values in `src/ssapy_data/data/ssapy_satellites_default.json` remain a **historical snapshot of 152 unique NORAD records**. Metadata corrections do not refresh its TLEs.

| Snapshot field | Meaning |
| --- | --- |
| Earliest TLE epoch | 2025-10-27T14:19:01.946784Z |
| Latest TLE epoch | 2026-07-20T14:43:33.944448Z |
| Copy into SSAPy-Data | 2026-09-28 |
| Original Space-Track fetch date | Unknown; recorded as `null` |

The ledger's `retrieved` date describes the package copy, not a Space-Track fetch. Use this snapshot for reproducible historical examples. Refresh and revalidate appropriate elements before current-time tracking or coverage analysis; the Toolkit coverage CLI now checks TLE age and requires explicit opt-in for stale demonstrations. Length, prefix, field, checksum, and uniqueness checks establish file structure, not physical accuracy.

## Redistribution and benchmark provenance

`src/ssapy_data/data/sources.json` records the [Space-Track basic SSA redistribution policy](https://www.space-track.org/documentation#/odr), including the appropriate-citation condition and USSPACECOM attribution. Its scope is the basic TLE records in this snapshot. Preserve that attribution when redistributing them; the entry makes no authorization claim for advanced or emergency SSA products. The original snapshot fetch provenance remains unresolved.

Benchmark ledger entries now separate `benchmarks/long_term/` from `benchmarks/nbody/`. The long-term entry describes the recorded Earth-centered degree/order-0 comparison; its cislunar-radius case is not evidence of a full Earth-Moon-Sun model. The nbody entry marks its reference force model as **pending verification**. Verify original input decks, output states, frames, units, ephemerides, solver settings, versions, and provenance on the complete repositories before using that family as validation evidence. No generation or retrieval date is inferred for the new nbody ledger entry.

## Regenerate and verify the manifest

The manifest at `src/ssapy_data/manifest.json` records `scripts/update_manifest.py` as its generator. After applying the overlay, run that generator from the **complete checkout**, then run the package-data tests in the installed test environment:

```shell
python scripts/update_manifest.py
python -m pytest tests/test_package_data.py
```

Do not regenerate the manifest from the partial patch directory: it lacks most packaged resources and would remove their inventory entries. Review the resulting diff; changed resource bytes must have corresponding byte counts and SHA-256 hashes, and unrelated resource entries should remain present. `REPORT_FIXES.md` is repository documentation, outside the manifest's `data` resource root.

This patch's focused checks do not substitute for installed-wheel resource tests, a complete repository test run, or independent verification of benchmark physics.
