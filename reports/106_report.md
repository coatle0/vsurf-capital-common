# ORDER 106 — full_pipeline_confirm 실행 결과

## Report §0

- 상태: DONE
- 좌표: board.md 전문 (읽기 전용, 수정 없음)
- PC1 경로: C:\lab\vsurf_capital\common\board.md
- 커밋: (dispatcher 커밋 예정 — 본 세션은 commit/push 하지 않음)
- 요약: board.md 읽기 성공. 아래 board.md 원문 그대로 옮김. board.md 및 다른 파일 수정·삭제 없음.

## board.md 원문 (읽은 그대로)

```
# VSURF Board

> 정본: `C:\lab\vsurf_capital\common\board.md`
> 상태판. 로그 아님. 3줄 상한.
> 갱신: 2026-08-08

## 현재

| 프로젝트 | 지금 단계 | 산출물 | 쥔 자 | 다음 행동 | 갱신 |
|---|---|---|---|---|---|
| STI-G1 | 매핑표 33행 검토 대기 (13일) | BU-030 매핑표 | jw | 쟁점 4건 판정 → 승인 행만 적재 | 08-08 |
| SA-0 | Anchor 청산룰 미정의 | — | jw | 최소 청산룰 1판 확정 → G-A 해제 | 08-08 |
| 파이프 | ORDER 001·002 종결. 왕복·모바일 원격 실증 완료 | repo coatle0/vsurf-capital-common / remote-control 상시 ON | (비어있음) | PC2 단독파일 14개 저장소 편입 (003) | 08-08 |

## 규약

1. `쥔 자` = 점유 표시. 비었으면 집을 수 있고, 이름이 있으면 손대지 않음.
2. 착수: pull → `쥔 자`에 자기 이름 → push.
3. 종료: `지금 단계`·`산출물`·`다음 행동`·`갱신` 교체 → `쥔 자` 비움 → push → 그 행 1줄 TG 발행.
4. 줄은 지우지 않고 다음 단계로 민다.
5. **3줄 상한.** 4번째는 기존 1건 종결 후에만 진입.
6. 매일 1회 3줄 전문 TG 발행 (무변동이어도 발행 = 생존 신호).

## 대기열

발주 완료·미착수분은 `orders/` 참조. board 진입은 3줄 상한 준수.
```
