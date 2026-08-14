Run-ID: RUN-118-01

# ORDER 118 — duplicate_execution_check

## Report §0

- 상태: DONE
- 좌표: N/A (Phase2 §6-4 OrderLock 실측 — structure_map 칸 아님)
- PC1 경로: C:\lab\vsurf_capital\common\reports\118_report.md
- 커밋: (미커밋 — commit/push는 dispatcher 종료 절차 담당, 본 세션에서 수행하지 않음)
- 요약: structure_map.md 첫 2줄 확인 완료. 실행 중 `.runtime\order-118.lock`(pid=20004, started=2026-08-14T14:24:10+09:00)이 이미 걸려 있음을 관측했으며, 락 파일은 건드리지 않고 그대로 두었다(금지 사항 준수). 본 세션은 Order 118의 "첫 번째 발주"로서 정상 완료.

## 1. 실행 로그

- `structure_map.md` 1~2행 확인:
  1. `# VSURF Structure Map v1`
  2. `> 발효: 2026-05-08 | CIO 손그림 (2026-05-08 0816) 정본화`
- `.runtime\order-118.lock` 존재 관측 (내용: `pid=20004 started=2026-08-14T14:24:10+09:00`). `scripts\order_dispatcher.py:296-313`의 `OrderLock.__enter__`가 `os.open(path, O_CREAT|O_EXCL|O_WRONLY)`로 생성하는 락 파일과 경로·형식이 일치하며, 본 Order를 실행시킨 dispatcher 프로세스 자신이 보유 중인 락으로 판단된다(`__exit__`에서 dispatcher 종료 시 `unlink`됨).
- 코드 검토로 락 동작 확인: 동일 `order_id`로 두 번째 dispatch가 락 보유 중 진입하면 `os.open`이 `FileExistsError`를 던지고, `OrderLock.__enter__`가 이를 `DispatchError("Order is already claimed or needs manual lock recovery.")`로 변환해 즉시 차단하는 구조(`order_dispatcher.py:304-306`).

## 검증

- `structure_map.md` 읽기: 성공 (원문 인용 위 §1 참조).
- `reports/118_report.md` 생성: 성공 (본 파일).
- 파일 변경 범위: `reports/118_report.md` 신규 생성 1건 외 다른 파일 수정·삭제 없음 (Order 금지 사항 준수, `.runtime\order-118.lock`은 읽기만 하고 미변경).
- 미완/한계: "거의 동시 2건 발주" 시 실제 차단은 별도 두 번째 dispatch 요청이 락 보유 구간에 진입해야 관측되며, 본(첫 번째) 세션 범위에서는 락 존재 관측 + 코드 경로 검토로만 확인했고 두 번째 발주에 의한 실제 `DispatchError` 발생은 이 세션에서 직접 유발/관측하지 않았다. Slack 3줄 회신 및 git commit/push는 dispatcher 담당 범위로 본 세션에서 수행하지 않음.
