# Decisions

One line per decision, newest last: `day time - decision, why (who)`. Read it before every task. During the event only the integrator writes here; propose changes in chat or in a PR.

- Fri 13 Nov 20:08 - Challenge chosen: **Flame in Freefall** (`challenges/flame-in-freefall.md`) (team, recorded by PA)
- Sat 14 Nov 12:00 - The app is built in this repo, not a separate one: one place for code and rules (team)
- Sat 14 Nov 12:00 - Roles reorganised around five build lanes plus integration: A Intégration et pitch, B Données, C Recherche, D Comparateur, E Assistant, F Interface et 3D. One folder per role; table in `CONTRIBUTING.md` (team)
- Sat 14 Nov 12:00 - Four pages instead of six: Accueil, Recherche, Comparateur, Assistant. Ranking becomes the search order, the fiche becomes a search result's detail, the oxygen × pressure map moves to the Comparateur. To be confirmed by the team (proposal)
- Sat 14 Nov 12:00 - Third data table `data/publications.csv` from the NTRS API; column contract in `flame/commun/constantes.py` (proposal)
- Sat 14 Nov 12:00 - Short branches and pull requests replace "everyone on main"; a PR that only touches its author's files is merged by its author once `uv run verifier` passes (team)
- Sat 14 Nov 12:30 - GitHub Actions CI removed: it failed in seconds without logs on every run. `uv run verifier` and the push hook are the gate now (PA)
- Sat 14 Nov 12:30 - Repo rules are enforced, not just written: git hooks in `.githooks/` refuse commits on `main`, files outside the author's lane, secrets, big files, and pushes that fail the checks or come from an agent without a CLAIM. `AGENTS.md` holds the rules for every AI agent (PA)
- Sat 14 Nov 12:55 - Roles assigned: A Clément, B PA, C Martin, D Hugo, E Ethan, F Mathéo (table in `CONTRIBUTING.md`). `.github/CODEOWNERS` is active, so GitHub asks the owner of a folder for review when a PR touches it (PA)
- Sat 14 Nov 13:00 - A relayed agreement counts: when a member tells their AI agent that a file's owner agreed, the agent may write the `Accord: <owner>` line; the member answers for it (PA)
- Sat 14 Nov 13:16 - The site's interface is in English on all four pages (titles, buttons, texts), as the event rules require; use `flame.ui.label()` for habitats, pillars and profiles. Code comments and docstrings stay in French (PA)
- Sat 14 Nov 13:16 - `flame.recherche` also exports `detail_du_score`, `filtrer` and `valeurs_possibles`; `rechercher` keeps its name and parameters (PA)
- Sat 14 Nov 13:16 - `flame.ui` also exports the functions added by PR #11, under English names: `label`, `place_picker`, `pillar_picker`, `place_conditions`, `EARTH`, `investigation_card`, `flame_scene`, `show_sidebar`. The French names `afficher_cadre`, `carte_fiche` and `scene_3d` stay as aliases until their users switch (PA)
- Sat 14 Nov 13:16 - Search score settings accepted as the team's judgement, not NASA data: oxygen scores 0 from a 10-point gap with the habitat; fuel scores solid 20, liquid 12, gas 6; data scores 15 points at 50 tests, 10 at 10, 5 at 1 (PA)
