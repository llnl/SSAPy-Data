# IERS Earth orientation data

`finals2000A.all` is a frozen copy of the IERS Bulletin A Earth orientation
series. It contains daily historical, rapid-service, and predicted records in
the official 187-byte fixed-width format.

The SSATK reader uses these fields:

| Bytes | Field | Unit |
| ---: | --- | --- |
| 1–2, 3–4, 5–6 | UTC year, month, day | — |
| 8–15 | MJD (UTC) | day |
| 17 | polar-motion status | `I` or `P` |
| 19–27, 38–46 | Bulletin A polar motion `x`, `y` | arcsec |
| 58 | UT1 status | `I` or `P` |
| 59–68 | `UT1−UTC` | s |
| 96 | celestial-pole status | `I` or `P` |
| 98–106, 117–125 | `dX`, `dY` | milliarcsec |

The uncertainty and Bulletin B columns remain in the original file for audit
and future model selection. `sources.json` records the retrieval, checksum,
units, and distribution terms for this snapshot.

Predicted records must remain distinguishable from observed/rapid-service
records. Consumers should opt in explicitly when propagation extends into the
prediction interval.
