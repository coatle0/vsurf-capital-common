# ORDER 001 — common\ git 저장소 초기화

발행: 2026-08-07 | 발신: CAO (CIO 승인) | 수신: Bill (PC1)
상태: 미착수

## 목적

두 PC의 `C:\lab\vsurf_capital\common\` 을 동일 내용으로 유지.
Order·board·정본이 PC 경계를 넘어 도착하게 함. (현 불연속의 원인 제거)

## 범위

저장소 루트 = `C:\lab\vsurf_capital\common\` **만**.
상위 `vsurf_capital\` 루트는 제외 (epub·png·docx·xlsx·lock 혼재).

## 작업

1. `common\` 에서 git init
2. `.gitignore` 등재: `.venv/`, `__pycache__/`, `*.session`, `.env`, `*.bak_*`, `_*.txt`, `.~lock*`
3. GitHub **비공개** 저장소 생성 후 push
4. PC2 동일 경로에 clone
5. 양 PC 왕복 실증 1회 (PC1 커밋 → PC2 pull 확인 → PC2 커밋 → PC1 pull 확인)
6. `common\AGENT_RULES.md` 신설 — orders·board 규약 수록.
   `C:\lab\CLAUDE.md` 에 참조 지시 1줄 추가 (자격증명·PC별 설정은 저장소 밖 유지)

## 금지

- 자격증명·세션 문자열·토큰 값 출력 금지 (존재 여부만 보고)
- 공개 저장소 생성 금지
- 기존 파일 삭제·이동 금지 (정리는 별건)

## DoD

양 PC에서 `board.md` 수정 → push → 상대 PC pull 반영 확인 1회 왕복 성공.

## 보고

완료 시 `board.md` 파이프 행 갱신 + TG 1줄 발행.
보고 항목: 양 PC 경로, 원격 저장소명(비공개 여부), 커밋 해시, 왕복 성공 여부.
