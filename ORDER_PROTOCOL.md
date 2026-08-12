# ORDER_PROTOCOL — Slack → Order 실행 설계

> 정본: `C:\lab\vsurf_capital\common\ORDER_PROTOCOL.md` (PC1/PC2 공유, git 동기화 대상)
> `AGENT_RULES.md`의 "Orders"/"Slack 실행 Order" 절을 대체·구체화한다. OpenACP는 이 경로에서 제외됨(2026-08-09).

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
   parse_request()        executor/order/project 필드 검증
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
| Slack API | `scripts/slack_api.py` | `chat.postMessage` 등 공용 HTTP 호출 |
| 헤드리스 권한 | `.claude/settings.json` | claude 실행자용 범위 제한 허용목록(git push/commit/reset/rm 제외) |

## 4. Executor 분기 (`order_dispatcher.py`)

`parse_request()`가 Slack 메시지의 `executor:` 필드(`codex`/`claude`/`available`만 허용, 소문자 비교)를 읽고, 실제 분기는 두 함수에서 일어난다.

```python
# executor_prefix(): 실행 파일 경로 해석
codex  → node + codex.js 절대경로 직접 지정 (npm .cmd shim은 CreateProcess가 직접 못 띄움)
claude → shutil.which("claude.exe")

# executor_command(): 명령줄 조립 — 진짜 분기점
if executor == "codex":
    [*prefix, "exec", "-C", project, "--ignore-user-config",
     "--add-dir", COMMON_ROOT, "--sandbox", "workspace-write",
     "--output-last-message", summary_file, prompt]
else:  # claude
    [*prefix, "-p", prompt]
```

**claude**: 프로젝트를 `hasTrustDialogAccepted`로 신뢰 등록 + `.claude/settings.json` 허용목록만 있으면 헤드리스로 정상 작동 확인됨(2026-08-09, 2026-08-12 실측).

**codex**: 현재 미작동. `~/.codex/config.toml`의 `[windows] sandbox = "elevated"`가 Windows에서 write 가능한 샌드박스를 구성하는 데 필요한데, `--ignore-user-config`(전역의 위험한 `sandbox_mode = "danger-full-access"` / `approval_policy = "never"`를 걸러내기 위해 의도적으로 넣은 플래그)가 이것까지 함께 날려버려 모든 실행이 `blocked by policy`로 거부됨. codex 전용 범위 제한 config가 별도로 필요(미해결).

## 5. 메시지 포맷

```
[EXECUTE ORDER NNN]
executor: claude | codex | available
order: <orders/NNN_*.md 절대경로>   (생략 가능 — 생략 시 NNN으로 자동 탐색)
project: <C:\lab 아래 절대경로, git repo>
```

## 6. 알려진 제약·미해결 항목 (2026-08-12 기준)

- **`executor: bill` 미지원** — 조직 내 Claude Code 실명("Bill")이 별칭으로 안 먹힘, `claude`만 인식.
- **`order: NNN`(번호만) 오작동** — 필드 생략 시엔 번호로 자동 탐색되지만, 번호만 채워 넣으면 "경로 불일치"로 REJECTED. 생략하거나 전체 경로를 써야 함.
- **원문 Slack 메시지가 executor에게 안 넘어감** — `build_prompt()`가 정본 Order 파일 경로만 알려주고 Slack 메시지 원문은 전달하지 않음. 지시가 Slack 메시지 본문에만 있는 경우(사전에 커밋된 Order 파일이 없는 경우) executor가 `.runtime/inbox/`를 직접 뒤져 원문을 복구해야 했음(Order 100 실측, 처리 시간 6분+ 소요의 주원인).
- **PC1 미설정** — 이 전체 구조는 PC2(`codex-pc2`)에만 구축됨.
- **복수 프로젝트 동시 실행 불가** — consumer가 완전 순차 처리, `dispatch()`가 최대 3600초 블로킹.
- **단일 프로젝트 분할처리 미지원** — Order 1건 = dispatch 1회 = commit 1회가 원자 단위, sub-task 분할·병렬화 개념 없음.
- **codex 경로 미작동** — 위 4절 참조.

해결됨(2026-08-12, COO 작업지시 5건 중 1·2):
- ~~발신자 화이트리스트 없음~~ → `order_senders.json`(git 등재, user ID만) + `order_inbox_consumer.py`의 `process_pending()`이 dispatch 이전에 검사. 목록이 비었거나 읽기 실패해도 fail-closed(전원 거부). 목록 밖 발신자는 `REJECTED [task_id]: sender not allowed`로 명시 회신, dispatcher는 아예 호출 안 됨.
- ~~예약작업 미등록~~ → `VSURF-Slack-Bolt-PC2`/`VSURF-OrderConsumer-PC2` 등록(AtLogOn, coatle 계정). 스크립트 자체에 self-heal `while` 루프 내장(Task Scheduler의 restart-on-failure가 수동 시작 인스턴스엔 안 먹히는 걸 실측 확인했기 때문). consumer는 크래시 시 stale lock을 자동으로 안 지우고 사람이 치울 때까지 재시도만 반복(의도적).

## 7. 운영 이력

- 2026-08-09: OpenACP를 핵심 경로에서 제거(Windows daemon 미지원, `/health`·`/adapters` 404, libuv assertion, 예약작업 삭제·프로세스 정지 확인).
- 2026-08-09: durable inbox + exactly-once consumer + Slack Bolt 리스너 신규 구축, claude 헤드리스 실행 최초 성공(Order 003, commit `c687c0d`).
- 2026-08-12: Order 100(loop_proof) 실제 COO 발행 → 완주 확인(commit `aacd2fc5`). Order 004는 형식 오류 2건으로 미실행.
- 2026-08-12: COO 작업지시(파이프라인 보강 5건) 착수. 작업 1(재부팅·크래시 생존) 완료, 작업 2(발신자 화이트리스트) 완료.
