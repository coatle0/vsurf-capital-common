발행일: 2026-08-14
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 121
제목: phase3-canonical-docs-refresh
목적: Phase 1·2 실측 결과(Orders 100~120)를 정본 문서에 반영하여 낡거나 상충하는 운영 설명을 제거하고 Phase 3 표준화의 기준선을 확정한다.
대상: ORDER_PROTOCOL.md, AGENT_RULES.md, board.md
작업:
1. reports/ 및 관련 commits에서 Orders 100~120의 실측 결과를 확인하고, 추정이 아니라 저장소 근거가 있는 내용만 반영한다.
2. ORDER_PROTOCOL.md §4를 갱신하여 codex 경로가 해결된 현재 상태와 실제 실행 명령·제한을 반영하고 “codex 미작동/미해결” 문구를 제거한다.
3. ORDER_PROTOCOL.md §5를 현재 확정 포맷으로 수정한다. Slack 발주는 [EXECUTE ORDER 100] intake + ORDER BODY 방식이며 executor는 codex/claude/available, project는 필수, order: 필드는 넣지 않는 규칙을 명확히 한다.
4. ORDER_PROTOCOL.md §6·§7을 Orders 100~120 결과에 맞춰 정리한다. durable inbox, allowlist, 예약작업, signature parser, MCP 주입, claim/lock, 강제 종료 및 수동 stale-lock 복구의 현재 상태와 제한을 구분한다.
5. AGENT_RULES.md의 Orders 및 Slack 실행 Order 절을 현재 구현과 일치시키고, 필수 order: 필드·OpenACP 직접실행·중첩호출 금지 등 폐기된 설명을 제거한다. ORDER_PROTOCOL.md를 단일 상세 정본으로 참조하게 하여 중복 규칙의 재발을 줄인다.
6. board.md는 3줄 상한과 기존 STI-G1·SA-0 행을 보존한다. 파이프 행만 Phase 2 완료(Orders 100~120), Phase 3 정본 갱신 진행/완료 및 다음 행동 “governance DRAFT 3건 제출”로 갱신하고 날짜를 08-14로 바꾼다.
7. 세 문서 사이의 포맷·실행자·경로·상태 정의가 서로 모순되지 않는지 교차검토하고, 기존 테스트 중 문서 규칙과 연관된 검증을 실행한다.
8. reports/121_report.md를 작성한다. 첫 줄은 Run-ID: RUN-121-01로 하고 파일별 변경 요약, 근거 Order/commit, 제거한 낡은 규칙, 교차검토 및 테스트 결과, PASS/FAIL과 남은 위험을 기록한다.
9. 변경 파일과 보고서를 커밋하고 commit hash를 회신한다.
금지: STI-G1·SA-0 상태 임의 변경, governance 정책 3건을 ACTIVE로 선포, 실측 근거 없는 기능 완료 선언, credential·개인 설정 기록, 관련 없는 코드 변경, 기존 사용자 변경 덮어쓰기.
DoD: ORDER_PROTOCOL.md·AGENT_RULES.md·board.md가 Orders 100~120의 현재 구현과 일치하고 서로 모순되지 않아야 한다. codex 미작동, order: 필수, OpenACP 직접 실행 등 폐기된 설명이 제거되어야 한다. board 3줄 상한과 기존 두 프로젝트 행이 보존되어야 한다. reports/121_report.md와 Git commit이 생성되고 검증 결과가 기록되어야 한다.
