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
   OpenAI-호환 엔드포인트를 붙일 수 있음(공식 지원).
10. **[정정, CIO 지시] Hermes endpoint = Grok(api.x.ai) 재사용으로 확정** — 별도 Hermes
    호스팅(로컬 GPU/외부 provider)을 구하지 않는다. `https://api.x.ai/v1`이 OpenAI-호환
    chat completions 엔드포인트임을 확인(`base_url=https://api.x.ai/v1`, SDK 그대로
    호환, 모델 예: `grok-4.5`). 즉 `model_providers.hermes`에
    `base_url="https://api.x.ai/v1"`, `wire_api="chat"`, `env_key`에 Grok API key를
    연결하면 끝 — **로컬 GPU도 별도 호스팅 계정도 불필요.** Grok 구독 하나로 (a) 네이티브
    Grok CLI 실행기, (b) codex 하니스 기반 "hermes" 실행기(Order 123 MCP registry 상속)
    두 경로가 동시에 풀린다. 기존 병목 #2(호스팅 방식 결정)는 이걸로 해소됨 — §4 갱신.

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
4. ~~Hermes 호스팅 방식 결정~~ — **해소됨.** Hermes endpoint를 Grok(api.x.ai)로 재사용하기로
   확정(CIO 지시, 2026-08-16). 로컬 GPU/외부 호스팅 계정 불필요, 1번의 Grok API key만
   있으면 됨.

---

## 4. 병목 (진행 막는 지점, 2026-08-16 갱신)

1. **Grok 인증만 남음** — Grok API key/로그인 없이는 Grok CLI `-p`도, Hermes(codex
   model_providers) 경로의 `env_key`도 둘 다 막힌다. 이 하나가 두 실행기 전부의 유일한
   남은 병목. 설치까지가 Bill 권한 범위의 끝 — 인증은 사람이 직접(브라우저 OAuth 또는
   `grok login --device-auth`로 코드 발급 후 사람이 승인) 해야 함.
2. ~~Hermes 호스팅 방식 미정~~, ~~로컬 추론 런타임 부재~~ — Grok endpoint 재사용으로 해소.
