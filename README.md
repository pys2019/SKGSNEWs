# 주간 SK·GS AIDC 이슈 뉴스레터

SK그룹과 GS그룹의 AI 데이터센터(AIDC) 사업·투자 동향을 매주 정리한다. 각 건에 포스코 시사점 한 줄을 덧붙인다.

## 흐름
1. 매주 월요일 07:00(로컬) Claude Code 예약 작업 `weekly-ganggeonjae-newsletter`가 웹검색으로 SK·GS AIDC 한 호를 만든다. PC와 Claude 앱이 켜져 있어야 하며, 꺼져 있으면 다음 실행 때 돌아간다.
2. 결과를 `issues/YYYY-Www/newsletter.md`에 저장하고 `state/seen.json`을 갱신해 `git push`한다.
3. push를 받으면 GitHub Actions(`publish-newsletter`)가 `docs/`를 만들어 Pages에 게시하고 링크를 메일로 보낸다. 수신: yespark@posco.com, pys2019@gmail.com

## 구조
- `config/sections.json`: 섹션 6개(SK 사업, GS 사업, 투자·M&A, 테넌트·파트너, 입지·전력·용수, 경쟁·시장)와 검색 힌트
- `scripts/build_site.py`: md → HTML 변환
- `.github/workflows/weekly.yml`: 게시 + 메일
- `issues/`: 호별 원본 / `state/seen.json`: 중복 방지

## 설정 (한 번)
- Settings → Pages → Source: GitHub Actions
- Secrets: `MAIL_USERNAME`(Gmail 주소), `MAIL_PASSWORD`(Gmail 앱 비밀번호)
- 테스트: Actions → publish-newsletter → Run workflow (기본값은 pys2019@gmail.com에만 발송)

## 주의
- 저장소가 public이면 `issues/` 원문과 Pages가 누구에게나 보인다. 내부용이면 private로 바꾼다. 이 경우 일반 플랜에서는 Pages가 막힐 수 있다.
- push 즉시 메일이 나가므로, 검토가 필요하면 예약 작업이 push 전에 멈추도록 지침을 바꾼다.
