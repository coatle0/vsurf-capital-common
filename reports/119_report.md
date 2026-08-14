Run-ID: RUN-119-01

# Order 119 forced-kill lock recovery validation

## 판정

PASS (격리 실측). 실행 중에는 atomic claim과 `OrderLock`이 동시 중복 실행을 차단했고, 강제 종료 뒤에는 claim과 lock이 의도대로 stale 상태로 남아 자동 재실행을 fail-closed로 막았다. 격리된 stale lock을 수동 제거한 뒤 동일 작업을 순차 재실행하여 processed 상태로 종결할 수 있었다.

## 사전 상태

- 테스트 전 `git status --short`: 출력 없음(깨끗한 작업 트리).
- 운영 경로는 읽기만 했다. `.runtime/inbox/consumer.lock`의 PID 20004는 `python` 프로세스로 살아 있었고, Order 119 실행 lock도 같은 살아 있는 PID를 가리켰다.
- 운영 `.runtime/inbox/claimed/C0BNWS9QKDK-1786692357.708739.json`, `.runtime/order-119.lock`, `.runtime/inbox/consumer.lock`은 변경하거나 제거하지 않았다.
- 구현 확인: pending→claimed는 `Path.rename` 단일 전이이고, `ConsumerLock`과 `OrderLock`은 `O_CREAT | O_EXCL`로 생성된다. 비정상 종료 시 context manager의 `__exit__`가 실행되지 않아 lock이 남으며 자동 stale 정리는 없다. 별도의 시간 기반 lease 구현은 없다.

## 격리 좌표와 명령

- 임시 루트: `C:\lab\vsurf_capital\common\.runtime\order119-xig68nmc` (검증 후 삭제).
- task_id: `ORDER119-ISOLATED`; order lock ID: `T119`.
- worker 명령: `python -c <격리된 pending 생성 → claim → OrderLock 획득 → 실행 시작 기록 → sleep 300초>`.
- kill 대상 PID: **22176**.
- kill 명령/방법: 부모 Python의 `subprocess.Popen.kill()`로 PID 22176만 Windows `TerminateProcess` 강제 종료.

## 시간순 증거 (Asia/Seoul)

1. `2026-08-14T16:27:57.446+09:00` — PID 22176이 `claimed/ORDER119-ISOLATED.json`과 `dispatcher/order-T119.lock` 획득 후 READY. 실행 시작 수 1.
2. `2026-08-14T16:27:57.496+09:00` — 동시 두 번째 claim 결과 `None`; 두 번째 `OrderLock` 획득은 `DispatchError`로 차단. 실행 시작 수는 1로 유지되어 동시 중복 없음.
3. `2026-08-14T16:27:57.501+09:00` — PID 22176 강제 종료 완료(exit code 1). 직후 claimed 파일=true, lock 파일=true, 실행 시작 수=1.
4. 격리 lock을 수동 제거한 뒤 같은 작업을 재실행. `2026-08-14T16:27:57.522+09:00` — outbox COMPLETED 기록 및 claimed→processed archive 완료; context 종료 후 lock=false, claimed=false, processed=true. 순차 실행 시작 수=2.
5. `2026-08-14T16:27:57.528+09:00` — 임시 루트 삭제 확인(`root_exists=false`).

## lock/claim 전후와 재실행 결과

| 시점 | claim | order lock | 실행 시작 수 | 결과 |
|---|---|---:|---:|---|
| worker 실행 중 | claimed 존재 | 존재 | 1 | 두 번째 claim/lock 차단 |
| 강제 종료 직후 | stale claimed 존재 | stale lock 존재 | 1 | 자동 중복 재실행 차단 |
| 수동 복구 후 | processed로 archive | 해제 | 2(순차) | 동일 작업 재실행/종결 가능 |

## 검증 및 정리

- `python -m unittest tests.test_order_inbox tests.test_order_inbox_consumer` → 32 tests, OK.
- `python -m unittest -v tests.test_order_dispatcher.ParseRequestTests.test_rejects_duplicate_lock` → 1 test, OK.
- 기존 crash-recovery 테스트가 로컬 `claude` CLI 설치 여부에 의존하던 문제를 발견해 request parsing만 mock하도록 최소 수정했다. 수정 뒤 관련 테스트는 통과했다.
- 테스트 child PID 22176은 종료됐고 임시 디렉터리는 삭제됐다.
- 테스트 후 운영 consumer PID 20004가 `python`으로 계속 살아 있음을 확인했다.

## 남은 위험/제한

- lock은 PID 생존 확인이나 TTL/lease가 없는 수동 복구 방식이다. 실제 stale lock 제거 전에는 해당 Order가 계속 차단된다.
- dispatcher 결과가 기록되기 전에 worker가 죽으면, 사람이 stale lock과 부작용 여부를 판정한 뒤 재실행해야 한다. 외부 작업이 비멱등이면 순차 재실행도 부작용을 중복시킬 수 있으므로 lock만 보고 자동 제거하면 안 된다.
- 운영 consumer의 명령줄은 권한 제한으로 조회하지 못했지만, lock의 PID와 해당 PID의 `python` 생존 상태를 전후에 확인했다.
- 사용자 지시에 따라 commit/push는 수행하지 않았다. 따라서 Order 원문의 “Git commit 생성/commit hash 회신” 항목은 dispatcher 최종화 전까지 미완이다.
