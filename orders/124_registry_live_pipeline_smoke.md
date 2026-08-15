# ORDER 124 — Registry live pipeline smoke

- 발행일: 2026-08-15
- 발신: Codex (ORDER 123 final validation)
- 수신: Codex
- 상태: 완료
- 도구: tikr, gs

## 목적

ORDER 123의 registry 기반 MCP 주입이 실제 Slack consumer/dispatcher 경로에서도 작동하는지 최종 확인한다.

## 작업

1. TIKR `tikr_company_overview(ticker="FORM")`을 읽기 전용 호출한다.
2. GS `gs_read_idx(sheet_name="kr_idx")`를 읽기 전용 호출한다.
3. `reports/124_report.md`에 각 호출의 ok와 ticker 또는 rows/cols만 기록한다. 원시 CSV는 기록하지 않는다.

## 금지

- 위 보고서 외 파일 수정 금지.
- 외부 write 금지.
- MCP 실패를 성공으로 보고하지 않는다.

## DoD

- 두 호출 모두 실제 `ok=true`.
- `reports/124_report.md` 생성.
- dispatcher가 commit/push하고 Slack에 commit hash를 회신.
