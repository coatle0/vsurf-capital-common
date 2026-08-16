# Hermes(Nous Hermes)·Grok CLI 도입 — 실행 분담

> 작성: Bill (Claude, PC2) · 2026-08-16
> 목적: 토큰 사용 급증 대응 — codex/claude 외 실행기(Grok CLI, Hermes)를 VSURF Order 파이프라인에
> 추가해 분산한다. 최종형태: Grok 구독+CLI 설치, Hermes 설치(기존 Bill MCP 상속) → Slack 경유
> Order 수행 가능 상태.

---

## 1. Bill이 지금 실행 완료한 것 (실측)

1. **Grok CLI 설치 완료** — `npm i -g @xai-official/grok`, 3 packages, 약 54초.
   검증: `grok --version` → `grok 1.0.4 (d846eb93d9)`, `where grok` →
   `C:\Users\coatl\AppData\Roaming\npm\grok(.cmd)`.
2. **헤드리스 실행 모드 확인** — `grok -p "<prompt>"` (single-turn, stdout 출력 후 종료).
   `claude -p` / `codex exec`와 동일한 패턴 — dispatcher 통합 시 기존 `executor_command()`
   구조 그대로 재사용 가능.
3. **MCP 관리 서브커맨드 확인** — `grok mcp list/add/remove/enable/disable/doctor`.
4. **★ MCP 자동 상속 확인** — `grok inspect` 실행 결과, 별도 설정 없이 **기존 Claude MCP 5종을
   그대로 인식**:
   ```
   MCP Servers (5)
   └ telegram (stdio)           plugin: telegram
   └ tikr (stdio)               ~/.claude.json [claude]
   └ dart (stdio)               ~/.claude.json [claude]
   └ telegram-mcp (stdio)       ~/.claude.json [claude]
   └ telegram-research (stdio)  ~/.claude.json [claude]
   ```
   "Bill에 도입돼 있는 MCP를 상속" 요구사항이 Grok 쪽에서는 추가 작업 없이 이미 충족됨.
5. **권한/샌드박스 구조 확인** — `Project trusted: no`, `Permissions: 0 loaded`(아직 미설정),
   `--sandbox <PROFILE>`(env `GROK_SANDBOX`), `--permission-mode`
   (`default/acceptEdits/auto/dontAsk/bypassPermissions/plan`). headless dispatcher 용도로는
   `bypassPermissions`가 아니라 `dontAsk` + 별도 allow/deny 정책 조합이 codex/claude에
   적용한 "위험 우회 금지" 원칙과 일치.
6. **로그인/구독 시도 안 함** — `grok login`은 브라우저 인증 또는 API key(console.x.ai)가
   필요해 사용자 계정 행위이므로 손대지 않음.
7. **Hermes 정체 확정** — Nous Research의 open-weight 모델. **그 자체로는 CLI/에이전트가
   아니다.** OpenAI-호환 엔드포인트(`/v1/chat/completions`)를 통해 서빙돼야 codex 같은
   기존 실행기가 붙을 수 있음.
8. **로컬(PC2) 추론 런타임 부재 확인** — `where ollama`, `where vllm` 둘 다 미설치.
9. **codex CLI의 커스텀 provider 지원 조사 완료** — `~/.codex/config.toml`의
   `[model_providers.<id>]` 블록(`base_url`, `wire_api`, `env_key`)으로 임의의
   OpenAI-호환 엔드포인트를 붙일 수 있음(공식 지원). 즉 Hermes 엔드포인트만 확보되면
   **codex 실행 경로를 그대로 재사용**해 Order 123에서 만든 MCP registry 메커니즘까지
   같이 상속시킬 수 있다 — 새 하니스를 따로 만들 필요 없음.

---

## 2. Bill이 사용자 결정 이후 실행 가능한 것 (미착수 — 코드 미작성)

검증 불가능한 코드를 미리 작성하지 않는다(이 프로젝트의 실측 원칙). 아래는 endpoint/승인이
갖춰지면 바로 착수할 설계다.

- **Grok**: `order_dispatcher.py`에 `executor="grok"` 분기 추가 — `grok -p` 호출,
  `.grok/` 쪽 scoped allow/deny 정책 파일 설계(`.claude/settings.json` 패턴과 동일하게
  git push/commit/reset 등 deny). 격리 temp repo에서 STEP 0~2 방식 사전검증 후 실 Order로
  종단검증.
- **Hermes**: endpoint 확정 후 `config.toml`에 `[model_providers.hermes]` 추가,
  `order_dispatcher.py`에 `executor="hermes"` 분기(codex 실행 경로 재사용) 추가. 동일하게
  격리 temp repo 사전검증 → 실 Order 종단검증.

---

## 3. 사용자(COO/CIO)가 해야 하는 것

1. **xAI Grok 구독/인증** — console.x.ai에서 API key 발급, 또는 `grok login` 브라우저 인증
   (사람이 직접 있어야 하는 1회성 작업).
2. **Grok CLI 프로젝트 신뢰(trust) 승인** — headless 사용 전 최초 1회 결정 필요
   (`grok inspect` 결과 현재 "Project trusted: no").
3. **Grok용 scoped 권한 정책 검토·승인** — Bill이 설계안을 올리면 그 allow/deny·
   permission-mode를 최종 승인.
4. **Hermes 호스팅 방식 결정** (순수 인프라/비용 의사결정, Bill이 대신 정할 수 없음):
   - 로컬 GPU(Ollama/vLLM) — 모델 크기별 VRAM/디스크(수십 GB) 필요, 하드웨어 확보·비용.
   - 외부 호스팅 provider(Hermes 서빙하는 API 서비스) — 계정 개설·과금·API key.
5. Hermes 엔드포인트·API key 확정되면 Bill에게 전달.

---

## 4. 병목 (진행 막는 지점)

1. **Grok**: 인증(로그인/API key) 없이는 `-p` 실행 자체가 막힌다 — 설치까지가 Bill 권한
   범위의 끝.
2. **Hermes**: "설치"라는 표현 자체가 성립하지 않는다(CLI가 아니라 모델). 호스팅 방식이
   정해지지 않으면 다음 단계(코드 작성) 자체가 검증 불가능한 추측이 되어 이 프로젝트의
   "실측 필수·추정 금지" 원칙을 어기게 된다 — 결정이 선행돼야 함.
3. 로컬(PC2)에 추론 런타임이 전혀 없어, 로컬 호스팅을 선택할 경우 런타임 설치·모델 다운로드
   부터 새로 시작해야 한다.
