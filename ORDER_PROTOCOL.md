# ORDER_PROTOCOL — Slack → Order 실행 설계

> 정본: `C:\lab\vsurf_capital\common\ORDER_PROTOCOL.md` (PC1/PC2 공유, git 동기화 대상)
> Order 작성·실행의 단일 상세 정본이다. `AGENT_RULES.md`는 이 문서를 참조하는 요약 규약만 둔다.

## 1. 전체 흐름

```
[Slack #vsurf-agent-control]
        │  사람이 보낸 메시지 (Socket Mode push)
        ▼
① scripts/slack_bolt_listener.py        수신 전담 (빠름)
   - Socket Mode 실시간 수신
   - 기동 시 1회 REST catch-up (오프라인 중 놓친 메시지 보정)
        │  order_inbox.write_pending() 성공해야만 ACK
        ▼
.runtime/inbox/pending/<task_id>.json    디스크 영속화
        │
        ▼
Slack ACK 회신 ── "ACK [pc_id] RECEIVED task=<task_id>"

──────────────────────────────────────────────
        │  별도 프로세스, 5초 폴링
        ▼
② scripts/order_inbox_consumer.py        실행 전담 (느림, ①과 분리)
   claim(): pending → claimed (os.rename, 단일 소유 보장)
        │
   [EXECUTE ORDER NNN] 형식인가?
     아니오 → "NOTE: Order 형식 아님" 회신, processed/ 로 종료
     예 ↓
   outbox/<task_id>.json 이미 완료 상태로 있나? (중복 수신 방지)
     있음 → 재실행 없이 그 결과로 회신
     없음 ↓
③ scripts/order_dispatcher.py             실제 작업 수행
   parse_request()        executor/project 필드와 정본 Order 자동 탐색 검증
   OrderLock(order_id)    같은 order 동시 실행 차단
   ensure_clean_and_current()   git pull --ff-only, 트리 clean 확인
   executor 실행 (claude -p | codex exec)
   git diff 있음? → commit → push / 없음 → FAILED("완료 증명 안 됨")
        │
        ▼
outbox/<task_id>.json 갱신 (COMPLETED/FAILED/REJECTED)
        ▼
Slack 결과 회신 ── "COMPLETED [...] order NNN commit <hash>"
        ▼
claimed → processed/ 로 아카이브 (종결)
```

## 2. 핵심 설계 원칙

1. **ACK ≠ "봤다", ACK = "디스크에 안전하게 저장했다."** 저장 실패 시 ACK 자체를 보내지 않는다 — 리스너가 죽어있으면 무응답(유실 아님, 재전송하면 잡힘), 저장 성공 후 크래시해도 파일은 남아 재시작 시 이어진다.
2. **수신(①)과 실행(③)은 완전히 분리된 프로세스.** 느린 Order 하나가 도는 동안에도 ACK는 즉시 나간다.
3. **exactly-once 실행 보장.** `claim`(단일소유 rename) + `OrderLock`(order_id별 잠금, 크래시 시 stale lock을 일부러 남겨 사람이 치우게 함) + `outbox`(재실행 전 기존 결과부터 확인) 3중 방어. 애매하면 자동 재시도 대신 fail-safe.

## 3. 컴포넌트 ↔ 파일 매핑

| 컴포넌트 | 파일 | 역할 |
|---|---|---|
| 수신 | `scripts/slack_bolt_listener.py` | Socket Mode 실시간 수신 + 기동 시 catch-up |
| 수신 보조 | `scripts/slack_ack_watcher.py` | 위 리스너가 재사용하는 라이브러리(`process_message`/`fetch_new_messages`/cursor) |
| 영속 큐 | `scripts/order_inbox.py` | pending→claimed→outbox→processed 상태기계 (atomic rename/write) |
| 실행 조율 | `scripts/order_inbox_consumer.py` | inbox 소비, dispatcher 호출, Slack 회신, `ConsumerLock`(프로세스 중복 방지) |
| 실제 실행 | `scripts/order_dispatcher.py` | Order 검증·잠금·git·executor 호출의 단일 진실 공급원 |
| MCP 정본 | `mcp_registry.json` | Codex 격리 실행에 복원할 MCP와 PC별 환경변수 우선순위 선언 |
| Slack API | `scripts/slack_api.py` | `chat.postMessage` 등 공용 HTTP 호출 |
| 헤드리스 권한 | `.claude/settings.json` | claude 실행자용 범위 제한 허용목록(git push/commit/reset/rm 제외) |

## 4. Executor 분기 (`order_dispatcher.py`)

`parse_request()`가 Slack 메시지의 `executor:` 필드(`codex`/`claude`/`available`만 허용, 소문자 비교)를 읽는다. `available`은 Codex CLI가 있으면 codex, 없으면 claude를 선택한다. 실제 분기는 두 함수에서 일어난다.

```python
# executor_prefix(): 실행 파일 경로 해석
codex  → node + codex.js 절대경로 직접 지정 (npm .cmd shim은 CreateProcess가 직접 못 띄움)
claude → shutil.which("claude.exe")

# executor_command(): 명령줄 조립 — 진짜 분기점
if executor == "codex":
    [*prefix, "exec", "-C", project, "--ignore-user-config",
     "-c", 'approval_policy="never"', "-c", 'windows.sandbox="elevated"',
     "-c", <mcp_registry.json의 enabled MCP 설정>,
     "--add-dir", COMMON_ROOT, "--sandbox", "workspace-write",
     "--output-last-message", summary_file, prompt]
else:  # claude
    [*prefix, "-p", prompt]
```

**claude**: `claude.exe -p <prompt>`로 실행한다. `.claude/settings.json`의 범위 제한 허용목록을 사용하며, TIKR 도구 로드와 실호출 완주를 확인했다(Orders 113, 115, 117).

**codex**: Node로 `codex.js`를 직접 실행한다. `--ignore-user-config`로 사용자 설정을 격리한 뒤 `approval_policy="never"`와 `windows.sandbox="elevated"`를 CLI `-c`로 복원하고, `workspace-write`와 `--add-dir COMMON_ROOT`로 쓰기 범위를 제한한다. `mcp_registry.json`의 enabled 항목은 `resolve_mcp_config(name)`이 PC별 환경변수 우선으로 해석하고 공통 로직이 `mcp_servers.<name>.*` 인자를 생성한다. 새 MCP는 dispatcher 분기 대신 registry와 회귀시험을 추가한다. Order의 `도구:` 행은 아직 선택적 로딩 필터가 아니며 enabled MCP 전체가 격리 실행에 주입된다.

## 5. 메시지 포맷

```
[EXECUTE ORDER 100]
executor: claude | codex | available
project: <C:\lab 아래 절대경로, git repo>

--- ORDER BODY ---
번호: NNN
제목: 파일명에 사용할 제목
...
--- END ---
```

- 신규 발주는 위 **Order 100 intake + ORDER BODY** 형식만 사용한다. 외부 Slack 메시지에 `order:` 필드를 넣지 않는다.
- `executor`와 `project`는 필수다. `project`는 존재하는 Git 저장소이자 `C:\lab` 아래 절대경로여야 한다.
- consumer가 BODY의 번호·제목을 검증해 `orders/NNN_제목.md`를 등록하고, 내부적으로 정본 경로를 붙인 직접 실행 메시지로 변환한다. 번호 중복, marker/필수 본문 필드 누락은 REJECTED다.
- Slack이 마지막 줄에 signature를 붙여도 parser가 executor/project 값과 BODY 경계를 방어적으로 정리한다(Orders 108·109).

## 6. 현재 구현과 제한 (2026-08-14 기준)

- **`executor: bill` 미지원** — 조직 내 Claude Code 실명("Bill")이 별칭으로 안 먹힘, `claude`만 인식.
- **PC1 미설정** — 이 전체 구조는 PC2(`codex-pc2`)에만 구축됨.
- **복수 프로젝트 동시 실행 불가** — consumer가 완전 순차 처리, `dispatch()`가 최대 3600초 블로킹.
- **단일 프로젝트 분할처리 미지원** — Order 1건 = dispatch 1회 = commit 1회가 원자 단위, sub-task 분할·병렬화 개념 없음.
- **MCP 주입은 실행자별 비대칭** — Codex는 격리 뒤 Git 정본 `mcp_registry.json`의 enabled MCP를 공통 로직으로 주입한다. Claude는 로컬 설정을 이어받되 `.claude/settings.json` 허용목록의 적용을 받는다. `도구:` 행을 선택적 MCP 로딩으로 변환하는 기능은 아직 없다.
- **강제 종료 자동 복구 없음** — claim과 lock은 fail-closed로 남는다. TTL/lease/PID 생존 판정이 없으므로 outbox·last-result·외부 부작용을 사람이 확인한 뒤 stale lock을 수동 제거해야 한다. 비멱등 외부 작업은 안전 재실행을 보장하지 않는다(Orders 119·120).

해결됨(2026-08-12, COO 작업지시 5건 중 1·2):
- ~~발신자 화이트리스트 없음~~ → `order_senders.json`(git 등재, user ID만) + `order_inbox_consumer.py`의 `process_pending()`이 dispatch 이전에 검사. 목록이 비었거나 읽기 실패해도 fail-closed(전원 거부). 목록 밖 발신자는 `REJECTED [task_id]: sender not allowed`로 명시 회신, dispatcher는 아예 호출 안 됨.
- ~~예약작업 미등록~~ → `VSURF-Slack-Bolt-PC2`/`VSURF-OrderConsumer-PC2` 등록(AtLogOn, coatle 계정). 스크립트 자체에 self-heal `while` 루프 내장(Task Scheduler의 restart-on-failure가 수동 시작 인스턴스엔 안 먹히는 걸 실측 확인했기 때문). consumer는 크래시 시 stale lock을 자동으로 안 지우고 사람이 치울 때까지 재시도만 반복(의도적).
- ~~Slack 원문 미전달~~ → `build_prompt()`가 task_id와 원문을 verbatim으로 전달한다. Order 100 intake는 consumer가 BODY를 정본 파일로 먼저 등록한다.

## 7. 운영 이력

- 2026-08-09: OpenACP를 핵심 경로에서 제거(Windows daemon 미지원, `/health`·`/adapters` 404, libuv assertion, 예약작업 삭제·프로세스 정지 확인).
- 2026-08-09: durable inbox + exactly-once consumer + Slack Bolt 리스너 신규 구축, claude 헤드리스 실행 최초 성공(Order 003, commit `c687c0d`).
- 2026-08-12: Order 100(loop_proof) 실제 COO 발행 → 완주 확인(commit `aacd2fc5`). Order 004는 형식 오류 2건으로 미실행.
- 2026-08-12: COO 작업지시(파이프라인 보강 5건) 착수. 작업 1(재부팅·크래시 생존) 완료, 작업 2(발신자 화이트리스트) 완료.
- 2026-08-13: Codex Windows 설정을 CLI에서 제한적으로 복원해 쓰기 경로를 해결(Orders 107·110). signature parser 실경로 완주(Orders 108·109).
- 2026-08-14: Codex/Claude TIKR end-to-end 완주(Orders 114~117), 동시 중복 차단과 강제 종료 후 수동 stale-lock 복구를 격리 실측(Orders 118~120).
