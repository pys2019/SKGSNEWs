"""주간 강건재 뉴스레터 생성기.

실행: python scripts/generate.py   (환경변수 ANTHROPIC_API_KEY 필요)
산출: issues/YYYY-Www/newsletter.md, docs/issues/YYYY-Www.html, docs/index.html
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic
import markdown

ROOT = Path(__file__).resolve().parent.parent
KST = timezone(timedelta(hours=9))
MODEL = "claude-sonnet-5-5"

RULES = """\
작성 규칙:
- 지난 7일 안에 나온 사실만 쓴다. 출처 URL과 일자가 없는 문장은 쓰지 않는다.
- 모든 사실에 근거등급을 붙인다: A확정 / B계획 / C추진중 / D가정.
- 성능·절감 수치는 시험규격·기준시점·비교대상이 함께 있을 때만 쓴다. 없으면 수치를 빼고 '조건 미확인'이라고 적는다.
- 접근하지 못한 출처는 '막힘'으로 적고 추정으로 채우지 않는다.
- 섹션마다 최대 3건. 각 건에 '우리에게 의미' 한 줄을 단다.
- 지난주에 이미 다룬 건은 새 진전이 있을 때만 다시 쓴다.
- 문체: 두괄식, 짧은 문장, 번역투와 상투어 금지.
- 내부 공유용이다. 대외 배포 문구로 쓰지 않는다.
"""

TEMPLATE_MD = """\
# 주간 강건재 이슈 {issue} ({start} ~ {end})
> 내부 공유용

## 이번 주 결론 3줄
(행동 제안 포함)

## A. AIDC 발주·착공
## B. 강재 시황·가격
## C. 경쟁·대체
## D. 기준·규제
## E. 전력·용수 병목
## F. 포스코그룹 동향

## 다음 주 일정
## 막힌 지점·미검증
"""


def load_seen() -> list[str]:
    p = ROOT / "state" / "seen.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def build_prompt(cfg: dict, issue: str, start: str, end: str, seen: list[str]) -> str:
    secs = "\n".join(f"- {s['code']}. {s['title']} (검색 힌트: {s['query']})" for s in cfg["sections"])
    return (
        f"{cfg['context']}\n\n"
        f"기간: {start} ~ {end}. 웹 검색으로 아래 섹션별 이슈를 모아 주간 뉴스레터를 마크다운으로 써라.\n\n"
        f"섹션:\n{secs}\n\n{RULES}\n"
        f"지난주까지 다룬 URL(중복 방지):\n" + "\n".join(seen[-80:]) + "\n\n"
        f"아래 틀을 그대로 채워 마크다운만 출력하라.\n\n"
        + TEMPLATE_MD.format(issue=issue, start=start, end=end)
    )


def generate(prompt: str) -> str:
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 25}],
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:16px/1.7 "Malgun Gothic",sans-serif;max-width:820px;margin:2rem auto;padding:0 16px;color:#222}}
h1{{font-size:1.5rem}}h2{{font-size:1.15rem;border-bottom:1px solid #ccc;padding-bottom:.2rem;margin-top:2rem}}
blockquote{{color:#a00;margin:0}}a{{color:#0b5cad}}</style></head><body>{body}</body></html>"""


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY 가 없습니다.", file=sys.stderr)
        return 1
    today = datetime.now(KST).date()
    iso = today.isocalendar()
    issue = f"{iso.year}-W{iso.week:02d}"
    start, end = str(today - timedelta(days=7)), str(today - timedelta(days=1))

    cfg = json.loads((ROOT / "config" / "sections.json").read_text(encoding="utf-8"))
    seen = load_seen()
    md_text = generate(build_prompt(cfg, issue, start, end, seen))
    if not md_text.startswith("#"):
        print("모델 출력이 마크다운 틀이 아닙니다. 저장하지 않습니다.", file=sys.stderr)
        return 1

    issue_dir = ROOT / "issues" / issue
    issue_dir.mkdir(parents=True, exist_ok=True)
    (issue_dir / "newsletter.md").write_text(md_text, encoding="utf-8")

    html = HTML.format(title=f"주간 강건재 이슈 {issue}", body=markdown.markdown(md_text, extensions=["tables"]))
    out = ROOT / "docs" / "issues"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{issue}.html").write_text(html, encoding="utf-8")

    urls = re.findall(r"https?://[^\s)>\]]+", md_text)
    (ROOT / "state").mkdir(exist_ok=True)
    (ROOT / "state" / "seen.json").write_text(
        json.dumps(sorted(set(seen) | set(urls)), ensure_ascii=False, indent=1), encoding="utf-8")

    items = "\n".join(
        f'<li><a href="issues/{p.stem}.html">{p.stem}</a></li>'
        for p in sorted(out.glob("*.html"), reverse=True))
    (ROOT / "docs" / "index.html").write_text(
        HTML.format(title="주간 강건재 이슈", body=f"<h1>주간 강건재 이슈 (내부용)</h1><ul>{items}</ul>"),
        encoding="utf-8")
    print("생성 완료:", issue)
    return 0


if __name__ == "__main__":
    sys.exit(main())
