Run-ID: RUN-113-01

# Order 113 — claude MCP access check

## Report §0

- 상태: DONE (부분: 도구 목록 접근 확인 / 실호출은 권한 게이트로 미완주)
- 좌표: structure_map 칸 N/A (배관 검증 아님)
- PC1 경로: `C:\lab\vsurf_capital\common\reports\113_report.md`
- 커밋: (dispatcher가 커밋)
- 요약: tikr MCP 도구는 이 claude 세션의 도구 인벤토리에 실제로 노출된다(codex의 `--ignore-user-config` 격리와 다름). 다만 `tikr_company_overview` 실호출은 하네스 권한 게이트에 막혀 결과를 받지 못했다.

## 1. 도구 목록 노출 여부

세션 시작 직후 시스템이 제공한 "deferred tools" 목록(ToolSearch로 스키마를 당겨와야 호출 가능한 미로딩 도구 인벤토리)에 `tikr` 관련 도구가 전부 이름으로 나타났다. 원문 그대로:

```
mcp__tikr__tikr_cache_permid
mcp__tikr__tikr_company_events
mcp__tikr__tikr_company_news
mcp__tikr__tikr_company_overview
mcp__tikr__tikr_estimates
mcp__tikr__tikr_financials
mcp__tikr__tikr_get_filing
mcp__tikr__tikr_get_report_doc
mcp__tikr__tikr_get_transcript
mcp__tikr__tikr_list_earnings_calls
mcp__tikr__tikr_list_filing_docs
mcp__tikr__tikr_list_filings
mcp__tikr__tikr_list_reports
mcp__tikr__tikr_news_article
mcp__tikr__tikr_search_company
mcp__tikr__tikr_trkdids
```

이 order 자체의 `도구:` 필드는 "없음"이었고 어떤 MCP도 명시적으로 요청되지 않았다. 그럼에도 위 목록이 자동으로 노출됐다는 것은, 112번 코드리뷰 결론(codex 분기만 `--ignore-user-config`로 격리되고 claude 분기는 격리 없이 그대로 실행된다)과 일치한다. 즉 이 claude(Bill) 세션은 `C:\Users\coatl\.codex\config.toml`(또는 대응하는 claude 설정)에 등록된 로컬 MCP 서버 목록을 codex 와 달리 그대로 이어받는다.

## 2. 스키마 로드

`ToolSearch(query="select:mcp__tikr__tikr_company_overview")` 호출로 해당 도구의 완전한 JSONSchema를 정상적으로 받았다:

```json
{"description": "회사 개요 — 거래소·통화 등 메타데이터.", "name": "mcp__tikr__tikr_company_overview", "parameters": {"properties": {"ticker": {"title": "Ticker", "type": "string"}}, "required": ["ticker"], "title": "tikr_company_overviewArguments", "type": "object"}}
```

이는 도구가 이름만 보이는 게 아니라 실제 호출 가능한 상태로 로드된다는 뜻이다.

## 3. 실호출 시도 — `tikr_company_overview(ticker="NBIS")`

호출을 실행했으나 다음 오류가 반환됐다(원문):

```
Claude requested permissions to use mcp__tikr__tikr_company_overview, but you haven't granted it yet.
```

이 세션은 Slack dispatcher가 기동한 비대화형(non-interactive) 실행이라 승인 프롬프트에 응답할 사용자가 없다. 도구 자체는 로드됐지만 하네스의 권한 게이트가 실행을 차단했다 — MCP 서버가 없거나 도구를 찾지 못해서가 아니라, 별도의 승인 레이어에 걸린 것이다. 지시("불가능하면 우회하지 않고 정직하게 기록")에 따라 같은 호출을 재시도하거나 승인을 우회하지 않았다.

## 4. 결론

- tikr 등 로컬 MCP 도구는 claude 실행 분기에서 codex와 달리 도구 인벤토리 수준까지는 실제로 도달한다 — 112번에서 코드로 확인한 비대칭이 실물로도 재현됨.
- 다만 "쓸 수 있다"의 의미를 실제 데이터 취득까지로 좁히면, 이 특정 비대화형 dispatcher 세션에서는 권한 승인 부재로 완전한 실호출·응답 수신까지는 이르지 못했다. 대화형 세션(사용자가 승인 프롬프트에 응답 가능한 경우)이라면 통과할 가능성이 높으나 본 실행에서 검증되지 않았다.

## 검증

- ToolSearch를 통한 스키마 로드: 성공 (위 §2).
- `mcp__tikr__tikr_company_overview(ticker="NBIS")` 실호출: 실패 — 권한 미승인 오류, 재시도 없음.
- 본 파일 외 다른 파일 수정·삭제 없음 (order 금지 사항 준수).
