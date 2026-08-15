Run-ID: RUN-126-01

# Order 126 — ATI Phase 1 GS MCP Discovery

## §0

- 상태: DONE (분석 산출물 완료; 데이터 한계 명시)
- 좌표: N/A
- PC1 경로: `C:\lab\vsurf_capital\common\reports\126_report.md`
- 커밋: N/A — dispatcher가 Git 최종화
- 요약: 실제 GS MCP 8개 탭을 읽어 최신 시장/리더십/회전/위험 가설을 작성했다. Daily Morning Report v0.1과 Phase 2 register를 포함한다. 원시 CSV와 자격증명은 저장하지 않았다.

## Evidence and labeling rule

- **FACT**: MCP가 반환한 값, 날짜, 차원 또는 직접 계산값.
- **OBSERVATION**: 여러 FACT의 비교·요약이며 인과 또는 미래 성과를 뜻하지 않는다.
- **HYPOTHESIS**: Phase 2에서 역사적으로 검증해야 할 후보 규칙. 이 보고서에서 threshold를 확정하지 않는다.

호출별 증거와 축약 통계는 [126_data_summary.md](./126_data_summary.md)에 있다.

## ATI Daily Morning Report v0.1 — as of 2026-08-14

### MARKET REGIME

- **FACT**: `bgd_th`는 ema5 양수 14/15, ema20 양수 14/15, 동시 양수 13/15이다. `bgd_thih`는 각각 22/23, 23/23, 22/23이다. KOSPI ema5/ema20diffn은 4.06/4.55다.
- **OBSERVATION**: 단기·중기 breadth가 광범위하게 양수이고 상위 3개 강도 집중도도 24.9~32.1%로 극단적 단일 섹터 집중처럼 보이지 않는다. 다만 전일 대비 `bgd_thih` 동시 개선 10보다 동시 악화 12가 많아, 강한 절대 수준 속 내부 감속이 공존한다.
- **HYPOTHESIS (REGIME)**: breadth 동시 양수와 KOSPI 양수의 결합은 단일 EMA보다 risk-on regime 판별력이 높고, 개선/악화 확산은 exposure 증감의 선행 보조지표가 될 수 있다.

### EXPOSURE HYPOTHESIS

- **OBSERVATION**: 현재 자료는 broad-positive regime을 지지하지만 전일 내부 감속과 주기별 rank 충돌도 보여 준다.
- **HYPOTHESIS**: Phase 2에서는 exposure를 단일 숫자로 확정하지 말고 breadth 수준, breadth 변화, Q/W 방향 합치, concentration의 조합으로 단계화한다. 현재는 “확대 허용 여부 검토, 추격 확대는 확인 대기” 후보 상태다; 실제 비중 또는 주문 지시가 아니다.

### LEADING SECTORS

- **FACT**: Q 상위는 전공정/전자부품/전선/mem/반도체장비, W 상위는 건설/로봇2/SW/optic/로봇이다. 최신 EMA 결합강도 상위에는 로봇2/로봇/이차전지/자동차/전자부품이 있다.
- **OBSERVATION**: 전공정·전자부품은 장기 누적 리더십이나 W가 각각 18/23위로 약하다. 로봇2·로봇은 W와 EMA가 동반 상승해 신규 단기 리더 후보지만 Q는 각각 19/7위라 성숙도가 다르다.
- **HYPOTHESIS (LEADERSHIP)**: Q 상위+W 회복+EMA 동시 양수의 순차 결합이 “기존 leader 재가속”과 “신규 leader 부상”을 구분할 수 있다.

### LEADING STOCKS

- **FACT**: 현재 `kr_idx` 기준 로봇2 구성은 에스피지/에스비비테크/한국피아이엠/뉴로메카, 전공정은 브이엠/테스/주성엔지니어링/GST, 전자부품은 삼성전기/LG이노텍/대덕전자/아모텍이며 각 25 가중이다. BGD 대표주 EMA는 로봇2 에스피지 1.04, 로봇 로보티즈 1.05, 전자부품 삼성전기 1.12다.
- **OBSERVATION**: 섹터 leader 후보군은 식별되지만 `kr_idx`에는 개별 종목 가격 시계열이 없어 strongest/strong/weak를 사실로 분류할 수 없다.
- **HYPOTHESIS**: Phase 2에서 구성종목의 상대수익률·breadth를 추가하면 대표주 단독 신호보다 leader 지속성 판별력이 개선된다.

### TURNING-ROTATION

**TURNING PATTERN CANDIDATE #1 — Market Turning / broad recovery**

- **FACT**: 2026-07-24 `bgd_thih` ema5 양수 breadth는 8/23이었다가 7/31 22/23, 8/14 22/23이 됐다. 로봇2 ema5/ema20은 -4.74/-14.50 → 6.97/1.05 → 6.15/14.80 순으로 변했다.
- **OBSERVATION**: 단기 breadth 확산이 먼저 나타나고 여러 중기 EMA가 뒤따라 양수화한 회복 사례다.
- **HYPOTHESIS (TURNING)**: Market Turning은 sector rank 하나가 아니라 breadth 저점→ema5 확산→ema20 확인의 순서를 별도 패턴으로 검증해야 한다.

**TURNING PATTERN CANDIDATE #2 — Leadership Rotation / robotics emergence**

- **FACT**: 7/24→8/14 로봇 Q/W rank는 13/18→7/5, ema5/ema20은 -5.22/-13.64→6.22/13.32다. 로봇2 W rank는 16→2, Q rank는 22→19다.
- **OBSERVATION**: 기존 Q 리더 전공정/전자부품의 W 약세 속 로봇 계열 단기 순위와 EMA가 함께 개선됐다. 이는 장기 리더 교체 확정이 아니라 신규 leadership rotation 후보다.
- **HYPOTHESIS (ROTATION)**: Leadership Rotation은 기존 Q leader의 W 약화와 신규 sector의 W rank+breadth+EMA 동반 개선으로 별도 검증해야 한다.

따라서 Market Turning, Sector Turning, Leadership Rotation은 관찰 단위와 확인 순서가 달라 Phase 2에서 분리하는 편이 타당하다.

### SECTOR RISK

- **FACT**: optic은 8/10 W rank 1 및 ema5/ema20 13.71/24.53에서 8/14 W rank 4, Q rank 14, ema5/ema20 -0.98/9.99로 변했다. 그 사이 전체 ema5 breadth는 22/23을 유지했다.
- **OBSERVATION — Early warning**: 시장 breadth 유지 중 optic 단기 EMA 음전과 rank 후퇴는 sector-specific deterioration 후보다.
- **HYPOTHESIS — Confirmation**: ema20 약화, W rank 추가 하락, constituent breadth/leader 동반 약화가 후속될 때만 위험 확인으로 승격한다.
- **Expected failure case**: ema5가 빠르게 양전하고 W rank가 회복되면 단순 조정일 수 있다.

### ENTRY

- **HYPOTHESIS**: 약세 sector의 ema5 회복, breadth 확산, W rank 개선이 순차 발생하고 ema20이 안정될 때 Entry 후보로 분류한다. 7/24→7/31 로봇2가 역사 사례 후보이며 임계값은 미확정이다.

### BUILD

- **HYPOTHESIS**: Entry 이후 ema20 양전, W rank 지속 개선, 구성종목 breadth 확대가 확인될 때 Build 후보로 승격한다. 로봇2의 7/31→8/14 진행은 검증 사례 후보일 뿐 매수 지시가 아니다.

### REDUCE-EXIT

- **HYPOTHESIS**: 시장 breadth가 유지되는 가운데 sector ema5 음전→rank 하락→ema20/leader/breadth 동반 약화가 이어지면 Reduce, 그 이후 다중 확인이 지속되면 Exit 후보로 검증한다. optic은 Early warning까지만 충족한다.

### HEAD-UP

- **NEW LEADER**: 로봇 — W 5위, Q 7위, ema5/ema20 6.22/13.32. 중·단기 정렬 후보.
- **EMERGING SECTOR**: 로봇2 — W 2위와 강한 EMA지만 Q 19위. 신규 부상인지 단기 반등인지 확인 필요.
- **TURNING WATCH**: 자동차 — 최신 W one-row rank +5, ema5/ema20 6.14/9.71; Q 11/W 12로 아직 상위 리더는 아니다.
- **SECTOR RISK**: optic — ema5 음전 및 W 1→4 후퇴, ema20은 아직 양수.
- **UNUSUAL RANK CHANGE**: 자동차 +5, 로봇 +4 (W 전일 대비). 표본 기반 threshold가 없으므로 “unusual”은 모니터링 라벨이지 통계적 이상 확정이 아니다.

### DATA LIMITATION

- `bgd_year`는 220행(2025-09-18~2026-08-14) rolling window이며 장기 역사 전체가 아니다.
- `kidx-mmt` 최신일은 2026-07-22이고 반도체장비 중복열 경고가 있어 최신 regime 결정에서 제외했다.
- `etf_idx`는 coercion/NA warning과 16개 NA weight 행이 있어 weighted inference에서 제외했다. 현재 구성도 과거 구성으로 간주하지 않았다.
- 건설 ETF mapping 정정 여부를 확인할 guide가 프로젝트 안에 없어 건설 관련 ETF 추론을 배제했다.
- 현재 constituent mapping만 있고 개별 구성종목 가격 시계열이 없어 strongest/middle/weakest 및 constituent breadth는 미확인이다.

## Phase 2 Hypothesis Register

| ID | Category | Observation | Hypothesis | Metric | Threshold Candidate | Required Historical Test | Expected Failure Mode | Priority |
|---|---|---|---|---|---|---|---|---|
| H-REG-01 | REGIME | breadth와 KOSPI EMA가 동시 양수 | 다중 breadth 결합이 exposure regime을 개선 | ema5+, ema20+, both+, KOSPI EMA, concentration | 분위수/상태조합; 미확정 | 220행 밖 충분한 bull/bear 구간, walk-forward | breadth 급반전·횡보장 whipsaw | P0 |
| H-LEAD-01 | LEADERSHIP | Q/W 순위가 전공정·전자부품에서 충돌 | Q 리더의 W 재상승이 지속성 확인 | Q/W rank, rank slope, EMA, constituent breadth | rank 교차/지속일; 미확정 | 다수 sector cycle과 forward relative return | 장기 누적 수준이 rank를 고착 | P0 |
| H-TURN-01 | TURNING | 7/24→7/31 breadth 8/23→22/23 | breadth→ema5→ema20 순서가 market turn 후보 | breadth trough, EMA crossing order | 변화폭/지속일; 미확정 | D-20~D+20 전 시장 저점 표본 | 단일 이벤트 반등·휴일 효과 | P0 |
| H-ROT-01 | ROTATION | 로봇/로봇2 W와 EMA 개선, 기존 Q leader W 약세 | 상대 rank 교차와 breadth가 rotation을 구분 | old/new leader Q/W rank, EMA, breadth | rank spread/지속일; 미확정 | D-20~D+20 leadership 교체 표본 | 두 그룹 동시 상승, horizon artifact | P0 |
| H-RISK-01 | SECTOR_RISK | 시장 유지 중 optic 단기 약화 | sector-only 다중 악화가 조기 위험 | sector EMA5/20, rank, leader, breadth vs market | 순차 확인 조건; 미확정 | 정상 조정과 지속 하락 비교 | 빠른 ema5/rank 회복 | P0 |
| H-ENT-01 | ENTRY | 로봇2는 EMA·W rank가 저점 후 회복 | ema5 회복+W rank 개선 후 ema20 안정이 entry 후보 | crossing order, rank delta, breadth | lookback/confirmation; 미확정 | 모든 sector의 event study | gap rebound 후 재하락 | P1 |
| H-BLD-01 | BUILD | 로봇2 중기 EMA와 W rank가 후속 개선 | 다중 확인 지속 시 build 후보 | ema20 slope, W persistence, constituent breadth | 지속일/확산율; 미확정 | entry cohort forward test | concentration in one stock | P1 |
| H-EXT-01 | EXIT | optic은 early warning만 충족 | rank→ema20→leader/breadth 악화 누적 시 reduce/exit | warning count/order, relative drawdown | 단계별 조건; 미확정 | false-positive/lead-time analysis | 단순 조정을 exit로 오판 | P0 |

## ATI 판단영역 결론

1. **Market Regime / Exposure**: broad-positive이나 내부 감속을 함께 보는 단계적 exposure 가설.
2. **Leadership**: Q 누적 리더와 W 신규 리더를 분리하고 재정렬을 검증하는 가설.
3. **Turning / Rotation**: 실제 7/24 회복과 robotics 부상 사례에서 서로 다른 패턴 후보 2개.
4. **Sector Risk**: 시장 유지 중 optic 약화의 Early warning→Confirmation→Failure 구조.
5. **Trade Lifecycle**: Entry/Build/Reduce/Exit를 다중 신호의 순서로 검증; 실제 주문 없음.
6. **CIO Head-up**: NEW LEADER, EMERGING SECTOR, TURNING WATCH, SECTOR RISK, UNUSUAL RANK CHANGE 포함.

## Remaining limits

Phase 1은 threshold를 정하지 않았다. Phase 2에는 더 긴 역사, 당시 구성종목 스냅샷, 개별 종목 가격/breadth, 정상 조정 대조군이 필요하다. `etf_idx` NA/coercion과 `kidx-mmt` 중복열은 upstream 정비 후 재검증해야 한다.
