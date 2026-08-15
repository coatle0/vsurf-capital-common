# ORDER 123 — MCP Dispatcher Generalization

- 발행일: 2026-08-15
- 발신: COO
- 수신: Bill/Codex
- 상태: 완료
- 도구: local files, git, Codex CLI, tikr MCP, gs MCP

## 목적

MCP가 추가될 때마다 dispatcher에 전용 분기를 추가하지 않도록 Git 정본 registry 기반 구조로 일반화한다.

## 작업

1. `resolve_gs_mcp_config()`의 환경변수 우선순위 패턴을 `resolve_mcp_config(name)`으로 일반화한다.
2. 저장소 내부 registry에 tikr/gs와 향후 MCP 설정을 선언적으로 관리한다.
3. `executor_command()`가 enabled MCP의 Codex `-c mcp_servers.*` 인자를 공통 생성하게 한다.
4. 기존 tikr 및 gs 설정과 호출의 회귀시험을 수행한다.
5. 백업 → 수정 → dry-run → 격리 temp repo → MCP 재현 → 실사용 검증 순서를 지킨다.

## 금지

- Registry를 저장소 밖에 두지 않는다.
- 기존 tikr/gs 회귀를 허용하지 않는다.
- GS의 R `quantmod` 문제는 별도 작업으로 유지한다.

## DoD

- registry, diff, tikr/gs 회귀시험 결과를 `reports/123_report.md`와 Slack에 보고한다.
