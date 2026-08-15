Run-ID: RUN-123-01

# ORDER 123 — MCP Dispatcher Generalization 결과

## 판정

**PASS.** TIKR 하드코딩과 GS 전용 resolver를 Git 정본 registry 기반 공통 경로로 통합했다. 격리 temp repository의 실제 dispatcher-generated `codex exec`에서 TIKR transcript와 GS 4개 sheet가 모두 `ok=true`로 재현됐다.

`COMPLETED` 문자열만으로 판정하지 않고 아래 DoD 실측 결과를 기준으로 PASS 처리했다.

## 변경 파일

- `mcp_registry.json` — tikr/gs enabled 설정, 환경변수 우선순위, 파일 검증 선언
- `scripts/order_dispatcher.py` — `load_mcp_registry()`, `resolve_mcp_config(name)`, `mcp_config_overrides()`
- `tests/test_order_dispatcher.py` — 일반 registry, 환경 override, invalid registry, enabled/disabled 회귀시험
- `ORDER_PROTOCOL.md` — registry 정본과 현재 executor 동작 반영
- `orders/123_mcp_dispatcher_generalization.md`
- `reports/123_report.md`

수정 전 백업은 Git 제외 패턴의 다음 파일로 생성했다.

- `scripts/order_dispatcher.py.bak_20260815_120213`
- `tests/test_order_dispatcher.py.bak_20260815_120213`

## Registry 구조

```json
{
  "version": 1,
  "mcp_servers": {
    "tikr": {"enabled": true, "command": {}, "args": [], "env": {}},
    "gs": {"enabled": true, "command": {}, "args": [], "env": {}}
  }
}
```

PC별 값은 registry에 하드코딩하지 않는다. 명시적 환경변수가 우선하고, 공용 fallback은 현재 Python과 `{AUTOAI_ROOT}`를 사용한다.

- TIKR: `TIKR_PYTHON`, `TIKR_MCP_SERVER`, `AUTOAI_ROOT`
- GS: `GS_PYTHON`, `GS_MCP_SERVER`, `GS_RSCRIPT`, `AUTOAI_ROOT`
- GS 전달 환경: `APPDATA`, `LOCALAPPDATA`, `USERPROFILE`, `R_USER`, `GS_RSCRIPT`

필수 실행파일/서버 스크립트가 없으면 command 생성 전에 fail-closed 한다.

## Dry-run

```text
order_id=123
executor=codex
status=VALIDATED
project=C:\lab\vsurf_capital\common
```

PC2 실측 registry 해석:

```text
enabled: tikr, gs
TIKR: C:\Python314\python.exe + C:\autoai\tikr-toolkit\tikr_mcp_server.py
GS:   C:\Python314\python.exe + C:\autoai\gs-toolkit\gs_mcp_server.py
R:    C:\Program Files\R\R-4.5.2\bin\Rscript.exe
generated -c pairs: 11
```

## 격리 temp repository 재현

### 1차 smoke

dispatcher가 생성한 격리 명령을 그대로 사용했다.

```json
{"tikr_ok":true,"ticker":"FORM","gs_ok":true,"rows":98,"cols":3,"tools":["mcp__tikr__tikr_company_overview","mcp__gs__gs_read_idx"]}
```

exit code 0, sandbox `workspace-write`, approval `never`, common만 `--add-dir`로 허용됨을 session header에서 확인했다.

### TIKR 111~117 + GS 122 전체 회귀

```json
{
  "tikr":{"ok":true,"segments":38,"chars":42687},
  "gs_read_bgdgs":{"ok":true,"rows":94,"cols":46,"warning":true},
  "gs_read_sggs":{"ok":true,"rows":95,"cols":24,"warning":true},
  "gs_read_idx":{"ok":true,"rows":98,"cols":3,"warning":true},
  "gs_read_bgdidx":{"ok":true,"rows":30,"cols":3,"warning":true}
}
```

- TIKR: NBIS transcript, 38 segments / 42,687 chars
- GS: `bgd_th` 94×46, `kidx-Q` 95×24, `kr_idx` 98×3, `etf_idx` 30×3
- GS payload의 R warning은 숨기지 않고 `warning=true`로 보존했다. 도구 payload는 모두 `ok=true`였다.
- 중첩 Codex가 전체 회귀의 다섯 read-only 호출을 한 차례 반복했다. 결과값은 동일했지만, 이는 향후 registry에 write MCP를 넣을 때 별도의 멱등성/승인 gate가 필요하다는 관찰사항이다.

Order 122의 `quantmod` 누락은 이번 PC2 실사용 환경에서 재현되지 않았다. 다만 해당 의존성 설치/관리 자체는 Order 지시대로 이번 변경 범위에 포함하지 않았다.

## 코드 검증

```text
python -m compileall -q scripts tests: PASS
python -m unittest discover -s tests -v: 64/64 PASS
```

추가된 핵심 회귀:

- enabled MCP를 서버별 분기 없이 자동 생성
- disabled MCP 제외
- PC별 환경변수 override 우선
- 서버 스크립트 누락 fail-closed
- 잘못된 registry version/shape 거부
- 기존 tikr 및 gs 인자 동시 보존

## Diff 요약

- 삭제: `resolve_gs_mcp_config()`와 `executor_command()`의 tikr/gs 개별 조립
- 추가: `resolve_mcp_config(name)` 공통 resolver
- 추가: registry의 모든 enabled MCP를 순회하는 `mcp_config_overrides()`
- 유지: `--ignore-user-config`, `approval_policy=never`, `windows.sandbox=elevated`, `workspace-write`, `--add-dir COMMON_ROOT`

## 남은 한계

1. `도구:` 행으로 필요한 MCP만 선택하지 않고 registry의 enabled MCP 전체를 주입한다.
2. Claude 분기는 기존 로컬 설정/allowlist 경로를 유지하며 이 registry를 사용하지 않는다.
3. Registry schema는 JSON Schema 파일로 별도 형식검증하지 않고 runtime validator와 단위테스트로 검증한다.
4. write MCP는 중첩 executor의 재호출 가능성 때문에 현재 registry에 추가하면 안 된다. read-only/멱등 도구가 기본 전제다.

## DoD

- [x] 백업
- [x] registry Git 정본
- [x] MCP별 dispatcher 분기 제거
- [x] dry-run
- [x] 격리 temp repo
- [x] TIKR 실제 재현
- [x] GS 4개 실제 재현
- [x] compile + 전체 64 tests
- [x] 기존 sandbox/approval 설정 보존
