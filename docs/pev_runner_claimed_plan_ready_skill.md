# SKILL — Order 실행 CLAIMED·PLAN_READY 회신

- 기능명: CLAIMED / PLAN_READY 회신 (PEV Runner 도입 1·2단계)
- 버전: v1.0
- 상태: ACTIVE
- Owner: COO
- 적용 대상: `#vsurf-agent-control`을 통해 발행되는 모든 정식 Order (executor 무관 — codex/claude/grok 전부)
- Source: 설계 검토(GO_WITH_CHANGES) → 실행계획 → `#vsurf-code-reports` 라이브 검증(Order 149·150)
- Git 경로: `scripts/order_inbox_consumer.py` (`extract_plan_summary`/`format_plan_ready`/claim 직후 reply 삽입)
- 관련 커밋: `0384e04`(CLAIMED), `4c69184`(PLAN_READY)
- 관련 정책: `GOVERNANCE_POLICY.md` §8

## 무엇이 바뀌었나

기존엔 Order 발행 후 회신이 두 번뿐이었다: 수신 즉시 뜨는 일반 ACK(`slack_ack_watcher.py`, 이건 Order인지 아직 모르는 시점), 그리고 실행이 끝난 뒤 뜨는 `COMPLETED`/`FAILED`. 그 사이에 "정말 claim됐는지", "이 Order를 뭘로 이해하고 있는지"를 확인할 방법이 없었다.

이제 claim 직후 두 회신이 추가로 뜬다.

```text
[CLAIMED ORDER NNN] run_id=<task_id> executor=<codex|claude|grok> status=CLAIMED
[PLAN_READY ORDER NNN] run_id=<task_id>
objective: <Order 본문 "목적:" 필드>
execution_steps: <Order 본문 "작업:" 블록 전체>
prohibitions: <Order 본문 "금지:" 필드>
expected_outputs: <Order 본문 "DoD:" 필드>
decision: READY_TO_EXECUTE
```

## 사용법 (발주자 입장)

아무것도 바꿀 필요 없다. 기존 Order 발행 형식(`orders/100_order_intake.md` §입력 형식) 그대로 쓰면 자동으로 두 회신이 뜬다. 새 필드도, 새 지시문도 없다.

## 입력·출력

- **입력**: Order 본문의 표준 필드(`목적:`/`작업:`/`금지:`/`DoD:`) — 이미 모든 Order가 쓰고 있는 형식.
- **출력**: 위 두 Slack 회신. `PLAN_READY`는 원문 필드를 그대로 옮긴 것이지 요약·재작성이 아니다.

## 제약·실패조건

- **가시성만 제공한다. 실행을 막지 않는다.** `decision: READY_TO_EXECUTE`는 항상 고정값이고, 실행 대기·승인 게이트는 없다. 발행 이후 막는 지점은 여전히 없다 — 승인은 발행 자체가 승인이라는 기존 원칙 유지(`GOVERNANCE_POLICY.md` §8).
- Order 본문에 해당 필드가 없으면 그 줄은 그냥 생략된다(에러 아님) — 전부 없으면 `decision` 한 줄만 뜬다.
- 등록 직후 canonical 파일을 못 읽으면(예: 잘못된 번호로 발행됐을 때) `PLAN_READY`는 조용히 생략되고, 뒤이어 정상 경로의 `REJECTED` 회신이 뜬다 — `PLAN_READY` 자체가 검증기가 아니다.
- `target_pc`·`base_sha` 필드는 의도적으로 뺐다: 전자는 코드베이스에 아직 개념이 없고, 후자는 이 모듈이 git을 직접 호출해야 해서 범위를 벗어난다.

## 검증

- `tests/test_order_inbox_consumer.py`: `PlanSummaryTests`(5건) + happy-path 3회신 순서·내용 검증
- 라이브: Order 149(`[CLAIMED ORDER 149]` 실측), Order 150(`CLAIMED`→`PLAN_READY`→종결 순서·내용 전부 실측)
- 전체 테스트 스위트 118/118 PASS
