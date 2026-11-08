"""issues/*/newsletter.md 를 docs/ 아래 HTML 사이트로 변환한다. (GitHub Actions에서 실행)"""
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
HTML = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:16px/1.7 "Malgun Gothic",sans-serif;max-width:820px;margin:2rem auto;padding:0 16px;color:#222}}
h1{{font-size:1.5rem}}h2{{font-size:1.15rem;border-bottom:1px solid #ccc;padding-bottom:.2rem;margin-top:2rem}}
blockquote{{color:#a00;margin:0}}a{{color:#0b5cad}}</style></head><body>{body}</body></html>"""


def main() -> None:
    out = ROOT / "docs" / "issues"
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for md in sorted((ROOT / "issues").glob("*/newsletter.md")):
        issue = md.parent.name
        body = markdown.markdown(md.read_text(encoding="utf-8"), extensions=["tables"])
        (out / f"{issue}.html").write_text(
            HTML.format(title=f"주간 강건재 이슈 {issue}", body=body), encoding="utf-8")
        names.append(issue)
    items = "\n".join(f'<li><a href="issues/{n}.html">{n}</a></li>' for n in sorted(names, reverse=True))
    (ROOT / "docs" / "index.html").write_text(
        HTML.format(title="주간 강건재 이슈", body=f"<h1>주간 강건재 이슈 (내부용)</h1><ul>{items}</ul>"),
        encoding="utf-8")
    print("호수:", len(names))


if __name__ == "__main__":
    main()
