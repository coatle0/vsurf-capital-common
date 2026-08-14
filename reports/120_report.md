Run-ID: RUN-120-01

# Order 120 forced-kill restart Git integrity validation

## 판정

PASS (격리 실측). 테스트 worker만 강제 종료한 뒤 완료 증거가 없음을 확인하고 격리 stale lock만 제거했다. 동일 task 재기동은 terminal `COMPLETED`를 정확히 한 번 기록하고 claimed→processed 이동 및 lock 해제로 끝났다. 운영 PID/lock은 변경하지 않았다.

## 시작 상태

- 시작 HEAD: `7eb1528b59af4963cda321e12506d92271f22789`
- 시작 `git status --short`: 출력 없음.
- 시작 `git diff --check`: 오류 없음.
- 운영 `.runtime/inbox/consumer.lock`과 `.runtime/order-120.lock`은 모두 `pid=20004`를 가리켰고, `Get-Process -Id 20004`에서 살아 있는 `python` 프로세스(시작 2026-08-14 08:17:18 +09:00)로 확인했다.
- 권한 제한으로 운영 프로세스 command line은 조회하지 못했다. 운영 consumer, Slack listener, 운영 lock은 종료·수정·삭제하지 않았다.

## 격리 좌표와 실제 명령

- 격리 임시 루트: `C:\lab\vsurf_capital\common\.runtime\order120-avqe4evm` (검증 뒤 삭제).
- task ID: `ORDER120-ISOLATED`; order lock ID: `T120`.
- 최초 worker: `C:\Python314\python.exe C:\lab\vsurf_capital\common\.runtime\order120_harness.py --child C:\lab\vsurf_capital\common\.runtime\order120-avqe4evm --mode initial`
- 강제 종료: 부모 harness의 `subprocess.Popen.kill()` (Windows TerminateProcess), 대상 PID 20808만 종료.
- 재기동: `C:\Python314\python.exe C:\lab\vsurf_capital\common\.runtime\order120_harness.py --child C:\lab\vsurf_capital\common\.runtime\order120-avqe4evm --mode restart`
- harness 실행: `python .runtime\order120_harness.py`

## 시간순 로그 (Asia/Seoul)

1. `2026-08-14T17:17:48.815+09:00` — 최초 worker PID 20808이 claimed 파일과 격리 `OrderLock`을 획득하고 READY 기록.
2. `2026-08-14T17:17:48.819+09:00` — 부모가 claim/lock 동시 존재를 관측.
3. `2026-08-14T17:17:48.824+09:00` — PID 20808 강제 종료 완료(exit code 1).
4. 재기동 전 대조: claimed=true, lock=true, outbox=null, completion file=false. terminal/완료 증거가 없고 부분 산출물도 없어 재실행 가능으로 판정.
5. 위 판정 뒤 격리 `order-T120.lock`만 제거하고 동일 task 재기동(PID 19256). 운영 lock은 건드리지 않음.
6. `2026-08-14T17:17:49.086+09:00` — 재기동 worker가 terminal outbox를 기록하고 claimed→processed archive 완료(exit code 0).
7. 종료 관측: claimed=false, processed=true, lock=false, outbox status=`COMPLETED`, completion count=1.

## 복구 판단과 부작용 대조

강제 종료 직후 last-result에 해당하는 격리 outbox가 없고 completion marker도 없었다. 따라서 완료 뒤 기록만 누락된 상태가 아니며, 격리 stale lock 제거 후 재실행 조건을 충족했다. 재기동 후 completion marker가 한 줄뿐이므로 완료 실행은 한 번이며, terminal outbox와 processed archive가 일치한다. Git diff에는 harness의 임시 작업 산출물이 나타나지 않았고 격리 루트 및 harness/result 파일은 삭제했다.

## Git 및 테스트 결과

- 종료 HEAD: `7eb1528b59af4963cda321e12506d92271f22789` (시작 HEAD와 동일).
- 종료 `git status --short`: `?? reports/120_report.md`만 존재. 의도한 보고서 외 추적/untracked/partial 파일 없음.
- `git fsck --no-progress` → exit 0.
- `git diff --check` → exit 0.
- `python -m unittest -v tests.test_order_inbox tests.test_order_inbox_consumer` → 32 tests, OK.
- `python -m unittest -v tests.test_order_dispatcher.ParseRequestTests.test_rejects_duplicate_lock` → 1 test, OK.
- 전체 결합 명령 `python -m unittest tests.test_order_inbox tests.test_order_inbox_consumer tests.test_order_dispatcher`는 35개 성공 표시 뒤 120초 timeout. 분리 실행 결과 `tests.test_order_dispatcher.CommitPendingRegistrationTests.test_commits_only_the_untracked_order_file`에서 멈추는 기존 환경 의존 hang을 확인했으며 성공으로 계산하지 않았다.
- 격리 임시 루트와 harness/result 파일은 모두 부재함을 확인했다.
- 최종 확인에서도 운영 PID 20004는 동일 시작 시각의 살아 있는 `python` 프로세스였고 두 운영 lock 내용은 시작 시점과 동일했다.

## 남은 위험과 제한

- lock에는 TTL/lease 또는 PID 생존 자동 판정이 없어 실제 장애 복구는 완료 증거를 사람이 대조한 뒤 stale lock을 수동 제거해야 한다.
- 외부 부작용이 비멱등이면 outbox/last-result 이전의 강제 종료만으로 안전 재실행을 단정할 수 없다. 이번 PASS는 외부 부작용이 없는 격리 task의 실측 결과다.
- 운영 프로세스 command line은 OS 권한 제한으로 확인하지 못했고, lock PID와 프로세스 이름·생존 상태로만 연속성을 확인했다.
- dispatcher 전체 suite의 위 commit 관련 테스트는 환경에서 timeout되어 전체 suite 완주 증거는 없다. lock 복구 직접 관련 테스트와 inbox/consumer suite는 통과했다.
- 사용자 지시에 따라 commit/push는 수행하지 않는다. commit hash 생성은 dispatcher 최종화 책임으로 남는다.
