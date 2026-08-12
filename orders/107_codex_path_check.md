발행일: 2026-08-13
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 107
제목: codex_path_check
목적: ORDER_PROTOCOL §4에 기록된 codex 미작동(--ignore-user-config 가 windows sandbox=elevated 설정을 함께 제거해 blocked by policy 발생) 이 현재도 재현되는지 실물 확인한다.
작업:
1. C:\lab\vsurf_capital\common\structure_map.md 첫 3줄을 읽는다.
2. 읽은 내용을 reports/107_report.md 에 Report §0 형식으로 남긴다.
금지: 다른 파일 수정·삭제 금지. structure_map.md 는 읽기만 한다.
DoD: 실행 성공 시 orders/107_codex_path_check.md 와 reports/107_report.md 존재, Slack 3줄 회신 도착. 실패해도(blocked by policy 등) 그 자체가 유효한 결과이며 FAIL 로 보고한다.
