# Pitch: premier jet (dimanche 15 nov.)

Propriétaire : rôle A. Rédigé avec le gabarit `/pitch-builder`. Les textes à soumettre sont en anglais ; les consignes pour l'équipe sont en français.

**À confirmer par un humain avant la remise** (marqué `[À CONFIRMER]` dans le texte) :

1. le nom de l'équipe ;
2. l'adresse publique du site (elle doit s'ouvrir sans compte, dans une fenêtre privée) ;
3. la durée du pitch oral fixée par les organisateurs de Paris ;
4. le modèle utilisé par l'assistant du site le jour de la remise (Gemini aujourd'hui, PA demande de passer à Claude) ;
5. comment le fond étoilé, la mascotte et les icônes ont été faits : s'ils viennent d'un outil d'IA, ils doivent porter la mention visible « AI-generated » dans la vidéo et sur les diapositives.

Les chiffres ci-dessous ont été recalculés sur `main` (`cc64803`) le 15 nov. Si les données changent, les recalculer.

| Chiffre | Valeur | D'où il vient |
|---|---|---|
| Investigations NASA | 24 | `data/investigations.csv` |
| Lignes de tests | 1 989 | `data/tests.csv` |
| Conditions de la base lunaire | au moins 30 % d'oxygène, au plus 10,2 psi (70,3 kPa) | énoncé du défi (à revérifier sur le texte officiel) |
| Tests NASA dans ces conditions | 67, de 3 investigations (66 avec la pression notée) | `tests_correspondants`, recalculé à part |
| Oxygène le plus haut pour un vrai échantillon solide | 22,2 % | `data/tests.csv` (BASS-II) |
| Tests en gravité lunaire ou martienne | aucun | PSI n'a que de la microgravité et du 1 g |
| Licence des données PSI | CC0-1.0 | `data/psi/investigations.csv` |

## 1. Vidéo de 30 secondes

Cible : 30,0 s au plus, 70 à 80 mots, voix en anglais.

| Time | Beat | Voice-over | On screen |
|---|---|---|---|
| 0:00-0:02 | Team | "We're [À CONFIRMER: team name], from Paris." | Name card over the starry home page (no faces needed) |
| 0:02-0:05 | Challenge | "Flame in Freefall: Moon habitats will hold thirty percent oxygen. How does fire behave there?" | Home page, a click on "Moon base": the oxygen slider jumps to 30 % |
| 0:05-0:10 | Title | "Our fire-safety dashboard shows what NASA tested, and what nobody has." | Title "Flame in Freefall · Fire-safety dashboard", then the chart of tests filling in |
| 0:10-0:20 | How it works | "Set your oxygen and pressure. Two thousand real tests from NASA's PSI database light up, investigations are ranked, every score is explained." | Real footage: sliders moving, points changing colour on the oxygen × pressure chart, the ranking, one "why" panel opened |
| 0:20-0:30 | Impact | "Mission designers see the gaps before launch: no real solid was tested above twenty-two percent oxygen. Next: partial gravity." | "What we don't know" card, then the CSV export button, then the address of the site |

Word count: 72 (with a two-word team name)

Notes de tournage :

- Filmer le vrai site, pas des diapositives. Une seule prise par plan, souris lente.
- Le plan 0:10-0:20 est le cœur : on doit voir le chiffre des tests changer quand le curseur bouge.
- « Two thousand » arrondit 1 989 : le chiffre exact reste lisible à l'écran.
- Ne pas montrer la page Equipment ni le menu « Ask the assistant » s'ils sont retirés avant le gel.

### Checklist

- [ ] 30,0 s au plus (`ffprobe`, ou `uv run check-submission --demo`)
- [ ] Voix en anglais, ou sous-titres anglais
- [ ] Aucun logo, drapeau ou écusson de mission NASA à l'écran
- [ ] Visuels faits par IA marqués « AI-generated » de façon visible [À CONFIRMER, point 5]
- [ ] Musique libre de droits ou aucune ; créditée sur la page projet
- [ ] Aucun visage, voix ou nom de mineur
- [ ] Vidéo publique (YouTube non répertorié ou public), testée dans une fenêtre privée

## 2. Sept diapositives (solution de repli)

Sept au plus, titre compris. Peu de mots, grandes captures du vrai site.

1. **Title**: "Flame in Freefall · Fire-safety dashboard". Tagline: "What NASA tested, and what nobody has." Team [À CONFIRMER], Paris, the six first names, challenge "Flame in Freefall".
2. **Problem and user**: a habitat designer choosing the cabin air of a Moon base. The statement gives at least 30 % oxygen at 10.2 psi or less. One number: 24 NASA investigations, 1,989 test rows, scattered across tables nobody reads together.
3. **Solution**: full-width screenshot of the home page with "Moon base" chosen: sliders on the left, tests against your conditions on the right.
4. **How it works**: environment (habitat, oxygen, pressure, gravity, fuel) → tests that match (NASA PSI tables) → ranked investigations with the reason for each score → compare and export as CSV. Data: NASA Physical Sciences Informatics (PSI), CC0-1.0.
5. **Validity**: every count is recomputed from NASA's tables; a missing value is shown as missing, never guessed. Limits stated on screen: 67 tests match the Moon base conditions, from 3 investigations; no real solid sample above 22.2 % oxygen; no test in lunar or Martian gravity; Mars has no atmosphere figure in the statement, so nothing is matched to it.
6. **Impact**: who benefits: mission and habitat designers, fire-safety engineers, students. What it changes: the gaps in the evidence are visible before a design choice is made. [À CONFIRMER: a local case, for example a lab or a school in Paris that could use it.]
7. **Next steps**: add the partial-gravity experiments when their data is published, link each test to its NTRS report, open the site and the code to other teams. Live demo: [À CONFIRMER: public address]. Code: https://github.com/PA-Andries/space-apps-kit

## 3. Pitch oral (jury de Paris)

Durée : [À CONFIRMER auprès des organisateurs ; environ 4 minutes les années passées].

1. **Hook** (20 s): "On the Moon, the air in the cabin will hold thirty percent oxygen or more. Has anyone burned a fabric in that air, in space? NASA's own data says no."
2. **User and problem** (30 s): a habitat designer, 24 investigations, 1,989 test rows, no single place to read them against one environment.
3. **Live demo** (2 min): choose Moon base → the conditions fill in from the statement → the chart shows the 67 tests that match → "What we don't know" → the three most relevant investigations and why → Compare → CSV export.
4. **Data and validity** (40 s): NASA PSI tables only, counts recomputed, unknown values shown as unknown, scores are the team's judgement and say so.
5. **Impact** (20 s): design decisions made knowing where the evidence stops.
6. **Ask** (10 s): what the team needs next (partial-gravity data, feedback from combustion scientists).

### Les cinq questions probables

| Question | Réponse courte | Preuve |
|---|---|---|
| Is the science valid? | We predict nothing. We count NASA's own tests and show where they stop. | Counts recomputed from `data/tests.csv`; the fact-check of 15 Nov on issue #2 |
| What are the limits of the data? | 827 of 1,989 test rows have no recorded oxygen and 951 no pressure; no partial-gravity test; Mars has no atmosphere figure. | `data/tests.csv`, the statement |
| What is new compared with a chatbot over reports? | The site starts from the user's environment and refuses to guess outside the tested conditions. | Home page and "What we don't know" |
| Who would use it? | Habitat and mission designers, fire-safety engineers, students. | [À CONFIRMER: a real contact if the team has one] |
| What is next? | Partial-gravity data, a link from each test to its report, more partner data. | Slide 7 |

## 4. Texte de la page projet

### High-level summary

Flame in Freefall is a fire-safety dashboard for crewed habitats. The user describes an environment (spacecraft, station, Moon base, pressurized rover, Mars base, or custom oxygen, pressure, gravity and fuel) and the site shows which NASA microgravity combustion tests were run in those conditions, ranks the investigations that matter most with the reason for each score, compares them side by side, and exports the matching tests as CSV. It also says what is not known: for the Moon base conditions of the challenge statement, 67 NASA test rows from 3 investigations match, no real solid sample was tested above 22.2 % oxygen, and no test was run in lunar or Martian gravity. Nothing is estimated: a missing value is shown as missing.

### How we used NASA data

All figures come from NASA's Physical Sciences Informatics (PSI) repository, Combustion Science investigations: 24 investigations and 1,989 test rows (oxygen, pressure, air flow, fuel, result), read from PSI's published tables, licence CC0-1.0. The planet maps of the 3D scene are NASA images.

### Use of Artificial Intelligence

- **Claude Code (Anthropic)**: each team member worked with an AI coding agent. The agents wrote most of the code, tests and documentation under each member's direction, coordinated through a shared GitHub issue, and checked each other's work. The pull requests say what the agent did. The choice of the challenge, the scope, the scoring weights and every decision recorded in `DECISIONS.md` are the team's.
- **Assistant inside the site** [À CONFIRMER: Gemini (Google), model `gemini-3.5-flash`, today]: answers questions from the NASA records shown on the site and can call two counting tools; its answers are generated text.
- **Images**: the planet maps are NASA images, not AI-generated. [À CONFIRMER: the starry background, the mascot and the habitat icons were drawn with code written with an AI agent; if they appear in the video or slides, they carry a visible "AI-generated" mention.]
- No NASA logo, flag or mission insignia is used.

### Credits

- Data: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov, CC0-1.0.
- Images: NASA Scientific Visualization Studio (Blue Marble, https://svs.gsfc.nasa.gov/2915; LROC colour map of the Moon, https://svs.gsfc.nasa.gov/4720); NASA 3D Resources (Mars map, https://github.com/nasa/NASA-3D-Resources). Details in `flame/ui/three/assets/README.md` and in the footer of the home page.
- Software: Python, Streamlit, pandas, Plotly, requests, pypdf, three.js, uv, ruff, pytest (see `pyproject.toml`).
- Code: MIT licence, https://github.com/PA-Andries/space-apps-kit

## 5. Ce qui manque encore pour remettre

- [ ] Nom de l'équipe et adresse publique du site
- [ ] Vidéo tournée, montée, mise en ligne, testée en fenêtre privée
- [ ] Champ « Use of Artificial Intelligence » relu par chaque membre (chacun confirme ses outils)
- [ ] Texte officiel de l'énoncé collé dans `challenges/flame-in-freefall.md`, puis relecture de la diapositive 2 et du résumé
- [ ] `/submission-checker` lancé sur le brouillon de la page projet avant de cliquer sur Submit
