발행일: 2026-08-14
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 119
제목: forced-kill-lock-recovery-validation
목적: 긴 실행 도중 worker 강제 종료 시 중복실행 방지용 claim·lease·lock의 잔존 여부와 안전한 재실행 가능성을 실측하여 Phase 2 §6-4를 마무리한다.
대상: order_inbox_consumer 및 Order claim·lease·lock 처리 경로
작업:
1. 현재 claim·lease·lock 구현과 관련 테스트를 확인하고, 테스트 전 Git 상태 및 활성 consumer/worker 상태를 기록한다.
2. 운영 consumer나 무관한 프로세스를 건드리지 않는 격리 환경에서, 충분히 오래 실행되는 테스트 worker를 시작하여 claim 또는 lock 획득을 확인한다.
3. PID와 테스트 좌표를 기록한 뒤 해당 테스트 worker만 강제 종료한다.
4. 종료 직후 stale claim·lease·lock 잔존 여부, 동시 중복실행 발생 여부, 동일 작업의 재claim·재실행 가능 여부를 확인한다.
5. 테스트 과정에서 만든 프로세스·임시 자원을 정리하고 기존 운영 consumer가 정상인지 확인한다.
6. reports/119_report.md를 작성하고 필요한 경우 재현 테스트만 최소 변경한다. 보고서 첫 줄은 `Run-ID: RUN-119-01`, 본문에는 kill 대상 PID, 사용한 명령, 시간순 로그, lock/claim 전후 상태, 재실행 결과, PASS/FAIL 판정, 남은 위험을 포함한다.
7. 결과 파일을 커밋하고 commit hash를 회신한다.
금지: 운영 consumer/Slack listener/무관한 프로세스 종료, 저장소 밖 영구 변경, credential 출력, 기존 사용자 변경 덮어쓰기, 근거 없는 PASS 판정.
DoD: 격리된 긴 실행 worker의 강제 종료가 실제 수행되고 PID·명령·시간순 증거가 reports/119_report.md에 남아야 한다. 종료 후 중복실행 여부와 stale claim·lease·lock 상태 및 동일 작업 재실행 가능성이 모두 실측되어야 한다. 테스트 자원이 정리되고 운영 consumer 정상 상태가 확인되어야 한다. 보고서 첫 줄에 Run-ID가 포함되고 결과가 Git commit으로 생성되어야 한다.
