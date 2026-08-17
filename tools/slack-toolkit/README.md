# Grok Slack MCP (조회·보고 전용)

정본 경로: `C:\lab\vsurf_capital\common\tools\slack-toolkit`

Grok에는 공식 Slack Connector가 없다. 이 stdio MCP가 조회·보고용이다.
PC2 Order listener/consumer를 대신하지 않는다. 토큰을 이 폴더나 Git에 두지 않는다.

## PC1 / PC2 공통 설정

```powershell
git -C C:\lab\vsurf_capital\common pull --ff-only
powershell -File C:\lab\vsurf_capital\common\scripts\setup_grok_slack_mcp.ps1
```

토큰은 User 환경변수만 사용한다.

```powershell
[Environment]::SetEnvironmentVariable("OPENACP_SLACK_BOT_TOKEN", "<paste-once-in-terminal>", "User")
```

값은 채팅·Git·로그에 쓰지 말고, 확인은 `<set>` / `<not set>`만 보고한다.

Grok config는 `C:\autoai\slack-toolkit`이 아니라 이 git 경로를 가리킨다.
`C:\autoai\slack-toolkit` 복사는 필요 없다.
