# Order 126 — GS MCP compact evidence

Generated from read-only GS MCP calls on 2026-08-15 (Asia/Seoul). Raw CSV payloads are intentionally not stored.

## Call log

| Call | ok | rows | cols | warning summary |
|---|---:|---:|---:|---|
| `gs_read_bgdgs("bgd_th")` | true | 94 | 46 | none |
| `gs_read_bgdgs("bgd_thih")` | true | 94 | 70 | R returned data with non-zero process-code warning |
| `gs_read_bgdgs("bgd_year")` | true | 220 | 46 | R returned data with non-zero process-code warning |
| `gs_read_sggs("kidx-Q")` | true | 95 | 24 | R returned data with non-zero process-code warning |
| `gs_read_sggs("kidx-W")` | true | 38 | 24 | R returned data with non-zero process-code warning |
| `gs_read_sggs("kidx-mmt")` | true | 12 | 13 | duplicate `반도체장비_idx` names normalized to `...5`/`...9`; latest row is 2026-07-22 |
| `gs_read_idx("kr_idx")` | true | 98 | 3 | R returned data with non-zero process-code warning |
| `gs_read_bgdidx("etf_idx")` | true | 30 | 3 | `NAs introduced by coercion`; 16 rows have non-numeric/NA weight |

`ok=true` and dimensions are MCP response facts. The recurring process-code warning did not prevent CSV return, but it is an operational integrity warning, not evidence of clean execution.

## Latest compact statistics

Latest common date for `bgd_th`, `bgd_thih`, `kidx-Q`, and `kidx-W`: **2026-08-14**.

- `bgd_th` (15 series including KOSPI): ema5 positive 14/15, ema20 positive 14/15, both positive 13/15; vs 2026-08-13, both measures improved together in 8 and worsened together in 5. Top-three share of total positive ema5+ema20 strength: 32.1%.
- `bgd_thih` (23 sectors): ema5 positive 22/23, ema20 positive 23/23, both positive 22/23; improved together in 10 and worsened together in 12. Top-three positive-strength share: 24.9%.
- Top combined `bgd_thih` ema5/ema20: 로봇2 6.15/14.80, 로봇 6.22/13.32, 이차전지 4.46/14.65, 자동차 6.14/9.71, 전자부품 6.91/8.92.
- `kidx-Q` top five level ranks: 전공정 223.95, 전자부품 211.64, 전선 200.35, mem 181.41, 반도체장비 140.35.
- `kidx-W` top five: 건설 118.13, 로봇2 117.50, SW 117.06, optic 105.50, 로봇 105.09.
- Largest one-row W rank rises: 자동차 +5, 로봇 +4, 로봇2 +2, 반도체장비 +2. One-row changes are observations, not calibrated anomalies.
- `kidx-mmt` is stale relative to 2026-08-14 and structurally ambiguous due to duplicate 반도체장비 columns; it is supporting context only.

## Date-bounded case evidence

### Broad recovery: 2026-07-24 → 2026-07-31 → 2026-08-14

- On 2026-07-24, only 8/23 `bgd_thih` sectors had positive ema5diffn.
- On 2026-07-31, breadth rose to 22/23; 로봇2 moved from ema5/ema20 -4.74/-14.50 to 6.97/1.05 and W rank 16→4.
- On 2026-08-14 breadth remained 22/23; 로봇2 reached 6.15/14.80 and W rank 2.

### Horizon rotation: robotics versus inherited semiconductor leadership

- 로봇 moved from Q/W ranks 13/18 on 2026-07-24 to 7/5 on 2026-08-14; ema5/ema20 moved from -5.22/-13.64 to 6.22/13.32.
- 전자부품 ended at Q rank 2 but W rank 23; 전공정 ended at Q rank 1 but W rank 18. Their positive latest EMA readings indicate recovery, while the rank split indicates unresolved horizon conflict.
- `kr_idx` constituents (equal 25 weights): 로봇2 = 에스피지/에스비비테크/한국피아이엠/뉴로메카; 전공정 = 브이엠/테스/주성엔지니어링/GST; 전자부품 = 삼성전기/LG이노텍/대덕전자/아모텍.

### Sector-specific risk: optic

- optic rose to W rank 1 with ema5/ema20 13.71/24.53 on 2026-08-10.
- By 2026-08-14 it was W rank 4, Q rank 14, ema5 -0.98, ema20 9.99. This is an early-warning candidate, not confirmation of failure.

## Integrity limitations

- `bgd_year` is exactly a 220-row rolling window (2025-09-18 through 2026-08-14), not full history.
- Current `etf_idx` composition is not used as historical composition. Because coercion produced NA weights, it is excluded from weighted inference.
- Construction ETF mapping cannot be independently established from the available guide (the referenced `GS_MCP_index_BGD_guide.md` is absent from the project root); construction is treated only through BGD/SGS/`kr_idx` observations.
- `kr_idx` supplies current constituents and weights, not constituent price histories. It cannot establish strongest/middle/weakest stock performance.
