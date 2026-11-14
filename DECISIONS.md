# Decisions

One line per decision, newest last: `day time - decision, why (who)`. Read it before every task. During the event only the integrator writes here; propose changes in chat or in a PR.

- Fri 13 Nov 20:08 - Challenge chosen: **Flame in Freefall** (`challenges/flame-in-freefall.md`) (team, recorded by PA)
- Sat 14 Nov 12:00 - The app is built in this repo, not a separate one: one place for code, rules and CI (team)
- Sat 14 Nov 12:00 - Roles reorganised around five build lanes plus integration: A Intégration et pitch, B Données, C Recherche, D Comparateur, E Assistant, F Interface et 3D. One folder per role; table in `CONTRIBUTING.md` (team)
- Sat 14 Nov 12:00 - Four pages instead of six: Accueil, Recherche, Comparateur, Assistant. Ranking becomes the search order, the fiche becomes a search result's detail, the oxygen × pressure map moves to the Comparateur. To be confirmed by the team (proposal)
- Sat 14 Nov 12:00 - Third data table `data/publications.csv` from the NTRS API; column contract in `flame/commun/constantes.py` (proposal)
- Sat 14 Nov 12:00 - Short branches and pull requests replace "everyone on main"; a PR that only touches its author's files is merged by its author once CI is green (team)
