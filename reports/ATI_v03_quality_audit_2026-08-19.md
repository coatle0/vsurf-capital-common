# ATI v0.3 Quality Audit — 2026-08-19

## Result

PASS. GS MCP raw persistence behavior was measured, six payloads were preserved as dated snapshots, and the Morning Report was rebuilt with decision-first charts and explicit units.

## GS MCP persistence

- Runtime creates a temporary `.csv`, reads it into the MCP response `csv` field, and deletes the file in `finally`.
- Live `bgd_th` smoke: `ok=true`, 97 rows, 46 columns, 77,975 UTF-8 bytes.
- Temporary CSV remaining after the live call: 0.
- Durable snapshot therefore requires preserving the returned payload outside the MCP runtime.

## Snapshot

- Common as-of: 2026-08-19.
- Six GS payloads saved without value transformation under `data/ati/2026-08-19/v03_raw/`.
- Manifest records source tool, rows, columns, latest date, SHA-256, and payload parity.
- Payload parity: 6/6 PASS.

## Readability improvements

- Each chart starts with the investment question it answers.
- EMA values show the zero threshold and define positive/negative direction.
- Q/W raw levels were replaced by ranks; 1 is explicitly labeled as strongest.
- Executive page states observation, meaning, action, and validation limit separately.
- Dynamic breadth language prevents a low-breadth state from being labeled as broad recovery.

## Current measured state

- EMA5-positive breadth: 23/23 → 22/23 → 2/23 on 2026-08-04, 2026-08-11, 2026-08-19.
- Q/W ranks: Robot 8/7, Robot2 21/5, Optic 15/6, Front-end 1/15, Electronic Parts 2/23.
- Interpretation: broad short-term deterioration; strong Q ranks in Front-end/Electronic Parts do not agree with recent W ranks. Robot2 has strong recent rank but conflicts with negative EMA5.
- Governance: WATCHLIST ONLY; no exposure sizing, expected return, or trade order.

## Verification

- Python compile: PASS.
- Diff check: PASS.
- PDF structure: 4 pages, nonzero size.
- Chart visual inspection: PASS; Korean labels, units, zero line, rank direction, and source date are readable.
- No Git commit or push was performed.
