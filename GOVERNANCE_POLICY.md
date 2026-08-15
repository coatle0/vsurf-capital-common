# VSURF Capital 3Phase Order 운영 정책

- 상태: ACTIVE
- 버전: v1.2
- 승인: CIO
- Owner: COO
- 시행일: 2026-08-15
- Slack 근거: `#vsurf-governance`, message `1786767283.225149`

## 1. 기본 원칙

Git은 Order·코드·결과·Skill·Policy의 정본이며 Slack은 지시·전달·관제·승인·공유 기록이다.

정식 실행 Order의 번호는 프로젝트별 번호가 아니라 전역 unique identifier다. 발행자의 기억이나 단순 `last + 1` 방식으로 번호를 정하지 않는다.

## 2. 채널별 실행 경계

### `#vsurf-agent-control`

- 정식 Order 실행 파이프 전용이다.
- `[EXECUTE ORDER 100]` intake와 `ORDER BODY` 형식을 사용한다.
- 정식 Order만 `orders/NNN_*.md`와 `reports/NNN_report.md`를 사용한다.

### `#vsurf-code-reports` (`rpt`)

- 기술 요청·원인 분석·코드 수정 협업·결과 보고용이다.
- 실행 신호 채널이 아니며 `[EXECUTE ORDER]`를 사용하지 않는다.
- rpt에서 발주한 작업은 `orders/NNN_*.md` 전역 번호공간을 사용하지 않는다.
- rpt 결과는 채널 내 텍스트 또는 `codex_reports/`와 같은 별도 로그 경로에 저장한다.
- `reports/NNN_report.md` 형식을 재사용하지 않는다.

이 분리는 ORDER 125 중복 발행 사고의 rpt 기여분을 제거한다. 이미 실행·claim된 기존 Order는 사후 renumber하지 않는다.

## 3. Order 번호 발행 Preflight

정식 Order를 발행하기 전에 다음 네 조건을 모두 확인한다.

1. `Git latest-order check = PASS`
2. `Git duplicate check = PASS`
3. `Slack active-order check = PASS`
4. `NNN globally unused = PASS`

구체적으로 다음 위치를 교차검증한다.

- Git의 `orders/`, `reports/`, `Register ORDER NNN`, `Complete ORDER NNN` 커밋
- dispatcher의 inbox, claimed, active 및 결과 상태
- Slack에 있으나 아직 Git에 반영되지 않은 병렬·진행 중 Order

어느 한 곳에서라도 같은 번호가 발견되면 해당 번호를 사용하지 않는다.

## 4. Duplicate Guard

Executor/Dispatcher는 claim 전에 Order 번호 중복을 검사한다. 중복이면 실행을 중단하고 다음 상태로 보고한다.

```text
REJECT_DUPLICATE_ORDER_ID
```

이미 claim 또는 실행된 Order 번호는 변경하지 않는다. 충돌한 미실행 Order만 새로운 전역 미사용 번호로 재발행한다.

## 5. 버전 관계

- v1.2: rpt 트랙을 정식 Order 번호공간에서 분리하여 위험 표면을 축소한다.
- v1.1: `#vsurf-agent-control` 안에서 여러 GM·트랙이 동시에 번호를 발행할 때의 중복 위험을 Preflight 4게이트로 방어한다.
- v1.2는 v1.1을 대체하지 않는다. 두 규칙을 함께 적용한다.

## 6. 적용 사례

2026-08-15 12:32~12:48 COO가 `#vsurf-code-reports`에서 codex MCP 변경 작업에 ORDER 125를 사용했고, 이후 ATI/IVK 트랙도 같은 번호를 사용하려 했다. Git 선점 확인으로 후속 실행은 차단되어 실물 피해는 없었다.

본 정책부터 rpt 작업에는 Order 번호를 부여하지 않으며, 정식 Order 번호는 `#vsurf-agent-control`에서만 전역 Preflight를 거쳐 사용한다.
