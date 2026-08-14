발행일: 2026-08-14
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 120
제목: forced-kill-restart-git-integrity-validation
목적: Order 119에서 확인한 강제 종료·stale lock 상태를 출발점으로, 격리 환경에서 안전한 복구 절차와 재기동 후 Git 작업트리 무결성을 실측하여 Phase 2 §6-6 rollback/안전중단 검증을 마무리한다.
대상: order_inbox_consumer, order_dispatcher, claim·outbox·processed·lock 복구 경로 및 Git 작업트리
작업:
1. 시작 전 현재 HEAD, `git status --short`, `git diff --check`, 활성 운영 consumer/worker PID와 관련 lock 상태를 기록한다.
2. 운영 consumer·Slack listener·무관한 프로세스에는 손대지 말고, 저장소 내부 임시 루트를 사용하는 격리 환경에서 긴 실행 테스트 worker를 시작하여 claim과 OrderLock 획득을 확인한다.
3. 테스트 worker PID만 강제 종료하고 stale claim·lock 및 부분 생성 파일 상태를 기록한다.
4. 재기동 전에 outbox·last-result·Git diff·임시 산출물을 대조하여 부작용과 완료 여부를 판정한다. 완료 증거가 없을 때만 격리 stale lock을 제거하고 동일 작업을 재기동한다.
5. 재기동 후 동일 작업이 한 번만 완료되고 claimed→processed 이동, outbox terminal 상태, lock 해제까지 정상 종결되는지 확인한다.
6. 복구 전후 HEAD 불변 여부, 추적 파일의 의도치 않은 변경 여부, untracked/partial 파일 잔존 여부를 확인하고 `git fsck --no-progress`, `git diff --check` 및 관련 unittest를 실행한다.
7. 테스트 프로세스와 임시 자원을 정리하고 운영 consumer가 계속 정상인지 확인한다.
8. `reports/120_report.md`를 작성한다. 첫 줄은 `Run-ID: RUN-120-01`로 하고, kill/restart PID, 실제 명령, 시간순 로그, 복구 판단 근거, Git 전후 상태, 테스트 결과, PASS/FAIL 판정과 남은 위험을 포함한다.
9. 결과 파일을 커밋하고 commit hash를 회신한다.
금지: PC 재부팅, 운영 consumer/Slack listener/무관한 프로세스 종료, 운영 lock 임의 제거, 완료 여부 확인 없는 자동 재실행, 저장소 밖 영구 변경, credential 출력, 기존 사용자 변경 덮어쓰기, 근거 없는 PASS 판정.
DoD: 격리 worker 강제 종료와 복구·재기동이 실제 수행되고 PID·명령·시간순 증거가 남아야 한다. 재기동 후 중복 실행 없이 terminal 상태로 종결되어야 하며, stale 자원과 임시 파일이 정리되어야 한다. 복구 전후 Git HEAD와 작업트리 상태, `git fsck --no-progress`, `git diff --check`, 관련 테스트 결과로 저장소 무결성이 입증되어야 한다. 운영 consumer 정상 상태가 확인되고 `reports/120_report.md` 및 Git commit이 생성되어야 한다.
