Run-ID: RUN-130-01

# Order 130 — ATI Phase 2B data extension / backtest readiness

## 0. Execution result

- Status: **COMPLETED AS A DATA-AVAILABILITY AUDIT; RETURN BACKTEST BLOCKED**.
- Execution date: 2026-08-15 (Asia/Seoul).
- Canonical baseline: Order 128 commit `f6f472357cd8373835383b70024c1c296ac9750c` and `reports/128_report.md`.
- Actions: repository/history inspection plus read-only GS MCP calls. No Google Sheet, trade, order, or external dataset was modified; no bulk data was collected or stored.
- Governing rule: a derived index is not called an actual/investable return unless its dated constituent membership, weights, adjustment method, and price lineage are known point-in-time.

Order 128's return upgrade cannot be completed from the currently connected sources. The blocker is not merely sample length: there is no qualified dated KOSPI close/total-return series, and the sector series are paired only with an undated current constituent master. Consequently H-REG-01 and H-TURN-01 remain proxy-only, while constituent-dependent rules remain UNVERIFIED.

## 1. Measured availability matrix

| Required coordinate | Measured source / access path | Period / frequency | Result | Survivorship / look-ahead and other limits |
|---|---|---|---|---|
| Dated KOSPI close or total return | Local repo search; GS `bgd_year`, `bgd_th`, `etf_idx`; connected TIKR tool inventory | `bgd_year`: 2025-09-18–2026-08-14, 220 daily rows; `bgd_th`: 2026-03-31–2026-08-14, 94 daily rows | **ABSENT / BLOCKED** | `kospi_ema5diffn`, `ema20diffn`, and `ema50diffn` are transformed indicators, not close/TR. `etf_idx` contains identifier-like values and NA coercions, not a dated return series. TIKR exposes company research/financial/report endpoints but no price-history endpoint. |
| Dated sector close or total return | GS `kidx-Q`, `kidx-W`, `kidx-mmt`; `bgd_year`, `bgd_th`, `bgd_thih` | Q: 2026-03-30–2026-08-14, 95 daily rows; W: 2026-06-23–2026-08-14, 38; mmt: 2026-07-06–2026-07-22, 12; breadth sheets as above | **PRESENT AS DERIVED LEVELS, NOT QUALIFIED RETURNS** | Q/W contain normalized sector-index-like levels, but formula lineage, corporate-action handling, rebalance dates, and point-in-time membership are unavailable. `kidx-mmt` is stale and has a duplicate column. EMA-difference fields remain proxies. |
| Point-in-time sector constituents / weights | GS `kr_idx`; GS `etf_idx` | One undated snapshot; 98 rows in `kr_idx`, 30 rows in `etf_idx` | **ABSENT** | `kr_idx` is a current static master, usually 4–5 names per group and equal weights; it has no effective-from/to or rebalance date. It cannot be back-cast. `etf_idx` has 16 NA weight/coercion rows established in Order 126/128 and reconfirmed here. |
| Constituent adjusted price / return history | Local repo; connected GS/TIKR inventories | None | **ABSENT** | No symbol-date adjusted close, delisting return, split/dividend flag, or source revision timestamp. |
| Constituent breadth / leader snapshots | GS `bgd_th`, `bgd_thih`; Q/W cross-sectional levels | 94 daily breadth rows; Q/W windows above | **PARTIAL, PROXY ONLY** | Representative-name EMA and synthetic-sector EMA/rank states exist, but constituent-level numerator/denominator and membership snapshots do not. |
| Long Q/W history | GS `kidx-Q`, `kidx-W` | 95 / 38 daily observations, one recent regime | **INSUFFICIENT** | Too short for bull/bear coverage or an honest train/test split with D+20 outcomes. Source may revise in place; no immutable version or as-of timestamp is exposed. |

### Access, revision, and license notes

- GS sources are accessible only through the configured read-only MCP whitelist in this run. The connector returns calculated sheet values, not formula/version history; later sheet recalculation may revise past cells.
- The connected TIKR service is access-controlled and suitable for company documents/financials in its exposed surface, but no historical market-price call was available. No claim is made about unexposed TIKR product features.
- Local repository data contains Order 127/129 governance artifacts but no relevant market-price dataset. Repository contents are internally reusable; upstream GS/TIKR redistribution or bulk export rights were not established, so no raw dump was created.

## 2. H-REG-01 and H-TURN-01 return validation

| Hypothesis | Required return outcome | D+5 | D+10 | D+20 | Verdict |
|---|---|---|---|---|---|
| H-REG-01 REGIME | KOSPI close/TR forward return from each qualifying breadth/EMA state | **BLOCKED** | **BLOCKED** | **BLOCKED** | **CONDITIONAL retained**, solely as Order 128's short-horizon descriptive proxy |
| H-TURN-01 MARKET TURNING | KOSPI close/TR forward return from each non-overlapping confirmation event | **BLOCKED** | **BLOCKED** | **BLOCKED** | **CONDITIONAL retained**, explicitly “D+5 proxy impulse only; actual return and durability unverified” |

The exact missing join is `event_date -> market_price[date] -> market_price[date + trading horizon]`. No reachable table supplies `market_price`. Therefore sample size, win rate, mean/median return, and MAE cannot truthfully be reported as actual returns. Order 128's EMA20-difference statistics are not repeated or relabelled.

## 3. Sector-return diagnostic and why it is excluded

A reproducibility diagnostic used the Q normalized sector levels as if they were continuous price indices, solely to test whether that shortcut would be safe. For Order 128's top-k families (3/5/7), aligned-leadership D+5 outcomes were n=14/26/32, win rate 7.1%/19.2%/28.1%, mean -17.54%/-13.34%/-11.53%, median -19.65%/-14.71%/-12.29%, and worst forward observation -38.86% for every family. At D+10 the win rate was 7.1%/8.0%/7.4%, and at D+20 it was 0% for all three families.

This diagnostic agrees directionally with Order 128's **REJECT** of the aligned continuation classifier. It is **not an actual-return backtest** and is excluded from promotion because:

1. `kr_idx` is an undated current constituent snapshot, so historical Q values may embed survivorship/look-ahead exposure.
2. Q's construction, adjustment, rebalance, and revision lineage are not exposed.
3. The W window starts only on 2026-06-23; overlapping sector-date observations are dependent and D+20 observations are heavily censored.
4. Magnitudes are implausibly large for a controlled investable sector benchmark and cannot be independently reconciled to constituent adjusted prices.

Rotation produced an especially important contradiction: newcomer-minus-old-leader Q-level changes appeared positive at D+10/D+20 across top-k families, opposite Order 128's EMA proxy direction, but only 6–8 D+10 and four D+20 event dates were available. Because the same invalid lineage applies, this is a warning against proxy equivalence, not evidence to reverse the **REJECT** verdict.

Simple sector RISK was not rerun as an actual-return test: the same unqualified Q lineage would turn a known data defect into a false validation. Existing **REJECT** is retained.

## 4. Threshold and time-split disposition

- Candidate families were preserved at top-k = 3, 5, 7; no best full-sample threshold was selected.
- A valid walk-forward or time split is **not possible** for the main return hypotheses because the market return outcome is absent.
- For Q/W-dependent sector rules, W has only 38 rows. Reserving D+20 plus a non-overlapping holdout would leave too few independent event dates, while the point-in-time lineage defect would remain. The diagnostic above is therefore descriptive only and is not a fitted model.
- Required minimum for the next run: immutable source version, multiple regimes, and either rolling-origin folds with a 20-trading-day embargo or a dated train/validation/test split fixed before threshold comparison.

## 5. Constituent-dependent rules and exact blocker schemas

Sector Turning, ENTRY, BUILD, and EXIT were not prototyped because all require point-in-time constituent history and adjusted constituent returns. They remain **UNVERIFIED**.

Minimum schemas:

```text
market_price(date, market_id, close, total_return_index, currency,
             adjustment_method, source, as_of_ts)

sector_price(date, sector_id, close, total_return_index, currency,
             construction_method, source, as_of_ts)

sector_membership(sector_id, symbol, effective_from, effective_to,
                  weight, weight_method, rebalance_date, source, as_of_ts)

constituent_price(date, symbol, adjusted_close, total_return,
                  split_factor, dividend, listing_status, source, as_of_ts)

constituent_snapshot(date, sector_id, symbol, breadth_state, leader_score,
                     eligible_flag, source, as_of_ts)
```

Required controls include delisted names, corporate actions, effective-dated membership, contemporaneously knowable weights, calendar alignment, missing-price policy, and an immutable extraction timestamp. Current constituents must never be applied before `effective_from`.

## 6. Phase 3 classification

| Rule / feature | Order 130 classification | Phase 3 action |
|---|---|---|
| H-REG-01 | **CONDITIONAL** | May enter only as a descriptive short-horizon state feature; no exposure rule and no actual-return claim. |
| H-TURN-01 | **CONDITIONAL** | Research sequence detector only, labelled D+5 proxy impulse; no durable-turn claim. |
| H-LEAD-01 | **REJECT** | Exclude. The unqualified Q diagnostic does not rescue it and directionally reinforces rejection. |
| H-ROT-01 | **REJECT** | Exclude. Proxy and unqualified Q diagnostic conflict; neither qualifies as forward investable evidence. |
| Simple H-RISK-01 | **REJECT** | Exclude as standalone warning. |
| Sector Turning | **UNVERIFIED** | Exclude until effective-dated membership and constituent adjusted returns exist. |
| H-ENT-01 ENTRY | **UNVERIFIED** | Exclude; entry cohorts cannot be formed without qualified Sector Turning and constituent history. |
| H-BLD-01 BUILD | **UNVERIFIED** | Exclude; persistence and breadth outcomes unavailable. |
| H-EXT-01 full EXIT | **UNVERIFIED** | Exclude; relative drawdown, leader, and constituent deterioration outcomes unavailable. |

No rule is promoted as **PASS**. Conditional labels preserve only the narrow Order 128 proxy findings; they are not trading rules.

## 7. Remaining limits and next executable step

The minimum unblock is not more threshold tuning. It is a small, licensed, immutable extract matching the schemas above: dated KOSPI TR/close, dated sector TR/close with construction metadata, and effective-dated constituent membership plus adjusted prices. Once present, rerun the predeclared 3/5/7 families and H-REG breadth families with D+5/D+10/D+20 returns, hit rate, mean, median, and event-window MAE, using rolling-origin folds and a 20-day embargo. Until then, ATI Phase 2B is closed as **data-blocked**, and all constituent-dependent items remain outside Phase 3.
