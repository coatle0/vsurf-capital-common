발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 122
제목: gs-mcp-dispatcher-enable
목적: 기존 TIKR MCP의 Codex 복원 구현을 기준으로 GS MCP도 Order Dispatcher의 비대화형 Codex 실행환경에서 사용할 수 있게 추가하고, ATI Phase 1 진입 전 4개 GS tool smoke test까지 실측 완료한다.
대상: scripts/order_dispatcher.py 및 관련 최소 테스트/보고서
작업:
1. 현재 `order_dispatcher.py::executor_command()` Codex 분기의 TIKR MCP 복원 구현을 실측하고 동일 패턴을 기준으로 GS MCP를 추가한다.
2. `--ignore-user-config` 상태에서도 `<http://mcp_servers.gs|mcp_servers.gs>`가 노출되도록 필요한 `-c` 설정을 주입한다. 최소 항목은 command, args, default_tools_approval_mode, APPDATA, LOCALAPPDATA, USERPROFILE, R_USER, GS_RSCRIPT이다.
3. PC1 경로를 그대로 하드코딩하지 말고, 실행 PC에서 Python/Rscript 및 사용자 환경을 실측하거나 기존 프로젝트의 PC별 설정/환경변수 패턴을 사용해 동적으로 해석한다. GS server script는 실제 존재 여부를 확인한 뒤 사용한다.
4. 변경 전후 생성되는 Codex 명령 배열을 비교하여 `--ignore-user-config` 뒤에도 TIKR 기존 복원이 보존되고 GS 설정이 추가되었는지 확인한다. 기존 TIKR 동작을 깨뜨리지 않는다.
5. 비대화형 Codex smoke test에서 다음 4개 tool이 실제 노출되는지 확인한다: `gs_read_bgdgs`, `gs_read_bgdidx`, `gs_read_sggs`, `gs_read_idx`.
6. 동일 비대화형 Order 실행조건에서 아래 read-only 호출을 실제 수행한다:
    ◦ `gs_read_bgdgs(sheet_name="bgd_th")`
    ◦ `gs_read_sggs(sheet_name="kidx-Q")`
    ◦ `gs_read_idx(sheet_name="kr_idx")`
    ◦ `gs_read_bgdidx(sheet_name="etf_idx")`
1. 각 호출은 성공/실패, ok, rows, cols, warning, header 일부만 기록한다. 전체 CSV dump 금지.
2. `R exit 3221225477`이 데이터 반환 성공과 병존하면 warning으로 보존한다. `etf_idx` coercion warning이 있으면 NA 존재 여부를 추가 확인하고 기록한다.
3. 관련 최소 단위 테스트 또는 격리 dry-run을 실행하여 GS 추가가 기존 TIKR/dispatcher 동작에 회귀를 만들지 않았는지 확인한다.
4. `reports/122_report.md`를 작성한다. 첫 줄은 `Run-ID: RUN-122-01`. 변경 파일, 실제 생성 명령, GS MCP 실측 설정, 4개 tool 노출 결과, 4개 smoke test 결과, warning, 회귀검증 결과, PASS/FAIL, 남은 위험을 기록한다.
5. 변경 파일과 보고서를 commit하고 commit hash를 회신한다.
금지: Google Sheets 쓰기, BGD.R/alltheidx*.R 실행, ATI 본 분석 수행, credential 출력, 전역 Codex config 광범위 수정, PC1 절대경로 무검증 하드코딩, 기존 TIKR MCP 제거/비활성화, 관련 없는 코드 변경.
DoD: Order Dispatcher의 비대화형 Codex 실행에서 GS MCP 4개 tool이 노출되고 지정 4개 sheet의 read-only smoke test가 모두 ok=true여야 PASS한다. 기존 TIKR 복원 동작이 보존되고 회귀 테스트가 통과해야 한다. `reports/122_report.md`와 Git commit이 생성되어야 하며 Slack 회신은 ACK/COMPLETED/FAILED + commit hash 형식을 따른다.
