Run-ID: RUN-121-01

# Order 121 — Phase 3 canonical docs refresh

## 판정

PASS. Orders 100~120의 저장소 보고서·구현·commit을 근거로 세 정본의 Slack 포맷, executor, 경로, 상태 및 복구 설명을 현재 구현에 맞췄다. STI-G1·SA-0 행은 변경하지 않았고 governance DRAFT를 ACTIVE로 선포하지 않았다.

## 파일별 변경 요약

- `ORDER_PROTOCOL.md`: Codex 정상 경로와 실제 CLI 제한, Order 100 intake + ORDER BODY 확정 포맷, signature parser, allowlist·예약작업·MCP 주입·claim/lock·강제 종료 후 수동 복구의 구현/제한을 구분했다.
- `AGENT_RULES.md`: 중복 상세 규칙을 줄이고 `ORDER_PROTOCOL.md`를 단일 상세 정본으로 참조했다. 외부 `order:` 필수, OpenACP 직접 실행, 중첩호출 금지 등 폐기된 경로를 제거했다.
- `board.md`: 3개 프로젝트 행과 STI-G1·SA-0 내용을 보존하고 파이프 행만 Phase 2 완료, Phase 3 정본 갱신 완료, 다음 행동 `governance DRAFT 3건 제출`, 날짜 08-14로 갱신했다.

## 근거

- Order 100 intake와 등록/자동 commit: `53b1e29`, `e66fe85`; Orders 103·104 복구: `2fa4549`, `de8e2d8`.
- Codex Windows 쓰기 경로: `291d6ab`, Orders 107·110 보고서/완료 commits `156e97c`, `3e9c7f4`.
- signature parser: `a73c9b4`, `3e113a7`, Order 109 완료 `aafaa4c`.
- MCP 주입과 양 executor end-to-end: `803bca4`, `548b48e`, `cc29b42`, Orders 112~117 보고서와 완료 commits `db49518`~`ac8e1f6`.
- 중복 차단과 강제 종료 복구: Orders 118~120 보고서, 완료 commits `0986d7b`, `4b3f569`, `e6fe959`.

## 제거한 낡은 규칙

- “Codex 미작동/미해결”.
- 외부 Slack 메시지의 `order:` 필수 또는 권장 포맷.
- OpenACP 주 세션 직접 실행과 하위 Codex 중첩호출 금지 설명.
- Slack 원문이 executor에게 전달되지 않는다는 설명.
- `도구:` 행이 범용 `--strict-mcp-config` 주입을 이미 구현했다는 설명.

## 교차검토 및 검증

- `ORDER_PROTOCOL.md` §5와 `AGENT_RULES.md` 모두 신규 Slack 발주를 Order 100 intake + ORDER BODY, 필수 `executor`/`project`, 외부 `order:` 없음으로 정의한다.
- executor 쓰기 범위와 Git 최종화 책임, claim/lock의 fail-closed 및 수동 stale 복구 설명을 구현과 대조했다.
- `python -m unittest -v tests.test_order_inbox tests.test_order_inbox_consumer` → 32 tests, OK.
- 결합 실행(`tests.test_order_dispatcher.ParseRequestTests` 포함)은 앞선 32개 성공 뒤 첫 dispatcher parse test에서 120초 timeout되어 PASS로 계산하지 않았다. Orders 119·120에서도 기록된 dispatcher suite의 기존 환경 의존 hang과 같은 제한이다.
- `git diff --check` → 오류 없음.
- board 프로젝트 행 구조 검사 → 정확히 3행. Git diff에서 STI-G1·SA-0 행 변경 없음 확인.
- 폐기 문구 검색(`codex 미작동/미해결`, `order: 필수`, `OpenACP 직접`, `중첩 호출`, `--strict-mcp-config`) → 0건.

## 남은 위험

- PC2 중심 운영이며 consumer는 순차 실행이다.
- 범용 `도구:` 기반 MCP 주입은 없고 Codex는 현재 TIKR만 명시 주입한다.
- TTL/lease/PID 기반 stale-lock 자동 복구가 없다. 비멱등 외부 부작용이 있는 작업은 수동 검토 후에도 안전 재실행을 보장하지 않는다.
- 사용자 지시에 따라 commit/push는 dispatcher 최종화 책임으로 남아 이 실행에서는 commit hash를 생성하지 않는다.
