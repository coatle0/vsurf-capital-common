발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 130
제목: ati-phase2b-data-extension-backtest
목적: ORDER 128에서 Phase 2 가설 검증은 완료됐지만 장기 수익률·point-in-time 구성종목·충분한 Q/W 역사 부재로 핵심 Entry/Build/Exit 및 Sector Turning이 UNVERIFIED이고, Regime/Turning도 단기 proxy 수준에 머문다. Phase 3 Skill 승격 전에 실제 가격/수익률 기반 백테스트 가능한 데이터 좌표와 최소 검증 파이프라인을 확보해 ATI Phase 2를 마무리한다.

전제:
• ORDER 128 완료 commit `f6f472357cd8373835383b70024c1c296ac9750c`, `reports/128_report.md`를 정본으로 사용한다.
• ORDER 128 판정: REGIME=CONDITIONAL(short horizon only), MARKET TURNING=CONDITIONAL(D+5 impulse only), LEADERSHIP=REJECT, ROTATION=REJECT, simple SECTOR RISK=REJECT, ENTRY/BUILD/EXIT/Sector Turning=UNVERIFIED.
• Phase 3에는 검증된 규칙만 승격하며 proxy 결과를 실제 투자수익률 결과로 오인하지 않는다.
작업:
1. 현재 repo/연결 MCP/기존 데이터 소스에서 다음 좌표의 존재 여부와 접근경로를 실측한다: dated KOSPI/sector index close 또는 total-return series, point-in-time sector constituents/weights, constituent adjusted price/return history, constituent breadth/leader snapshots, 장기 Q/W history.
2. 기존 GS MCP/TIKR/로컬 데이터 중 재사용 가능한 소스를 우선하고, 신규 대규모 데이터 수집은 하지 않는다. 각 소스는 기간, 빈도, survivorship/look-ahead risk, 수정 가능성, 라이선스/접근 제한을 기록한다.
3. 확보 가능한 가격 시계열로 ORDER 128의 H-REG-01과 H-TURN-01을 실제 forward return 기준으로 재검증한다. 최소 D+5/D+10/D+20, 표본수, win rate, mean/median return, max adverse excursion 또는 사용 가능한 drawdown 대체지표를 제시한다.
4. 가능하면 LEADERSHIP/ROTATION/RISK도 실제 sector return으로 재검증해 proxy와 방향이 일치하는지 확인한다. 기존 REJECT를 억지로 살리지 말고 결과가 동일하면 REJECT 유지.
5. Sector Turning, ENTRY, BUILD, EXIT는 필요한 constituent history가 존재하는 경우에만 최소 prototype backtest를 수행한다. 데이터가 없으면 정확한 blocker 좌표와 필요한 schema를 명시하고 UNVERIFIED 유지.
6. threshold는 2~3개 후보군 비교 + walk-forward 또는 최소한 시간분할 검증을 적용한다. full-sample 최적 threshold 하나만 선택하지 않는다.
7. 결과를 `reports/130_report.md`에 기록하고, Phase 3 승격 대상/제외 대상을 PASS / CONDITIONAL / REJECT / UNVERIFIED로 다시 분류한다.
8. 재현 가능한 최소 분석 script가 필요하면 repo 내 최소 파일로 저장한다. 원시 대용량 데이터 dump는 금지.
금지:
• 실제 주문/거래 실행
• Google Sheets 수정
• survivorship-biased 현재 구성종목을 과거 구성으로 간주
• forward information 사용
• proxy를 실제 return으로 표기
• 신규 대규모 데이터 수집/크롤링
• 단일 최적 threshold의 사후 확정
DoD:
• 가격/수익률 데이터 좌표 availability matrix 존재
• H-REG-01/H-TURN-01의 실제 return 검증 또는 명확한 BLOCKED 근거 존재
• 가능 항목의 D+5/D+10/D+20 실제 return 통계 존재
• 시간분할/walk-forward 또는 데이터상 불가 사유 명시
• Entry/Build/Exit/Sector Turning의 검증 가능 여부 명확화
• Phase 3 승격 후보와 제외 후보 재분류
• `reports/130_report.md` 첫 줄 `Run-ID: RUN-130-01`
• Git commit 후 COMPLETED/FAILED + commit hash 회신
