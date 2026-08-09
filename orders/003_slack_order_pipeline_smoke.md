# ORDER 003 — Slack Git Order 파이프 스모크 테스트

발행: 2026-08-09 | 발신: CIO | 수신: Codex PC2
상태: 검증 대기
도구: 없음

## 목적

Slack 실행 신호가 Git 정본 Order를 찾아 Codex를 실행하고 결과를 Git과 Slack에 남기는 최소 경로를 검증한다.

## 절대경로

- Order: `C:\lab\vsurf_capital\common\orders\003_slack_order_pipeline_smoke.md`
- 프로젝트: `C:\lab\vsurf_capital\common`
- 결과: `C:\lab\vsurf_capital\common\reports\003_pipeline_smoke.md`

## 작업

1. 본 Order와 `C:\lab\vsurf_capital\common\AGENT_RULES.md`를 읽는다.
2. `reports\003_pipeline_smoke.md`를 생성한다.
3. 파일에는 실행 PC ID, 검증 시각, Order 절대경로, Dispatcher 검증 결과를 기록한다.
4. `python -m unittest discover -s tests -p "test_*.py"`를 실행한다.

## 금지

- Slack·Telegram 토큰 또는 설정값 기록 금지.
- 다른 프로젝트 파일 변경 금지.
- 위험 권한 우회 옵션 사용 금지.

## DoD

- Dispatcher 단위 테스트 통과.
- 결과 문서 생성.
- Git commit 및 push.
- Slack에서 동일 Order 결과 확인.
