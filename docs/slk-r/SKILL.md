---
name: slk-r
description: Read the latest Slack message from a known channel. Use for /slk-r skl, /slk-r rpt, /slk-r agt. Add body to also fetch attached .md in memory. Do not use for posting, setup, or git.
when-to-use: slk-r, /slk-r, slk-r skl, /slk-r rpt, slk-r agt, slk-r skl body, 슬랙 최신, slk 최신, slack latest, 최신 메시지 확인
argument-hint: skl | rpt | agt | skl body
user-invocable: true
allowed-tools: use_tool
---

Call `slack_read_channel` once. Pick the ID locally. Do not search channels.

| 인자 | 채널 | ID |
|---|---|---|
| 없음, skl | `#vsurf-skill` | `C0BR8722F6C` |
| rpt | `#vsurf-code-reports` | `C0BSX931CPJ` |
| agt | `#vsurf-agent-control` | `C0BS4RXHV25` |

Unknown name → stop. Do not call `slack_search_channels`.

- limit: `1`
- Default: caption only (`text`). That is the `initial_comment`, not the attached .md.
- If the user also said `body` / 본문 / 내용: one more call, `slack_read_file` with the message `files[0].id`. Do not pass `save_path`. Do not write disk.

Do not use `search_tool`, do not read local files, do not run git or tests.

Reply with channel name, `ts`, and the caption. If `body` was requested, then the file text. No table. No extra report.
