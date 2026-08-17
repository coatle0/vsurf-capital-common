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
11. **Grok 로그인 완료** — `grok login --device-auth`로 코드 발급, 사람이 브라우저에서
    승인 → `Signed in as coatle0@gmail.com` 확인 (2026-08-16). 시행착오: device code가
    짧은 TTL을 가져 미리 발급해두면 만료됨(`Error: Device code expired`) — 승인 직전에
    발급해야 함.
12. **[CIO 지시] 모든 실행의 home/cwd = `C:\lab`으로 통일** (Grok·Hermes 공통). 이 지시를
    따르는 과정에서 핵심 원인 하나를 잡음: 헤드리스 실행을 `C:\lab` 밖(예: OS 임시 폴더)의
    낯선 경로에서 파일쓰기 프롬프트와 함께 돌리면 **무한 대기**했다(60초+, stdout/stderr/
    debug 로그 전부 무출력, `tasklist`로는 프로세스 생존 확인 — codex UAC 이슈와 같은
    "파이프 뒤에 숨은 프롬프트" 패턴으로 추정). `--cwd C:\lab`(또는 그 하위)로 바꾸자
    같은 파일쓰기 프롬프트가 41초 만에 정상 완료됨. 근본 원인은 미확정(추정)이지만,
    **"C:\lab 기준"이 실측으로 통과 조건이라는 것은 확정**.
13. **Project trust는 문서상 별개 축임을 확인** — `--allow`/`--deny` CLI 플래그는 trust
    상태와 무관하게 항상 강제 적용된다고 공식 번들 문서(`22-permissions-and-safety.md`)에
    명시. 실측(§ 아래)도 이를 뒷받침 — trust를 별도로 해결하지 않고 명시적 플래그만으로
    파일쓰기가 정상 동작했다. `.claude/settings.json` 자동상속 여부는 미확정으로 남겨두고,
    codex/claude와 동일하게 **매 호출마다 명시적 `--allow`/`--deny`를 넘기는 방식**으로
    설계 방향을 확정(감사 가능성도 더 높음).
14. **실측: C:\lab 기준 헤드리스 파일쓰기 성공**
    ```
    grok -p "Write the exact text 'grok-write-ok' to a new file named write_test.txt ..." \
      --cwd "C:\lab\_grok_scratch_test" --permission-mode dontAsk \
      --allow 'Write' --allow 'Edit' --allow 'Read' \
      --deny 'Bash(git push*)' --deny 'Bash(rm *)' --output-format json
    → {"text": "...Created write_test.txt with the text grok-write-ok.", "stopReason":"end_turn", ...}
    파일 실제 내용: grok-write-ok (정확히 일치). cost: $0.056/call. 테스트 후 정리(삭제) 완료.
    ```
15. **부가 발견 (차단 아님, 참고)**: 매 세션 시작마다 `global/orca-status` 훅(사용자
    레벨 `~/.claude/settings.json`의 기존 Orca 훅 인프라, Claude 호환 스캔으로 Grok에도
    상속됨)이 실패한다(exit code 1, CLIXML 에러) — fail-open이라 차단은 안 하지만 세션당
    ~9초 지연을 유발. Bill이 만든 것 아님, 별도 손 안 댐.
16. **부가 발견**: `C:\lab\.git`이 완전히 빈 디렉토리(HEAD 없음, 깨진 repo) — `grok`이
    `isGitRepo:false, gitRoot:null`로 정확히 인식함. 손 안 댐, 기록만.
17. **[2026-08-17] Hermes 배관(plumbing) — API key 없이 검증 완료.** "인증·모델 품질"
    (실제 xAI 키 필요, 아직 없음)과 "배관"(codex의 커스텀 provider 라우팅 메커니즘 자체)은
    분리 가능하다는 판단 하에, 로컬 mock OpenAI Responses API 서버(격리 scratch, 실
    config.toml 미변경 — 전부 `-c` CLI 플래그로만)로 실측:
    ```
    -c model_providers.hermes_mock.base_url="http://127.0.0.1:PORT/v1"
    -c model_providers.hermes_mock.wire_api="responses"
    -c model_providers.hermes_mock.env_key="MOCK_XAI_KEY"
    -c model_provider="hermes_mock"
    ```
    결과: `codex` 최종 출력 = `mock-hermes-ok` (mock이 반환하도록 설계한 문자열과 정확히
    일치). 확인된 것:
    - `Authorization: Bearer <MOCK_XAI_KEY 값>` 헤더 정상 구성 → `env_key` 자격증명
      배선 정상
    - 커스텀 `base_url`로 실제 HTTP 요청 전송 → provider 라우팅 정상
    - Responses API 요청 바디 형식 정상(`model/instructions/input/tools/...`)
    - SSE 스트림 파싱 정상(다만 정확한 이벤트 시퀀스가 필요 — 아래 참고)
    시행착오(전부 실측, 최신 codex 0.147.0 기준):
    - `wire_api="chat"`는 **더 이상 미지원** — 반드시 `"responses"`. 확인차 조사한 결과
      xAI도 `/v1/responses`를 지원하며 오히려 **레거시 `/v1/chat/completions`보다 권장**
      — 호환성 문제 없음.
    - Responses API는 **평문 JSON이 아니라 SSE 스트림** 필요. 최소 시퀀스:
      `response.created` → `response.in_progress` → `response.output_item.added` →
      `response.content_part.added` → `response.output_text.delta` →
      `response.output_text.done` → `response.content_part.done` →
      `response.output_item.done` → `response.completed`. 이 중 `output_item.added`
      없이 `output_text.delta`만 보내면 `OutputTextDelta without active item` 에러로
      텍스트가 유실됨(응답 자체는 실패하지 않고 continue).
    - codex는 세션 시작 시 `GET /v1/models`로 모델 메타데이터를 먼저 조회한다. mock이
      이걸 못 받쳐줘도(404/스키마 불일치) **치명적이지 않음** — "fallback metadata"
      경고만 내고 정상 진행.
    - **남은 것은 진짜 xAI 키로 진짜 응답 품질을 보는 것뿐** — 배관 자체는 이제 재검증
      불필요.

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

1. ~~xAI Grok 구독/인증~~ — **완료.** `coatle0@gmail.com`으로 device-auth 로그인 성공
   (2026-08-16).
2. ~~Grok CLI 프로젝트 신뢰(trust) 승인~~ — **불필요로 판명.** `--allow`/`--deny` 명시적
   플래그는 trust 상태와 무관하게 항상 적용됨(문서+실측 확인). trust 자체를 해결하지 않고
   진행.
3. ~~Grok용 scoped 권한 정책 검토·승인~~ — 1차 설계는 Bill이 codex/claude와 동일한 방식
   (매 호출 명시적 `--allow`/`--deny`)으로 확정, 실 Order 종단검증 시 최종본 리뷰 요청
   예정.
4. ~~Hermes 호스팅 방식 결정~~ — **해소됨.** Hermes endpoint를 Grok(api.x.ai)로 재사용하기로
   확정(CIO 지시, 2026-08-16). 로컬 GPU/외부 호스팅 계정 불필요, 1번의 Grok API key만
   있으면 됨.
5. ~~모든 실행 home/cwd 통일~~ — **완료.** CIO 지시로 `C:\lab`으로 확정, 실측으로 이게
   진짜 통과 조건이었음도 확인됨(§1-12,14).

---

## 4. 병목 (진행 막는 지점, 2026-08-16 갱신 — 전부 해소)

~~Grok 인증~~, ~~Project trust~~, ~~Hermes 호스팅~~, ~~home/cwd 확정~~ 전부 해소됨.
남은 건 실제 코드 통합(§2) — `order_dispatcher.py`에 `executor="grok"`/`"hermes"` 분기
추가 + 실 Order 종단검증. 이건 별도 지시 대기 없이 다음 세션에서 바로 착수 가능한
상태.
