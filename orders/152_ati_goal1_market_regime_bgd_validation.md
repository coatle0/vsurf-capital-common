[EXECUTE ORDER 152]
executor: codex
project: C:\lab\vsurf_capital\common

--- ORDER BODY ---
번호: 152
제목: ati-goal1-market-regime-bgd-validation
목적: ATI 목표 1인 Market Regime/Exposure 판단을 BGD.R의 실제 계산 정의와 최신 GS raw snapshot으로 재실행하고, 임의 점수 없이 재현 가능한 evidence 기반 판정 구조를 만든다.
대상: BGD.R, GS MCP raw snapshot (`bgd_year`, `bgd_th`, `bgd_thih`)
작업:
1. `R_tools\BGD.R` 또는 실제 canonical BGD.R 위치를 확인하고, `bgd_year`, `bgd_th`, `bgd_thih` 생성 로직과 `ema5diffn/ema20diffn/ema50diffn` 정의를 코드 기준으로 문서화한다.
2. GS MCP를 현재 세션에서 재시작/재호출하여 `bgd_year`, `bgd_th`, `bgd_thih` 최신 데이터를 읽고 각 호출의 `raw_snapshot.status/path/metadata_path/as_of/sha256`를 기록한다. raw snapshot 생성 실패 시 원인만 진단하고 임의 데이터로 대체하지 않는다.
3. 최신 raw snapshot에서 Market Regime용 최소 지표를 계산한다: (a) EMA5 양(+) 섹터 breadth, (b) EMA20 양(+) breadth, (c) EMA50 양(+) breadth가 가능한 경우, (d) 최근 5~10 trading rows breadth 변화, (e) ema5diffn/ema20diffn/ema50diffn의 평균과 중앙값, (f) ETF/대표주 확인 가능한 confirmation/divergence.
4. `st_date <- "2026-03-31"` normalization이 Regime 판단에 미치는 영향을 분리해서 평가한다. normalized ema5 level은 핵심 판단 신호로 사용하지 말고 EMA deviation/breadth와 구분한다.
5. 결과를 임의 numeric score 없이 `RISK-ON EXPANDING / RISK-ON DECELERATING / NEUTRAL-TRANSITION / RISK-OFF` 중 하나의 operational label과 confidence로 제시한다. 기준은 이번 run에서 사용한 실제 데이터와 함께 명시한다.
6. 최근 시계열에서 판단에 직접 사용한 raw-derived table과 chart를 생성한다. synthetic/illustrative data 금지. 각 chart에 source sheet, as_of, snapshot sha256를 표시한다.
7. `reports/152_report.md`에 `판정 → Raw Evidence Table → 시계열 Chart → 해석 → Exposure implication → limitations` 순서로 정리한다.
8. 이번 작업은 ATI 목표 1만 다룬다. Leadership/Rotation/Sector Risk/Entry-Build-Exit 규칙은 새로 만들거나 검증하지 않는다.
금지:
• GS write 금지.
• BGD.R 원본 계산 로직 수정 금지.
• raw data 임의 생성/보간/예시 차트 금지.
• Phase 2에서 REJECT된 단순 Q/W continuation 규칙 재사용 금지.
• Market Regime 결과를 검증되지 않은 기대수익/P&L로 표현 금지.
DoD:
• BGD.R 계산 정의와 snapshot provenance가 report에 명시됨.
• `bgd_year`, `bgd_th`, `bgd_thih` 중 사용 가능한 최신 raw snapshot의 path/as_of/sha256가 기록됨.
• 실제 raw 기반 Market Regime 지표와 최소 1개 시계열 chart가 생성됨.
• operational regime label 1개와 Exposure implication이 근거와 함께 제시됨.
• limitations와 NOT VERIFIED 항목이 분리됨.
• `reports/152_report.md` 생성 및 관련 산출물 Git commit 완료.
--- END ---
