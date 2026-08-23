발행일: 2026-08-23
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 001
제목: git-clean-baseline-verification
목적: orders/reports 초기화 직후 공용 저장소가 안전한 clean baseline인지 독립적으로 확인하고 증거를 남긴다.
대상: C:\lab\vsurf_capital\common
작업:
1. 착수 시 git status --porcelain=v1을 실행해 작업 트리 clean 여부를 확인한다.
2. git fetch origin master 후 HEAD, origin/master, merge-base 관계를 확인해 로컬과 원격이 동기화되어 있는지 검증한다.
3. orders와 reports에 .gitkeep 외 기존 산출물이 없는지 확인한다.
4. 현재 branch, HEAD short hash, origin/master short hash, dirty entry 수, orders 파일 수, reports 파일 수를 기록한다.
5. 결과를 reports/001_report.md에 작성한다. 민감정보와 환경변수 값은 기록하지 않는다.
6. 보고서만 commit/push하고 최종 git status가 clean인지 재검증한다.
7. #vsurf-code-reports에 PASS/FAIL, commit hash, 핵심 증거를 게시한다.
금지: 기존 코드 수정, board 수정, git reset/rebase/force push, credential 출력, unrelated file 생성.
DoD: (a) 착수 전 clean 여부가 명시됨, (b) HEAD/origin 동기화 검증됨, (c) 초기화된 orders/reports 상태 검증됨, (d) reports/001_report.md 생성, (e) commit/push 완료, (f) 최종 worktree clean, (g) Slack 결과 보고.
