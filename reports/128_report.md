Run-ID: RUN-128-01

# Order 128 — ATI Phase 2 hypothesis validation

## §0 execution result

- Status: DONE with explicit `UNVERIFIED` items; no trade/order action was performed.
- Canonical inputs: Order 126 commit `d5d817d9ac42e6e948ac14dfebea6c672034b8e7`, `reports/126_report.md`, and `reports/126_data_summary.md`.
- Evidence: read-only GS MCP calls to `bgd_year`, `bgd_th`, `bgd_thih`, `kidx-Q`, and `kidx-W` on 2026-08-15 (Asia/Seoul). No sheet was changed and no raw CSV was stored.
- Label rule retained: **FACT** is a returned value or direct calculation; **OBSERVATION** summarizes facts; **HYPOTHESIS** is a candidate rule and not a forecast.

## Data and method

### Available coordinates

| Sheet | Rows | Available dates | Use |
|---|---:|---|---|
| `bgd_year` | 220 | 2025-09-18–2026-08-14 | integrity/range check only |
| `bgd_th` | 94 | 2026-03-31–2026-08-14 | 14-sector breadth and KOSPI EMA proxy |
| `bgd_thih` | 94 | 2026-03-31–2026-08-14 | 23-sector breadth and sector EMA proxy |
| `kidx-Q` | 95 | 2026-03-30–2026-08-14 | cross-sectional Q rank |
| `kidx-W` | 38 | 2026-06-23–2026-08-14 | cross-sectional W rank |

**FACT:** `bgd_year` is a 220-row rolling window, not full history. `kidx-mmt` was not used because Order 126 established that it is stale and has a duplicate-column ambiguity. `etf_idx` was not used because its weight coercion created 16 NA rows. These sources therefore do not support validation evidence here.

No price or total-return series is exposed by these sheets. Accordingly, all forward outcomes below are an **alternative performance indicator**: change in KOSPI or sector `ema20diffn` from the event row to D+5/D+10/D+20. “Hit” means that this change has the hypothesized sign. It is not a security return, excess return, P&L, or investable backtest. Rows near the end have fewer forward observations; `n` is reported separately by horizon.

Events use trading-row horizons and may overlap unless explicitly de-duplicated. Thresholds are compared in families rather than selected from the best result. No holdout period exists, so all findings carry material overfitting and serial-correlation risk.

## Independent hypothesis register and quantitative verdicts

| ID | Event unit and definition | Forward outcome | Main quantitative result | Phase 3 verdict |
|---|---|---|---|---|
| H-REG-01 REGIME | Daily row: 14-sector ema5 breadth at/above candidate level, 5-row breadth change at/above candidate change, and KOSPI ema5/ema20 both positive | KOSPI ema20diffn change D+5/10/20 | Across candidate cells, D+5 hit 68–82% (n=9–19), but D+10 hit 31–54% and D+20 hit 31–41%; most longer means/medians are negative | **CONDITIONAL**: short-horizon state label only; reject persistent risk-on/exposure implication |
| H-TURN-01 MARKET TURNING | Non-overlapping confirmation event: 23-sector ema5 breadth trough, expansion within 5 rows, then ema20 breadth improvement within 10 rows; confirmations separated by at least 10 rows | KOSPI ema20diffn change D+5/10/20 | 5–6 events; D+5 hit 60–83%, D+10 hit 0–20%, D+20 hit 25–40% | **CONDITIONAL**: reproducible sequence, not durable turn confirmation |
| H-LEAD-01 LEADERSHIP | Sector-date: Q and W both top-k plus ema5/ema20 positive (“aligned”); Q outside top 10 and W top-k plus both EMA positive (“emerging”); Q top-k/W worse than 10 (“conflict”) | Sector ema20diffn change D+5/10/20 | For k=3/5/7, aligned D+5 hit 0–16% and emerging D+5 hit 9–23%; conflict D+5 hit 63–67% | **REJECT** as continuation classifier; observed result is consistent with mean reversion in the proxy |
| H-ROT-01 LEADERSHIP ROTATION | Date: at least one old Q top-k sector has W rank worse than 10 while a Q-below-10 newcomer is W top-k with both EMA positive; compare mean newcomer vs old-leader forward EMA20 change | New-minus-old sector ema20diffn change D+5/10/20 | k=3/5/7: 15–18 event dates; D+5 hit 31–54%, D+10 13–25%, D+20 0% (only n=4 at D+20) | **REJECT** for proposed leading rule; longer-horizon evidence is especially weak |
| H-RISK-01 SECTOR RISK | Sector-date: ema5 crosses positive-to-nonpositive and W rank retreats by at least 2/4/6 places versus best of prior 5 W rows | Subsequent sector ema20diffn decline D+5/10/20 | 29–61 warnings; downside hit only 32–36% at D+5, 28–36% at D+10, 23–25% at D+20; false-warning rate 48–56% | **REJECT** as standalone warning; confirmation inputs remain unverified |
| H-ENT-01 ENTRY | Sector Turning: ema5 recovery + W-rank improvement + ema20 stability | Sector return and constituent breadth | Required historical constituent/return data absent | **UNVERIFIED** |
| H-BLD-01 BUILD | Post-entry ema20 slope/persistence + W-rank persistence + constituent breadth | Sector/constituent forward return | Required entry cohort and constituent history absent | **UNVERIFIED** |
| H-EXT-01 EXIT | Risk warning followed by ema20, leader, and constituent-breadth deterioration | Relative drawdown and warning lead time | Only the first two sheet-level legs are available; leader/constituent outcome absent | **UNVERIFIED** as full rule; simple precursor is rejected |

## Threshold-family results

### Market Regime — breadth level + change + KOSPI EMA

Candidate levels are 50%, 70%, and 85%; candidate 5-row changes are 0, +10 percentage points, and +20 points. Representative cells follow (mean/median are ema20diffn-point changes).

| Breadth / 5-row change | Events | D+5 n, hit, mean/median | D+10 n, hit, mean/median | D+20 n, hit, mean/median |
|---|---:|---|---|---|
| 50% / +0pp | 20 | 19, 68%, +0.44/+1.30 | 19, 37%, -3.13/-2.55 | 19, 37%, -4.25/-2.25 |
| 70% / +10pp | 11 | 11, 82%, +0.89/+2.06 | 11, 36%, -3.58/-4.66 | 11, 36%, -6.13/-7.65 |
| 85% / +20pp | 9 | 9, 78%, +0.07/+2.01 | 9, 44%, -2.72/-4.66 | 9, 33%, -6.59/-7.65 |

**OBSERVATION:** higher breadth does not stabilize the D+10/D+20 proxy. The combination may describe a current strong state or a brief impulse, but this window does not validate persistent exposure expansion.

### Market Turning — kept separate from Sector Turning and Rotation

Trough candidates are 30%, 40%, and 50% ema5 breadth; required 5-row expansion candidates are +20pp, +30pp, and +40pp. The ema20-breadth confirmation only requires improvement from the trough, deliberately avoiding a fitted confirmation threshold.

| Trough / expansion | Events | D+5 n, hit, mean/median | D+10 n, hit, mean/median | D+20 n, hit, mean/median |
|---|---:|---|---|---|
| 30% / +20pp | 5 | 5, 60%, +1.37/+1.52 | 5, 20%, -6.29/-4.66 | 4, 25%, -7.07/-9.12 |
| 40% / +30pp | 5 | 5, 80%, +2.39/+2.43 | 4, 0%, -9.92/-10.38 | 4, 25%, -7.07/-9.12 |
| 50% / +20pp | 6 | 6, 83%, +2.40/+2.43 | 5, 0%, -9.21/-6.37 | 5, 40%, -5.59/-8.90 |

The five-event 30% family confirms on 2026-05-22, 06-12, 06-29, 07-15, and 07-31. Candidate threshold changes frequently identify the same clustered turns, so their apparent agreement is not independent evidence.

### Leadership and Leadership Rotation

| top-k | Aligned count; D+5 n/hit/median | Emerging count; D+5 n/hit/median | Conflict count; D+5 n/hit/median | Rotation dates; D+5 n/hit/median |
|---:|---|---|---|---|
| 3 | 14; 14/0%/-22.00 | 16; 11/9%/-5.78 | 56; 46/67%/+6.81 | 15; 11/36%/-10.98 |
| 5 | 27; 26/12%/-13.79 | 30; 18/22%/-3.06 | 108; 88/66%/+7.31 | 18; 13/54%/+0.05 |
| 7 | 41; 32/16%/-12.36 | 41; 22/23%/-2.87 | 160; 135/63%/+5.50 | 18; 13/31%/-4.88 |

At D+10 the aligned hit rate is 7–8%, emerging 33–44%, and rotation 13–25%. At D+20 rotation has four usable dates for every threshold and 0% hit. Counts are sector-date observations and are highly dependent within date; they must not be read as independent samples.

### Sector Risk — simple precursor and failure rate

| Rank retreat threshold | Warnings | D+5 n/downside hit/mean/median | D+10 n/downside hit/mean/median | D+20 n/downside hit/mean/median | False warnings |
|---:|---:|---|---|---|---:|
| 2 places | 61 | 59/34%/+2.41/+2.37 | 50/36%/+4.53/+3.10 | 35/23%/+12.09/+12.45 | 33/61 (54%) |
| 4 places | 39 | 38/32%/+2.72/+2.34 | 32/28%/+5.54/+3.68 | 25/24%/+13.57/+15.85 | 22/39 (56%) |
| 6 places | 29 | 28/36%/+1.98/+2.32 | 24/33%/+4.54/+3.21 | 20/25%/+13.52/+16.27 | 14/29 (48%) |

Here positive mean/median means the sector ema20 proxy improved, contrary to the risk hypothesis. A false warning is an ema5 recovery within 5 rows with no observed D+10 ema20 decline (or insufficient D+10 history). This definition is conservative about end-of-window censoring but still shows that the optic-style precursor alone is unreliable.

## Failure cases and exclusions

1. **Short impulse, no durable turn:** Market Turning gives a favorable D+5 proxy but unfavorable D+10/D+20 results. Treating confirmation as a lasting bottom is a failure mode.
2. **Rank/EMA saturation and mean reversion:** sectors already top-ranked with both EMA measures positive subsequently lose EMA20 strength. Q/W agreement is not validated as persistence.
3. **False sector warning:** ema5 can recover after a negative cross while ema20 does not deteriorate; the measured false-warning rate is roughly one half.
4. **Concurrent market movement:** pooled sector events share dates and market shocks, violating independence. No causal claim or standard significance test is justified.
5. **Threshold overfit:** only 94 breadth rows and 38 W rows cover a single recent regime. Choosing the best cell would be post-hoc optimization; no threshold is finalized.

## Event-class separation

- **Market Turning:** cross-market breadth trough → ema5 breadth expansion → ema20 breadth improvement. Quantified above.
- **Sector Turning:** a single sector’s reversal plus constituent breadth/returns. **UNVERIFIED** because historical constituent breadth and return coordinates are absent.
- **Leadership Rotation:** old/new cross-sectional Q/W-rank state with EMA confirmation. Quantified separately above and rejected as a leading rule in this window.

These classes were not pooled into one event count or one verdict.

## Phase 3 promotion decision

- **Candidate for conditional promotion:** H-REG-01 only as a descriptive, short-horizon regime-state feature; it must not set exposure or imply D+10/D+20 persistence.
- **Candidate for conditional research continuation:** H-TURN-01 as a sequence detector with an explicit “D+5 impulse only / durability unproven” label.
- **Excluded from promotion:** H-LEAD-01 continuation classifier, H-ROT-01 leading rotation rule, and the simple H-RISK-01 precursor. Their hypothesized forward signs do not hold robustly across the tested threshold families.
- **UNVERIFIED, therefore excluded:** H-ENT-01, H-BLD-01, full H-EXT-01, and Sector Turning.

## Required additional data / remaining limits

To convert proxy tests into return tests and resolve `UNVERIFIED` items, Phase 3 research needs: (1) dated KOSPI and sector-index close or total-return series covering multiple bull/bear cycles; (2) point-in-time sector constituents and weights; (3) constituent adjusted-price/return histories; (4) constituent breadth and leader-strength snapshots; (5) W and Q histories materially longer than 38/95 rows; and (6) an out-of-sample or walk-forward split.

`bgd_year` remains only a 220-row rolling window. Current `kr_idx` mappings cannot be back-cast. `kidx-mmt` and weighted `etf_idx` remain limited for the reasons above. No individual-stock performance was inferred, no new index was constructed, and no GS sheet was modified.
