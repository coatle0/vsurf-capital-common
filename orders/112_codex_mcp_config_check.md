발행일: 2026-08-14
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 112
제목: codex_mcp_config_check
목적: 111번에서 tikr MCP 가 codex 세션에 안 보인 원인 규명. CIO 기억: "agent 부를 때 mcp 안 붙이는게 default이고 지정에 따라 붙게 했다"는 설계가 있었을 가능성 — 이걸 실물로 확인한다. codex CLI 자체는 커뮤니티 이슈 기준 반대 성향(등록된 MCP를 기본 전부 로드하려는 경향, 끄기가 오히려 어려움)이라는 조사 결과가 있어 상충한다.
작업:
1. 현재 codex 세션의 ~/.codex/config.toml 전체 내용을 그대로 reports/112_report.md 에 옮긴다(토큰·API키 등 민감값이 있으면 그 줄만 마스킹, 나머지는 그대로). 파일이 없으면 "파일 없음"을 명시한다.
2. .codex/config.toml (프로젝트 스코프, 있다면 C:\lab\vsurf_capital\common.codex\ 또는 다른 위치) 도 확인해 있으면 함께 옮긴다.
3. 위 설정에 mcp_servers 섹션이 있는지, 있다면 tikr 관련 항목이 있는지, enabled 값이 어떻게 되어 있는지 확인한다.
4. dispatcher 가 codex 를 부를 때 사용하는 CLI 인자에 MCP 관련 플래그(--ignore-user-config 등)가 있다는 것을 알고 있다면, 그것이 이 config 로딩에 미치는 영향을 codex 자신의 관찰(세션 헤더에 표시되는 정보 등)로 설명한다.
금지: config.toml 을 수정하지 않는다. 읽기만 한다. 민감정보(토큰·API키 값)는 절대 원문 그대로 출력하지 않고 마스킹한다.
DoD: reports/112_report.md 존재, Run-ID: RUN-112-01 첫 줄 포함, Slack 3줄 회신. config 파일이 아예 없어도 그 사실 자체가 유효한 완주 결과다.
