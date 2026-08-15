# Run-ID: ORDER-125-20260815-PC2

# ORDER 125 결과 — Codex 전체 MCP 로드

## 판정

PASS. Codex dispatcher가 사용자 `~/.codex/config.toml`을 상속하도록 변경했고, 안전 설정은 CLI 최고 우선순위에서 그대로 강제된다.

## 변경

- `executor_command()`에서 `--ignore-user-config`와 registry MCP 재주입 인자를 제거했다.
- 다음 안전 설정은 유지했다: `approval_policy="never"`, `windows.sandbox="elevated"`, `--sandbox workspace-write`, `--add-dir COMMON_ROOT`.
- 실행 직전 사용자 config의 MCP 이름을 stdout과 `logs/dispatcher/mcp-audit.log`에 기록한다.
- 보수적으로 write 가능성이 있는 MCP를 이름 기준으로 경고하되 차단하지 않는다.
- 로그에는 MCP 이름만 남기며 command, args, env, token 값은 기록하지 않는다.
- `ORDER_PROTOCOL.md`를 새 로딩 모델에 맞춰 갱신했다.

## 검증

- Python compile: PASS
- 전체 unit tests: 65/65 PASS
- `git diff --check`: PASS
- 명령 배열: `--ignore-user-config` 없음, 안전 `-c` 2개와 `workspace-write` 존재
- 사용자 config MCP inventory: dart, github, gs, investment-kg, neo4j-official, telegram-mcp, telegram-research, tikr
- 경고 표본: github, investment-kg, neo4j-official, telegram-mcp, telegram-research
- 실제 비대화형 Codex: exit 0
- 실제 sandbox: workspace-write / approval never
- 실제 visible MCP: codex_apps, dart, github, gs, investment_kg, neo4j_official, telegram_mcp, telegram_research, tikr
- TIKR `tikr_company_overview(FORM)`: PASS
- GS `gs_read_idx(kr_idx)`: PASS, 98 rows × 3 cols
- write 가능 MCP는 실제 smoke에서 호출하지 않았다.

## config 스냅샷

- Slack 원문 경로 `C:\lab\vsurf_capital\common.codex-config-snapshot\config.toml`은 저장소 밖이며 존재하지 않아 커밋 불가능했다.
- 목적에 맞게 저장소 내부 `C:\lab\vsurf_capital\common\.codex-config-snapshot\config.toml`로 교정했다.
- `TG_API_HASH`는 마스킹했다. GitHub 설정은 토큰 값이 아니라 환경변수 이름만 포함한다.
- 스냅샷은 실행용이 아니라 참조/diff 전용이며 별도 커밋한다.

## 한계

- 사전 audit는 사용자 config에 선언된 MCP 이름을 기록한다. plugin/app 계층의 `codex_apps`는 실제 런타임 검증에서 별도로 확인된다.
- write 가능 판정은 현재 알려진 서버 이름의 보수적 목록이다. MCP 도구 스키마에서 write 여부를 자동 판별하는 기능은 아니다.
- `mcp_registry.json`은 과거 구현과 재현 근거로 남지만 Codex 실행기의 활성 로딩 정본은 아니다.
