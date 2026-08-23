# Grok Slack MCP (조회·보고 전용)

정본 경로: `C:\lab\vsurf_capital\common\tools\slack-toolkit`

Grok에는 공식 Slack Connector가 없다. 이 stdio MCP가 조회·보고용이다.
PC2 Order listener/consumer를 대신하지 않는다. 토큰을 이 폴더나 Git에 두지 않는다.

## PC1 / PC2 공통 설정

```powershell
git -C C:\lab\vsurf_capital\common pull --ff-only
powershell -File C:\lab\vsurf_capital\common\scripts\setup_grok_slack_mcp.ps1
```

토큰은 User 환경변수만 사용한다. Grok이 `${OPENACP_SLACK_BOT_TOKEN}`을
펼치지 못하면 서버가 그 리터럴을 버리고 `HKCU\Environment`에서 읽는다.

```powershell
[Environment]::SetEnvironmentVariable("OPENACP_SLACK_BOT_TOKEN", "<paste-once-in-terminal>", "User")
```

값은 채팅·Git·로그에 쓰지 말고, 확인은 `<set>` / `<not set>`만 보고한다.

Grok config는 `C:\autoai\slack-toolkit`이 아니라 이 git 경로를 가리킨다.
`C:\autoai\slack-toolkit` 복사는 필요 없다.

## 빠른 읽기 경로

채널 검색하지 말고 ID로 바로 읽는다.

| 채널 | ID |
|---|---|
| `#vsurf-skill` | `C0BR8722F6C` |
| `#vsurf-code-reports` | `C0BSX931CPJ` |
| `#vsurf-agent-control` | `C0BS4RXHV25` |

- 최신 메시지 확인: `slack_read_channel(channel=C0BR8722F6C, limit=1)` 한 번. 회신은 ts + 캡션 한 줄. `slack_post_markdown` 첨부는 캡션만 보인다. 검색·표 금지.
- 첨부 본문: `slack_read_file(file_id=...)`. 기본은 메모리만. 디스크에 쓰지 마라. 텍스트/md만.
- 텍스트 게시: 긴 글은 `.md` + `slack_post_markdown`. `slack_send_message`는 한 줄 ACK 전용 (한도 약 4000자).
- 짧은 브리프: 기본 `limit=3` (이름 `#vsurf-skill`도 ID로 해석)
- 서버는 HTTPS keep-alive와 토큰 캐시를 사용한다. 알려진 채널 이름은 목록 API 없이 해석한다.
- Grok MCP 프로세스에 반영하려면 세션을 재시작한다.
