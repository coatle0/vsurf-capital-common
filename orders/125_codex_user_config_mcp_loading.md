# ORDER 125 — Codex user-config MCP loading

- Codex dispatcher에서 `--ignore-user-config`를 제거한다.
- `approval_policy="never"`, `windows.sandbox="elevated"`, `workspace-write`는 유지한다.
- 사용자 config에서 상속되는 MCP 이름을 기록하고 write 가능 MCP를 경고한다.
- TIKR/GS와 실제 Order 종단 회귀를 검증한다.
- 실제 config를 마스킹해 저장소 내부 참조 스냅샷으로 별도 커밋한다.
