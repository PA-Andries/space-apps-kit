import zipfile

from space_apps_kit import submission
from space_apps_kit.submission import Report, check_demo, check_sections, main

FILLED_PAGE = """
# Project Name
Fire Watch
# High-Level Project Summary
A map of wildfire risk built on NASA FIRMS data.
# Link to Project Demo
https://example.org/demo
# Link to Final Project
https://example.org/app
# Detailed Project Description
It shows risk per town.
# NASA Data
FIRMS active fire data.
# Space Agency Partner & Other Data
None.
# Use of Artificial Intelligence
We used Claude Code to write parts of the map component and reviewed every change.
"""


def test_filled_page_has_no_blocking_issue():
    report = Report()
    check_sections(FILLED_PAGE, report)
    assert report.blocking == []


def test_missing_and_placeholder_sections_block():
    page = FILLED_PAGE.replace("# NASA Data\nFIRMS active fire data.", "# NASA Data\n<datasets>")
    page = page.replace("# Project Name\nFire Watch\n", "")
    report = Report()
    check_sections(page, report)
    assert "Missing section: Project Name" in report.blocking
    assert "Empty section: NASA Data" in report.blocking


def test_demo_section_without_url_blocks():
    report = Report()
    check_sections(FILLED_PAGE.replace("https://example.org/demo", "coming soon"), report)
    assert "No URL in section: Link to Project Demo" in report.blocking


def make_pptx(path, slides):
    with zipfile.ZipFile(path, "w") as archive:
        for i in range(1, slides + 1):
            archive.writestr(f"ppt/slides/slide{i}.xml", "<p/>")


def test_deck_over_seven_slides_blocks(tmp_path):
    deck = tmp_path / "deck.pptx"
    make_pptx(deck, 8)
    report = Report()
    check_demo(deck, report)
    assert report.blocking == ["Deck has 8 slides, limit is 7 including the title"]


def test_long_video_blocks(tmp_path, monkeypatch):
    video = tmp_path / "demo.mp4"
    video.write_bytes(b"")
    monkeypatch.setattr(submission, "video_duration", lambda path: 31.5)
    report = Report()
    check_demo(video, report)
    assert report.blocking == ["Video is 31.5 s, limit is 30 s"]


def test_cli_exit_codes(tmp_path):
    page = tmp_path / "page.md"
    page.write_text(FILLED_PAGE, encoding="utf-8")
    assert main([str(page), "--no-network"]) == 0
    page.write_text("# Project Name\nOnly a name\n", encoding="utf-8")
    assert main([str(page), "--no-network"]) == 1
