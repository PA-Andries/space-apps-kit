---
name: submission-checker
description: Check a Space Apps project submission draft against the rules before the Sunday 23:59 deadline: required fields, public links, demo length or slide count, English, AI disclosure, credits and branding. Use on Sunday before clicking Submit.
---

# Submission checker

A submission that breaks a rule is out of global judging, whatever its quality. Run this on Sunday evening, not at 23:55.

## Input

The project page draft in `work/project-page.md` (from `templates/project-page.md`) and, if available locally, the demo video or slides file.

## Procedure

1. Run the automated checks:
   ```bash
   python3 scripts/check_submission.py work/project-page.md --demo path/to/video.mp4   # or slides.pdf / slides.pptx
   ```
   It checks required sections, English-only hints, that every URL answers publicly (no login redirect), video duration ≤ 30 s (needs `ffprobe`) and slide count ≤ 7 (PDF or PPTX).
2. Then review by hand what a script can't judge:
   - [ ] Answers an official 2026 challenge (not "create your own").
   - [ ] NASA data section names each dataset with a link and explains how it's used.
   - [ ] Every external resource (code, libraries, images, data, text) is credited.
   - [ ] AI section says which tools and how; AI images/video carry a visible watermark.
   - [ ] No NASA logo, flag, mission patch, or anything implying NASA endorsement.
   - [ ] No minors' names, faces or voices; no personal data; no commercial promotion.
   - [ ] Final project link opens without login (test in a private window) and shows the working product.
   - [ ] Repo has an OSI open-source license file.
   - [ ] All teammates appear on the team's Members tab and are registered at the Paris event.
   - [ ] High-level summary reads well to someone with no background in 20 seconds.
   - [ ] The text addresses each of the five criteria (influence, creativity, validity, relevance, presentation).
3. Report blocking issues first, then improvements, in a short list.

Remember: once submitted, it's final. Saved drafts are visible publicly on the site even before submission.
