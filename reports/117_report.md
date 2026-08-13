Run-ID: RUN-117-01

# ORDER 117 — NBIS Q2 2026 Earnings Call 분석 (claude 실호출 재검증)

## Report §0

- 상태: PASS — `tikr_get_transcript(ticker="NBIS", eid=2012928878, transcript_id=3791591)` 실호출 성공, 승인 게이트 차단 없이 완주(113번에서 관측된 권한 게이트 미재현). transcript 38세그먼트/42,687자 정상 수신.
- 가이던스: FY2026 전 지표 재확인 — ARR $70억~$90억, 그룹 매출 $30억~$34억, 그룹 조정 EBITDA 마진 약 40%, CapEx $200억~$250억, 연말 연결전력 800MW~1GW(연말 계약전력 목표는 이번 분기 5GW로 상향).
- 매출/마진: Q2 그룹 매출 $5.82억(YoY +454%, QoQ +46%), ARR $30억(연말 대비 QoQ +58%); 그룹 조정 EBITDA $2.36억·마진 41%(Q1 32%에서 개선), Nebius AI 사업부 마진 50%.
- 성장 동력/코멘트: 분기 중 평균 $10억 이상 랜드마크 계약 4건 체결(연 $20M~$25M/MW, CapEx 선급 50~60%), $40M~$50M/MW 프리미엄 단기계약, 최초 용량 경매 낙찰가 전고점 대비 +15%, 신규 자산경량(asset-light) 파트너십 모델 도입.
- 주요 Q&A 리스크: (1) Vineland 부지 공청회 표결 보류 — 경영진은 일정 영향 없다고 주장하나 인허가 지연 리스크 잔존, (2) 연결전력(connected power) 시점과 매출 인식 사이 수개월 시차, (3) 2027년 대규모 증설 자금조달 방식(자산담보부채·회사채·지분희석 배분) 미확정, (4) 단기 프리미엄 가격 지속가능성 및 초기 단계인 자산경량 모델의 검증 부족.

## 1. 실행 로그

- `mcp__tikr__tikr_get_transcript` 스키마는 세션 시작 시 deferred tool 목록에 이름으로 노출되었고, `ToolSearch(query="select:mcp__tikr__tikr_get_transcript")`로 스키마를 로드한 뒤 즉시 실호출했다.
- 실호출 결과: `{"ok": true, "ticker": "NBIS", "segments": 38, "chars": 42687, "file": "C:\\autoai\\tikr-toolkit\\outputs\\NBIS_transcript_3791591.txt"}` — 승인 프롬프트나 권한 게이트 오류 없이 1회 호출로 완료.
- 저장된 transcript 파일을 전문 그대로 읽어 위 §0 요약을 직접 작성했다(인용·추론이 아닌 원문 기반).
- 113번에서 보고된 "하네스 권한 게이트로 실호출 미완주" 이슈는 본 실행에서 재현되지 않았다 — 115번(사전 승인 확인)에 이은 완전한 end-to-end 통과.

## 검증

- tikr 실호출: 성공 (§1, 원문 응답 로그).
- transcript 원문 대조: 성공 — CFO 가이던스 문단("we are reaffirming our full year 2026 guidance..."), 매출/마진 문단, Q&A 4개 리스크 항목(Vineland, 연결전력-매출 시차, 2027 자금조달, 단기가격/자산경량 모델) 모두 원문에서 직접 확인.
- 파일 변경 범위: `reports/117_report.md` 신규 생성 1건 외 다른 파일 수정·삭제 없음(order 금지 사항 준수).
- 미완 사항: 없음. Slack 3줄 회신 및 git commit/push는 dispatcher 담당 범위로 본 세션에서 수행하지 않음.
