발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 137
제목: ati-gs-raw-snapshot-morning-report-v02-retry
목적: clean-tree 및 Git divergence blocker 해소 후 ATI GS raw snapshot / Morning Report v0.2 작업을 Order 137로 재실행한다. ATI handover의 CURRENT STATE(Phase 1 COMPLETE, Phase 2/2B 완료, Phase 3 HOLD)에서 GS MCP 반환 payload를 dated raw snapshot으로 보존하고, 동일 raw data 기반 차트와 ATI Morning Report v0.2 PDF를 생성한다.
대상: coatle0/gs-toolkit의 gs_batch.py·gs_reader.R·gs_mcp_server.py, GS MCP의 bgd_year·bgd_th·bgd_thih·kidx-Q·kidx-W·kr_idx, ATI handover 및 Orders 126/128/130/134/135/136
작업:
1. Governance ACTIVE v1.2 preflight 4개와 clean working tree를 실행 직전 재확인하고 reports/137_report.md 첫 부분에 기록한다. Order 137 외 새 번호 생성 금지.
2. GS MCP implementation을 재실측한다. gs_batch.py의 NamedTemporaryFile, gs_reader.R의 write.csv, payload의 csv field, finally os.unlink 동작을 확인하여 “temporary CSV 생성 후 삭제, CSV text payload 반환” 여부를 PASS/FAIL로 판정한다.
3. MCP core는 수정하지 않는다. 반환 payload의 csv 값을 그대로 dated ATI raw snapshot으로 저장하는 최소 thin wrapper 또는 repository convention에 맞는 snapshot 경로를 사용한다. as-of와 source sheet를 metadata/manifest에 남긴다.
4. GS MCP를 실제 호출하여 bgd_year, bgd_th, bgd_thih, kidx-Q, kidx-W, kr_idx 6개 sheet의 raw CSV snapshot을 확보한다. 각 파일의 rows, cols, header, latest/common date, checksum을 기록하고 payload와 저장본 byte/content parity를 검증한다.
5. kidx-mmt는 stale/duplicate ambiguity로 supporting context only, etf_idx는 weight coercion/NA로 weighted inference에서 제외한다.
6. GS embedded chart export 가능 여부를 확인한다. 가능하면 원본 chart를 우선 사용하고, 불가능하면 저장한 GS raw values 자체를 그대로 시계열로 시각화한다. 임의 숫자·synthetic indicator·예시 차트 생성 금지.
7. 차트에 source sheet, 사용 columns, as-of를 표시한다. 우선 구간은 2026-07-24→2026-07-31→2026-08-14, 우선 대상은 market breadth, Robot, Robot2, Optic, 전공정, 전자부품이다.
8. ATI Morning Report v0.2 PDF를 생성한다. 각 섹션은 판정→GS Evidence Table→GS/raw 기반 Chart→해석→CIO Action 순서로 작성하며, Executive Decision, Market Regime, Market Turning, Sector Leadership/Rotation, Sector Turning, Sector Risk, Stock Head-Up(데이터 허용 범위), Today's ATI Playbook, Confidence/Validation status를 포함한다.
9. FACT/OBSERVATION/HYPOTHESIS/VALIDATION을 구분한다. Leadership continuation/rotation leading/simple sector-risk precursor의 REJECT, Sector Turning/Entry/Build/Exit의 UNVERIFIED 상태를 유지하며 검증되지 않은 exposure sizing이나 기대수익을 확정적으로 표현하지 않는다.
10. reports/137_report.md에 snapshot 경로, chart/PDF 경로, 호출 결과, parity 검증, 사용·제외 데이터, PASS/FAIL, blocker, commit SHA를 기록하고 모든 산출물을 commit/push한다.
금지: GS raw 없이 임의 숫자나 예시 차트 생성, MCP core 불필요 수정, synthetic score를 사실처럼 표시, Phase 3 Skill/Policy 승격, unrelated refactor, credential 출력·commit, Order 137 외 새 번호 생성.
DoD: (a) GS MCP CSV lifecycle 코드 실측 PASS/FAIL, (b) 6개 실제 raw CSV snapshot과 payload parity 증거, (c) 실제 GS raw 기반 차트, (d) ATI Morning Report v0.2 PDF, (e) Phase 2 verdict와 epistemic labels 유지, (f) reports/137_report.md 생성, (g) commit/push 완료.
