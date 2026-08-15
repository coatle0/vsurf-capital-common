발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 128
제목: ati-phase2-hypothesis-validation
목적: ORDER 126 Phase 1 Discovery에서 생성한 ATI 가설들을 기존 GS MCP/BGD/SGS/index의 역사 데이터로 정량 검증하여 Market Regime, Turning, Leadership Rotation, Sector Risk의 후보 규칙과 실패 조건을 확정한다.

전제:
• ORDER 126 완료 commit `d5d817d9ac42e6e948ac14dfebea6c672034b8e7` 및 `reports/126_report.md`, `reports/126_data_summary.md`를 입력 정본으로 사용한다.
• 기존 ATI 번호 127 발행은 IVK ORDER 127과 번호 충돌이므로 무효로 간주한다. ATI Phase 2의 유효 Order는 128이다.
• ORDER 126의 FACT/OBSERVATION/HYPOTHESIS 구분을 유지한다.
• `bgd_year`는 220-row rolling window이며 full history가 아님을 명시한다.
• `kidx-mmt` stale/duplicate column, `etf_idx` NA weight 문제는 검증 근거에서 제한적으로 취급한다.
작업:
1. ORDER 126의 Phase 2 Hypothesis Register를 추출하고 각 가설을 독립 검증 단위로 정의한다.
2. GS MCP를 read-only로 호출하여 가능한 역사 구간에서 다음을 검증한다.
    ◦ REGIME: breadth level + breadth change + KOSPI EMA 조합과 이후 시장/섹터 성과 관계
    ◦ MARKET TURNING: breadth 저점 → ema5 확산 → ema20 확인 순서의 재현성
    ◦ LEADERSHIP: Q/W rank 합치·불일치, EMA 동시 양수/개선이 리더 지속·재가속·신규부상 구분에 주는 정보
    ◦ ROTATION: 기존 Q leader W 약화 + 신규 sector W rank/breadth/EMA 개선 조합의 선행성
    ◦ SECTOR RISK: optic 사례와 유사한 ema5 음전/rank 후퇴 이후 ema20·leader 약화가 이어지는지와 false warning 빈도
1. 각 가설마다 표본수, event 정의, forward horizon(가능하면 D+5/D+10/D+20 또는 데이터 빈도에 맞는 동등 horizon), hit/win rate, median/mean forward return 또는 사용 가능한 대체 성과지표를 제시한다.
2. threshold는 사후 최적화 하나만 제시하지 말고 최소 2~3개 후보 구간을 비교하고 과최적화 위험을 명시한다.
3. Market Turning / Sector Turning / Leadership Rotation을 별도 event class로 유지하고 혼합하지 않는다.
4. 현재 데이터로 검증 불가능한 항목은 추정하지 말고 `UNVERIFIED`로 표시하며 필요한 추가 데이터 좌표를 적는다.
5. 결과를 `reports/128_report.md`에 작성하고, 재현 가능한 계산/스크립트가 필요하면 최소 파일로 저장한다.
6. Phase 3에서 skill/rule로 승격할 후보를 PASS / CONDITIONAL / REJECT / UNVERIFIED로 분류하고 이유를 명시한다.
금지:
• 새로운 index 구축 또는 기존 GS sheet 수정
• 원시 CSV 대량 저장
• credential/token 기록
• 단일 최근 사례만으로 threshold 확정
• 데이터가 없는 개별 종목 성과 추정
• 실거래/주문 실행
DoD:
• `reports/128_report.md` 첫 줄 `Run-ID: RUN-128-01`
• ORDER 126 주요 가설별 정량 검증표 존재
• 최소 Market Regime / Market Turning / Leadership Rotation / Sector Risk 네 범주 판정 존재
• 표본수와 forward horizon 명시
• false positive/failure case 포함
• Phase 3 승격 후보와 제외 후보 명시
• 데이터 한계 및 UNVERIFIED 항목 명시
• Git commit 후 Slack에 COMPLETED/FAILED + commit hash + report 경로 회신
