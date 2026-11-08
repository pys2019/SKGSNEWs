# 주간 강건재 이슈 뉴스레터 (GitHub 자동 갱신)

매주 월요일 07:00(KST)에 GitHub Actions가 한 호를 만들어 저장소에 커밋하고 GitHub Pages로 게시한다.

## 구조
- `.github/workflows/weekly.yml`: 일요일 22:00 UTC 스케줄 + 수동 실행
- `scripts/generate.py`: 웹검색으로 수집 → 마크다운 작성 → HTML 변환 → 목차 갱신
- `config/sections.json`: 섹션 6개와 검색 힌트 (여기를 고치면 다음 호부터 반영)
- `issues/YYYY-Www/newsletter.md`: 원본 / `docs/`: Pages 게시본 / `state/seen.json`: 중복 방지

## 최초 설정 (사용자가 직접)
1. GitHub에 **private** 저장소를 만들고 이 폴더를 push한다.
2. Settings → Secrets and variables → Actions에 `ANTHROPIC_API_KEY`를 등록한다.
3. Settings → Pages → Source를 **GitHub Actions**로 바꾼다.
4. Actions 탭에서 `weekly-newsletter`를 수동 실행해 1호를 확인한다.

## 주의
- 내부 공유용이다. private 저장소의 Pages는 GitHub Team/Enterprise 플랜이 필요하다. 해당 플랜이 아니면 Pages 대신 `issues/*.md`를 저장소에서 읽거나, `deploy` 잡을 지우고 이메일 발송 단계를 붙인다.
- 자동 생성본은 사람이 검토한 뒤 공유한다. 수치 조건 누락 여부를 확인한다.
