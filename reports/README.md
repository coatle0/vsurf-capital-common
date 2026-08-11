# reports/

ORDER 실행 결과 보고 디렉터리.

## 파일명

`{order번호}_{executor}.md` (예: `100_bill.md`)
executor 단일이면 `{order번호}_report.md` 도 허용.

## 필수 — Report §0

```
- 상태: DONE / FAIL / 부분완료
- 좌표: structure_map 칸 (배관 검증은 N/A)
- PC1 경로: 산출물 절대경로
- 커밋: 해시
- 요약: 3줄 이내
```

## 원칙

- 본문 정본은 여기. Slack 은 신호 3줄만 싣는다.
- 부분완료는 미완 항목을 명시한다. 통째 중단 금지 (AGENT_RULES 준용).
- FAIL 도 유효한 종결이다. 침묵만이 실패다.
