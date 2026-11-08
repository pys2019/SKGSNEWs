"""비공개 주석이 붙은 뉴스레터를 pys2019@gmail.com 한 곳으로만 보낸다. (로컬 실행 전용)

사용: python scripts/send_private.py <호수> [--dry-run]
자격 증명: 환경변수 MAIL_USERNAME / MAIL_PASSWORD, 또는 private/.mail.env (KEY=VALUE 두 줄).
private/ 는 .gitignore 대상이라 저장소에 올라가지 않는다. 자격 증명은 사용자가 직접 파일에 적는다.
수신자는 아래 상수로 고정하며 인자로 바꿀 수 없다.
"""
import argparse
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TO = "pys2019@gmail.com"


def load_creds() -> tuple[str, str]:
    user, pw = os.environ.get("MAIL_USERNAME"), os.environ.get("MAIL_PASSWORD")
    f = ROOT / "private" / ".mail.env"
    if (not user or not pw) and f.exists():
        kv = {}
        for line in f.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                kv[k.strip()] = v.strip()
        user, pw = user or kv.get("MAIL_USERNAME"), pw or kv.get("MAIL_PASSWORD")
    return user or "", (pw or "").replace(" ", "")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("issue")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    news = read(ROOT / "issues" / a.issue / "newsletter.md")
    note = read(ROOT / "private" / f"주석_{a.issue}.md")
    usage = read(ROOT / "issues" / a.issue / "usage.md")
    if not news:
        print("뉴스레터 본문이 없습니다.", file=sys.stderr)
        return 1
    if not note:
        print("비공개 주석 파일이 없습니다. 보내지 않습니다.", file=sys.stderr)
        return 1

    body = (
        f"[비공개] 회의록 주석 포함본입니다. 이 메일은 {TO} 한 곳으로만 갑니다. 전달하지 마세요.\n"
        f"공개 링크: https://pys2019.github.io/SKGSNEWs/issues/{a.issue}.html\n\n"
        f"===== 뉴스레터 본문 =====\n{news}\n\n===== 비공개 주석 ([내부N] 대응) =====\n{note}\n"
    )
    if usage:
        body += f"\n===== 토큰 사용량 =====\n{usage}\n"

    msg = EmailMessage()
    msg["Subject"] = f"[비공개·주석 포함] 주간 SK·GS AIDC 이슈 {a.issue}"
    msg["To"] = TO
    user, pw = load_creds()
    msg["From"] = user or TO
    msg.set_content(body)

    if a.dry_run:
        print(f"[드라이런] 수신: {TO} / 제목: {msg['Subject']} / 본문 {len(body)}자 / 자격 증명 {'있음' if user and pw else '없음'}")
        return 0
    if not (user and pw):
        print("자격 증명이 없습니다. private/.mail.env 를 만들어 주세요.", file=sys.stderr)
        return 1
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(user, pw)
        s.send_message(msg)
    print("발송 완료:", TO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
