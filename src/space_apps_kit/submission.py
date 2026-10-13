"""Check a Space Apps project page draft and demo file against the submission rules.

Usage:
    uv run check-submission work/project-page.md [--demo FILE] [--no-network]
    uv run check-submission --demo FILE

Checks:
  - required sections are present and filled (no leftover <placeholders>)
  - every URL answers publicly (HTTP < 400, no redirect to a login page)
  - demo video is <= 30 s (needs ffprobe) or slides <= 7 (PDF or PPTX)
  - mentions of NASA logos/insignia and missing AI disclosure are flagged

Exit code 1 if any blocking issue is found.
"""

import argparse
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from pypdf import PdfReader

REQUIRED_SECTIONS = [
    "Project Name",
    "High-Level Project Summary",
    "Link to Project Demo",
    "Link to Final Project",
    "Detailed Project Description",
    "NASA Data",
    "Space Agency Partner & Other Data",
    "Use of Artificial Intelligence",
]
MAX_VIDEO_SECONDS = 30.0
MAX_SLIDES = 7
LOGIN_HINTS = ("accounts.google.com", "/login", "signin", "sign_in", "auth", "sso")
URL_RE = re.compile(r"https?://[^\s)>\]\"']+")
PLACEHOLDER_RE = re.compile(r"<[^>\n]{2,}>")


class Report:
    def __init__(self):
        self.blocking = []
        self.warnings = []
        self.ok = []

    def block(self, msg):
        self.blocking.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def good(self, msg):
        self.ok.append(msg)

    def print(self):
        for title, items, mark in (
            ("BLOCKING", self.blocking, "x"),
            ("WARNINGS", self.warnings, "!"),
            ("OK", self.ok, "v"),
        ):
            if items:
                print(f"\n{title}")
                for item in items:
                    print(f"  [{mark}] {item}")
        print()


def split_sections(text):
    sections = {}
    current = None
    for line in text.splitlines():
        heading = re.match(r"^#{1,3}\s+(.*?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {name: "\n".join(body).strip() for name, body in sections.items()}


def check_sections(text, report):
    sections = split_sections(text)
    lowered = {name.lower(): body for name, body in sections.items()}
    for name in REQUIRED_SECTIONS:
        body = lowered.get(name.lower())
        if body is None:
            report.block(f"Missing section: {name}")
        elif not body or PLACEHOLDER_RE.fullmatch(body.strip()):
            report.block(f"Empty section: {name}")
        else:
            report.good(f"Section filled: {name}")

    leftovers = PLACEHOLDER_RE.findall(text)
    if leftovers:
        report.warn(f"Leftover placeholders: {', '.join(sorted(set(leftovers))[:5])}")

    for name in ("Link to Project Demo", "Link to Final Project"):
        body = lowered.get(name.lower(), "")
        if body and not URL_RE.search(body):
            report.block(f"No URL in section: {name}")

    ai = lowered.get("use of artificial intelligence", "")
    if ai and len(ai.split()) < 8:
        report.warn("AI section is very short: name the tools and what they were used for")

    if re.search(r"\b(nasa (logo|meatball|worm|insignia|patch))\b", text, re.I):
        report.warn("Mentions a NASA logo/insignia: NASA branding is not allowed in submissions")

    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    if re.search(r"\b(le|la|les|des|nous|avec|pour|données)\b", text, re.I) and non_ascii > 20:
        report.warn("Text may contain French: all project page content must be in English")


def check_url(url, timeout):
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 space-apps-kit"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final = response.geturl()
            if any(hint in final.lower() for hint in LOGIN_HINTS) and not any(
                hint in url.lower() for hint in LOGIN_HINTS
            ):
                return False, f"redirects to a login page ({final})"
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as err:
        return False, f"HTTP {err.code}"
    except Exception as err:  # network errors, timeouts, bad TLS
        return False, f"unreachable ({err.__class__.__name__}: {err})"


def check_links(text, report, timeout):
    urls = sorted(set(u.rstrip(".,;") for u in URL_RE.findall(text)))
    if not urls:
        report.block("No links found in the project page")
        return
    for url in urls:
        ok, detail = check_url(url, timeout)
        if ok:
            report.good(f"Public: {url} ({detail})")
        else:
            report.block(f"Not publicly reachable: {url} ({detail})")


def video_duration(path):
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def pdf_pages(path):
    return len(PdfReader(str(path)).pages)


def pptx_slides(path):
    with zipfile.ZipFile(path) as archive:
        return sum(1 for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))


def check_demo(path, report):
    path = Path(path)
    if not path.exists():
        report.block(f"Demo file not found: {path}")
        return
    suffix = path.suffix.lower()
    if suffix in (".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"):
        duration = video_duration(path)
        if duration is None:
            report.warn("Could not read video duration (install ffmpeg/ffprobe) - check it is <= 30 s by hand")
        elif duration > MAX_VIDEO_SECONDS:
            report.block(f"Video is {duration:.1f} s, limit is {MAX_VIDEO_SECONDS:.0f} s")
        else:
            report.good(f"Video length {duration:.1f} s (<= {MAX_VIDEO_SECONDS:.0f} s)")
    elif suffix in (".pdf", ".pptx"):
        count = pdf_pages(path) if suffix == ".pdf" else pptx_slides(path)
        if count > MAX_SLIDES:
            report.block(f"Deck has {count} slides, limit is {MAX_SLIDES} including the title")
        else:
            report.good(f"Deck has {count} slides (<= {MAX_SLIDES})")
    else:
        report.warn(f"Unknown demo format {suffix}: check the 30 s / 7 slides limit by hand")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check-submission", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "page", nargs="?", help="project page draft (Markdown, headings as in project-page-template.md)"
    )
    parser.add_argument("--demo", help="local demo file: video (mp4/mov/webm) or slides (pdf/pptx)")
    parser.add_argument("--no-network", action="store_true", help="skip the public link checks")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args(argv)
    if not args.page and not args.demo:
        parser.error("give a project page, a --demo file, or both")

    report = Report()
    if args.page:
        text = Path(args.page).read_text(encoding="utf-8")
        check_sections(text, report)
        if not args.no_network:
            check_links(text, report, args.timeout)
    if args.demo:
        check_demo(args.demo, report)

    report.print()
    print(
        "Manual checks left: official challenge, datasets credited, AI media watermarked, "
        "no minors, OSI licence in repo, all members on the Members tab."
    )
    return 1 if report.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
