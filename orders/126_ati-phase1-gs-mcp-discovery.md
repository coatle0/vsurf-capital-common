발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 126
제목: ati-phase1-gs-mcp-discovery
목적: 기존 GS MCP/BGD/SGS/index 인프라의 실제 최신 가격 기반 데이터를 사용해 ATI Phase 1 Discovery를 수행하고, CIO가 매일 아침 사용할 ATI Daily Morning Report Prototype과 Phase 2 검증 가설을 만든다.

전제:
• Order 124 live smoke PASS 및 이후 MCP runtime 정비 완료.
• Google Sheets index 계산 인프라와 GS MCP는 이미 구축되어 있다.
• 새 index 구축이 아니라 기존 데이터를 읽고 해석하는 작업이다.
• 참조: #vsurf-skill `GS_MCP_index_BGD_guide.md`.
ATI 판단 목표:
1. Market Regime → 적정 Exposure 판단 근거
2. Leading Sector / Leading Stock 판별
3. Turning Point / Leadership Rotation Discovery
4. Sector Risk 조기 판정
5. Entry / Build / Reduce / Exit 후보 로직
6. CIO Head-up 섹터/종목
작업:
1. GS MCP를 시트별 순차 호출한다. 최소 대상:
    ◦ gs_read_bgdgs("bgd_th")
    ◦ gs_read_bgdgs("bgd_thih")
    ◦ gs_read_bgdgs("bgd_year")
    ◦ gs_read_sggs("kidx-Q")
    ◦ gs_read_sggs("kidx-W")
    ◦ gs_read_sggs("kidx-mmt")
    ◦ gs_read_idx("kr_idx")
    ◦ gs_read_bgdidx("etf_idx")
1. 각 호출마다 ok/rows/cols/warning을 기록하고, 전체 CSV를 한 번에 context에 넣지 않는다. 필요한 열·기간·통계만 즉시 축약해 중간 산출물로 저장한다.
2. MARKET REGIME: bgd_th/bgd_thih의 sector별 ema5diffn, ema20diffn 분포와 kidx-Q/W/mmt 방향성을 비교한다. 양수 sector 비율, 동시 양수 비율, 전일 대비 개선/악화 sector 수, 강도 집중도를 계산/관찰한다. Threshold는 확정하지 말고 FACT/OBSERVATION/HYPOTHESIS를 분리한다.
3. LEADERSHIP: kidx-Q/W/mmt + BGD를 결합해 sector 상대강도 rank, rank 변화, 단기/중기 강도, cycle 상태를 정리한다. 상위 sector는 kr_idx로 구성종목을 내려가 leader/strong/weak constituent 후보를 찾는다.
4. TURNING POINT는 사전 공식화하지 않는다. 실제 시계열에서 상승→약화, 하락→회복, 기존 leader 약화, 신규 sector 부상, 단순 조정 후 추세복귀 사례를 찾는다. 가능한 사례마다 D-20~D+20 범위에서 ema5diffn/ema20diffn/sector rank/leader/breadth 변화 순서를 비교한다. Market Turning / Sector Turning / Leadership Rotation을 분리할 필요가 있는지 검토하고 `TURNING PATTERN CANDIDATE #n`으로 제시한다.
5. SECTOR RISK: 시장 전체는 유지되는데 특정 sector만 ema5/20diffn, rank, leader, breadth가 악화되는 사례를 우선 탐색해 Early warning / Confirmation / Failure case 후보를 만든다.
6. TRADE LIFECYCLE: 강한 sector 내부 strongest/middle/weakest stock의 상대 움직임을 비교하고 Entry→Build→Reduce→Exit 가설 후보를 만든다. 실제 주문은 만들지 않는다.
7. 최신 데이터로 ATI Daily Morning Report v0.1을 생성한다. 필수 섹션: MARKET REGIME / EXPOSURE HYPOTHESIS / LEADING SECTORS / LEADING STOCKS / TURNING-ROTATION / SECTOR RISK / ENTRY / BUILD / REDUCE-EXIT / HEAD-UP / DATA LIMITATION.
8. HEAD-UP에는 최소 NEW LEADER, EMERGING SECTOR, TURNING WATCH, SECTOR RISK, UNUSUAL RANK CHANGE를 포함한다.
9. Phase 2 Hypothesis Register를 만든다. 필드: ID, Category, Observation, Hypothesis, Metric, Threshold Candidate, Required Historical Test, Expected Failure Mode, Priority. Category: REGIME/LEADERSHIP/TURNING/ROTATION/SECTOR_RISK/ENTRY/BUILD/EXIT.
주의/금지:
• Google Sheets 쓰기 금지.
• BGD.R/alltheidx*.R 실행 금지.
• `bgd_year` 220-row rolling window를 장기 역사 전체로 오인 금지.
• 현재 `etf_idx`를 과거 구성으로 간주 금지.
• 건설 ETF mapping 오류가 미정정이면 배제 또는 명시.
• etf_idx coercion/NA warning이 있으면 검증 후 기록.
• 단일 EMA 신호만으로 매매 결론 확정 금지.
• Phase 1에서 threshold를 임의 확정 금지.
• 데이터로 확인되지 않은 논리를 사실처럼 기술 금지.
DoD:
• 실제 GS MCP 최신 데이터를 사용한 증거가 있다.
• ATI 5개 판단영역 각각 데이터 기반 hypothesis가 있다.
• Turning/Rotation은 실제 사례 기반 pattern candidate가 최소 2개 이상 제시되거나 데이터 한계가 명시된다.
• ATI Daily Morning Report v0.1 생성.
• Phase 2 Hypothesis Register 생성.
• FACT/OBSERVATION/HYPOTHESIS 구분.
• reports/126_report.md 첫 줄 `Run-ID: RUN-126-01`.
• 필요한 요약 산출물과 report를 Git에 commit하고 commit hash를 회신한다.
