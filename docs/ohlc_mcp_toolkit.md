# OHLC MCP Toolkit

> 작성: Bill (Claude, PC2) · 2026-08-23

## 목적

기존 vvp_lab R 캐시(`ohlc_store_cache.rds`, `minute_store/`)를 MCP tool로 바로 조회할 수
있게 하는 read-only 브리지. tikr/gs-toolkit과 동일한 구조(Python MCP → Rscript subprocess
→ CSV 반환).

## 위치

```
C:\autoai\ohlc-toolkit\
  ohlc_reader.R       — readRDS(일봉)/read.csv(1분봉) 래핑
  ohlc_batch.py        — Rscript subprocess 호출, CSV 파싱
  ohlc_mcp_server.py    — MCP tool 2개 노출
```

## Tools

- `ohlc_read_daily(code, from_date="", to_date="")` — 일봉. 컬럼:
  `date,open,high,low,close,volume,adjusted,chgr,pswing,nswing`. `code`는 6자리
  종목코드(예: `005930`), 날짜는 `YYYY-MM-DD`, 생략 시 전체 기간.
- `ohlc_read_minute(code, date)` — 1분봉. 컬럼: `date,tm_idx,open,high,low,close,volume`.
  `date`는 `YYYYMMDD`.

## 데이터 신선도 (중요)

실시간 아님. Windows 예약작업 `VVP_Daily_OHLC_Refresh`가 매일 16:00에 캐시를 갱신한다.
즉 항상 "전일 장마감 기준 최신"이며, 당일 16:00 이전 조회는 전전일까지만 반영돼 있다
(실측 확인: `Get-ScheduledTask` — 마지막 실행 2026-08-21 16:00, 다음 2026-08-24 16:00).

## 실측 검증 (smoke test)

```
ohlc_read_daily("005930", "2026-08-01", "2026-08-21")  → 14 rows, ok=true
ohlc_read_minute("005930", "20260821")                  → 381 rows, ok=true
```

## 등록 현황

3개 실행기 전부 등록·확인 완료:

- **Claude**: `~/.claude.json` `mcpServers.ohlc`
- **Grok**: `grok mcp add ohlc -- python ohlc_mcp_server.py` → `grok mcp doctor` healthy
- **Codex**: `codex mcp add ohlc -- python ohlc_mcp_server.py` → `codex mcp list` enabled
- **Hermes**: `hermes mcp add ohlc --command python --args ohlc_mcp_server.py` → 연결 성공,
  tool 2개 확인, `~/.hermes/config.yaml`에 저장, `hermes mcp list`로 enabled 확인. 단
  Nous Portal 인증 자체는 아직 미완료라 실제 대화형 실행은 key/구독 확정 후.

`mcp_registry.json`(codex용 `-c` 주입 방식)에는 넣지 않음 — Order 125 이후 codex는
`--ignore-user-config`를 안 쓰고 `~/.codex/config.toml`을 직접 상속하는 구조로 바뀌어서,
registry 경유 주입이 현재 실제 dispatch 경로에서 안 쓰이는 걸 확인함(코드에 `-c
mcp_servers...` 호출 없음). 대신 codex 자체 config에 직접 등록.
