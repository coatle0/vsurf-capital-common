# PC1 Grok/Hermes 셋업 프롬프트

> 작성: Bill (Claude, PC2) · 2026-08-17
> PC2(GOSU)에서 실측 검증한 Grok CLI 도입 절차를 PC1에 동일하게 적용하기 위한 프롬프트.
> PC1 세션에 아래 "프롬프트" 섹션을 그대로 붙여넣을 것. 배경은 `hermes_grok_integration_plan.md` 참조.

---

## 프롬프트

```
PC1의 C:\lab에 Grok CLI와 Hermes 실행 경로를 PC2(GOSU)와 동일하게 셋업해줘.
PC2에서 이미 실측 검증한 내용을 그대로 옮기는 작업이다 — 아래 순서·주의사항을 반드시 지켜라.

배경: 토큰 사용 급증 대응으로 codex/claude 외에 Grok CLI, Hermes(codex 하니스+api.x.ai
재사용)를 VSURF Order 파이프라인 실행기로 추가한다. PC2에서 겪은 시행착오를 여기 그대로
반영했으니 반복하지 않아도 된다.

■ 1. Grok CLI 설치
    npm i -g @xai-official/grok
검증: grok --version (1.0.4 이상이면 정상), where grok

■ 2. Grok 로그인 (사람 필요, 1회성)
    grok login --device-auth
URL+코드가 출력된다. 코드는 유효시간이 짧다 — 발급 즉시 브라우저에서 승인해야 한다.
미리 발급해두고 나중에 승인하면 "Error: Device code expired"로 실패한다(PC2에서 실제
겪음). 성공하면 "Signed in as <email>"이 뜬다.

■ 3. MCP 자동 상속 확인
    grok inspect
"MCP Servers (N)" 섹션에 PC1의 기존 ~/.claude.json에 등록된 MCP들이 별도 설정 없이 그대로
나열되는지 확인. PC2와 MCP 목록 자체는 다를 수 있다(PC1/PC2가 각기 다른 MCP를 씀) — 개수·
이름이 PC1의 실제 Claude MCP 구성과 일치하는지만 보면 된다.

■ 4. ★★★ 핵심 주의사항 — 반드시 C:\lab을 --cwd로 사용 ★★★
PC2에서 겪은 버그: 헤드리스 실행(grok -p)을 C:\lab 밖의 낯선 경로(OS 임시 폴더 등)에서
"파일을 써라" 같은 프롬프트와 함께 돌리면 60초+ 무한 대기했다(stdout/stderr/--debug
로그 전부 무출력, 프로세스는 tasklist에 살아있음 — codex의 UAC 무응답 패턴과 동일하게
추정, 근본 원인 미확정). --cwd를 C:\lab(또는 그 하위)로 바꾸면 정상 동작한다(PC2 실측:
41초, 정상 완료). 따라서 이후 모든 grok 헤드리스 호출은 반드시 --cwd "C:\lab\..." 형태로
실행할 것. C:\lab 밖 경로에서 절대 테스트하지 마라.

■ 5. 헤드리스 파일쓰기 실측 (--cwd는 C:\lab 하위 스크래치 폴더)
    mkdir C:\lab\_grok_pc1_scratch_test  (없으면)
    grok -p "Write the exact text 'grok-pc1-ok' to a new file named write_test.txt in the current directory. Do nothing else." ^
      --cwd "C:\lab\_grok_pc1_scratch_test" ^
      --permission-mode dontAsk ^
      --allow "Write" --allow "Edit" --allow "Read" ^
      --deny "Bash(git push*)" --deny "Bash(git commit*)" --deny "Bash(git reset*)" --deny "Bash(git checkout*)" --deny "Bash(git clean*)" --deny "Bash(rm *)" ^
      --output-format json
"Project trusted: no" 상태라도 상관없다 — --allow/--deny 플래그는 trust 상태와 무관하게
항상 강제 적용된다(공식 문서 확인, PC2 실측으로도 확인). 별도 trust 승인 절차를 밟을
필요 없다. 결과 JSON의 text 필드와 실제 파일 내용이 일치하는지 확인 후, 스크래치 폴더는
삭제해서 정리할 것.

■ 6. Hermes — 이번엔 하지 마라 (막힘, 별도 확인 필요)
Hermes 실행 경로(codex model_providers.hermes → https://api.x.ai/v1)는 2번의 Grok CLI
로그인과 **다른 자격증명**이 필요하다. ~/.grok/auth.json을 구조만 확인해보면(값은 절대
출력하지 말 것 — 필드 이름만) auth.x.ai OIDC 세션(refresh_token 등)이지, console.x.ai에서
발급하는 범용 API key(xai-... 형식)가 아니다. codex는 후자만 쓸 수 있다. 따라서:
    - console.x.ai에 이미 발급된 API key가 있는지 사용자에게 먼저 확인
    - 없으면 발급 요청 — 이건 계정/과금 행위라 우리가 대신 못 한다
    - key 없이 codex config.toml에 model_providers.hermes 블록을 만들지 마라 — 검증
      불가능한 코드는 안 쓴다(실측 원칙)

■ 보고
그대로 회신:
- Grok 설치 버전 / 로그인 성공 여부(이메일)
- grok inspect의 MCP 목록 (개수·이름)
- 5번 헤드리스 파일쓰기 결과(JSON 텍스트 + 실제 파일 내용 일치 여부, 소요시간)
- console.x.ai API key 보유 여부(값은 절대 언급 말 것, 있다/없다만)
- 막힌 지점이 있으면 정확히 어느 단계인지
```
