# Comment on travaille

Ce fichier fixe qui possède quoi, comment on envoie son travail et comment on écrit le code. Le sujet, les données et le planning sont dans `BRIEF_EQUIPE_IA.md`.

## Démarrer

Il faut [uv](https://docs.astral.sh/uv/getting-started/installation/) et GitHub Desktop.

```bash
uv sync
```

```bash
uv run streamlit run app.py
```

```bash
uv run verifier
```

- **`uv sync`** installe le même environnement pour tout le monde. À relancer après chaque Pull.
- **`uv run streamlit run app.py`** ouvre le site sur votre ordinateur.
- **`uv run verifier`** met le code en forme, puis lance les vérifications. À lancer avant chaque envoi. Au premier lancement, il active aussi les garde-fous du dépôt (voir « Les vérifications »).

Tant que `data/investigations.csv` n'existe pas, le site tourne sur les données fictives de `data/exemples/` et l'affiche en haut de chaque page. Chacun peut donc avancer sans attendre les vraies données.

## Qui possède quoi

| Rôle | Qui | Mission | Ses dossiers et fichiers | Binôme |
| --- | --- | --- | --- | --- |
| A. Intégration et pitch | Clément (`cbatonnier-wq`) | Fusionne le travail, garde le site en ligne, valide les fiches, prépare la vidéo et la page projet | `app.py`, `flame/commun/`, `tests/test_app.py`, `tests/test_contrat.py`, `pyproject.toml`, `uv.lock`, `.github/`, `pitch/`, les fichiers `.md` de la racine | B |
| B. Données | PA (`PA-Andries`) | Interroge l'API NTRS, structure les données PSI, produit les trois CSV | `flame/pipeline/`, `data/`, `tests/test_pipeline.py` | A |
| C. Recherche | Martin (`martinleducq`) | Moteur de recherche et classement selon le scénario | `flame/recherche/`, `pages/recherche.py`, `tests/test_recherche.py` | E |
| D. Comparateur | Hugo (`hugovlst`) | Comparaison de deux ou trois investigations | `flame/comparateur/`, `pages/comparateur.py`, `pages/donnees.py`, `tests/test_comparateur.py` | F |
| E. Assistant | Ethan (`Ethan-111`) | Chatbot d'aide qui répond à partir des fiches | `flame/assistant/`, `pages/assistant.py`, `pages/equipements.py`, `tests/test_assistant.py` | C |
| F. Interface et 3D | Mathéo (`matheocail4`) | Habillage Streamlit, composants partagés, scène three.js, page d'accueil | `flame/ui/`, `pages/accueil.py`, `.streamlit/config.toml`, `tests/test_ui.py` | D |

Entre parenthèses, le pseudo GitHub de chacun. Le binôme teste votre page cinq minutes à chaque point d'étape et vous remplace en cas de blocage.

## Les règles pour ne pas se gêner

1. **Un dossier, une personne.** Vous ne modifiez que vos fichiers. Pour un changement chez quelqu'un d'autre, vous le lui demandez ; il le fait, ou il vous donne son accord dans la PR.
2. **Les fichiers partagés passent par le rôle A.** Cela couvre `app.py`, `flame/commun/`, `pyproject.toml` et `uv.lock`. Pour ajouter une bibliothèque, vous donnez son nom au rôle A, qui lance `uv add`.
3. **Le contrat ne bouge pas sans annonce.** Le contrat, ce sont les noms de colonnes (`flame/commun/constantes.py`) et les fonctions listées dans le `__init__.py` de chaque dossier. Pour le changer : message dans le salon de l'équipe, accord du rôle A, une ligne dans `DECISIONS.md`.
4. **On importe par la vitrine.** Le `__init__.py` d'un dossier liste ce que les autres ont le droit d'utiliser. On écrit `from flame.ui import carte_fiche`, jamais `from flame.ui.composants import ...`.
5. **Les dépendances entre dossiers sont limitées.** Tout le monde peut importer `flame.commun` et `flame.ui`. L'assistant peut importer `flame.recherche`. Personne n'importe `flame.pipeline` : le site ne lit que les CSV.
6. **Les données se lisent avec `charger_fiches()`, `charger_tests()` et `charger_publications()`.** Aucune page n'ouvre un CSV elle-même.
7. **Le scénario se lit avec `get_scenario()`.** Vos propres clés dans `st.session_state` et vos `key=` de widgets commencent par le nom de votre dossier : `recherche_question`, `assistant_historique`.
8. **Des envois petits et fréquents.** Une PR par étape qui marche, au moins toutes les deux heures. Une PR qui attend une journée finit en conflit.

## Envoyer son travail

Avec GitHub Desktop :

1. **Se mettre à jour :** branche `main`, puis « Fetch origin » et « Pull ».
2. **Créer une branche :** « Branch » puis « New branch », nommée `dossier/sujet`, par exemple `recherche/filtres` ou `ui/scene-flamme`.
3. **Coder** dans ses fichiers, en regardant le résultat avec `uv run streamlit run app.py`.
4. **Vérifier :** `uv run verifier` doit finir par « Tout est bon ».
5. **Envoyer :** « Commit », « Push », puis « Create Pull Request ».
6. **Fusionner :** « Squash and merge », puis supprimer la branche.

Qui fusionne :

- **La PR ne touche que vos fichiers :** vous la fusionnez vous-même, une fois `uv run verifier` passé.
- **La PR touche les fichiers de quelqu'un d'autre :** elle attend son accord.
- **La PR touche un fichier partagé :** elle attend le rôle A.

Deux moments sans fusion, repris du planning : la nuit entre 2h et 8h, et après le gel de dimanche 14h, où seul le rôle A fusionne des corrections.

Si GitHub Desktop affiche « conflict », ne cliquez sur rien et appelez le rôle A.

## Les vérifications

Les vérifications tournent sur l'ordinateur de chacun, avec `uv run verifier` :

| Vérification | Commande | Ce qu'elle attrape |
| --- | --- | --- |
| Mise en forme | `uv run ruff format .` | Code non formaté (corrigé tout seul) |
| Règles de code | `uv run ruff check .` | Imports inutiles, variables oubliées, erreurs probables |
| Tests | `uv run pytest` | Une page qui plante, un CSV hors contrat, une fonction cassée, un import interdit (règles 4 à 6) |

Le premier `uv run verifier` active aussi des garde-fous (les « hooks » du dossier `.githooks/`). Ils valent pour tout le monde, humains et agents IA, et refusent :

| Moment | Ce qui est refusé | Quoi faire |
| --- | --- | --- |
| Commit | Un commit sur `main` | Créer une branche `dossier/sujet` |
| Commit | Un fichier de secrets, une clé d'API, un fichier de plus de 5 Mo | Le retirer du commit |
| Commit | Un fichier d'un autre rôle (le rôle se lit dans le nom de la branche) | Le retirer, ou ajouter `Accord: <prénom du propriétaire>` au message s'il est d'accord. Si vous dites à votre agent IA que le propriétaire est d'accord, cela compte : il écrit la ligne lui-même |
| Envoi (Push) | Un envoi direct sur `main` | Envoyer sa branche et ouvrir une PR |
| Envoi (Push) | Des vérifications qui échouent | `uv run verifier`, corriger, commiter |
| Envoi (Push) | Un agent IA sans CLAIM dans l'issue n°2 | Poster le CLAIM |

Le nom de la branche donne le rôle : `integration/`, `commun/`, `pitch/` (A), `pipeline/`, `donnees/`, `data/` (B), `recherche/` (C), `comparateur/` (D), `assistant/` (E), `ui/`, `interface/` (F). Avec un autre nom, on ajoute une ligne `Role: C` au message de commit.

On ne contourne pas un garde-fou (`--no-verify`). S'il bloque à tort, on appelle le rôle A.

## Les règles de code

- **La mise en forme n'est pas un sujet.** Ruff s'en charge ; on ne la discute pas et on ne la corrige pas à la main. Lignes de 120 caractères au plus.
- **Noms en minuscules avec des tirets bas :** `charger_fiches`, `oxygene_min`. Les constantes sont en majuscules : `PILIERS`.
- **Les unités sont dans le nom :** `pression_kpa`, `debit_air_cm_s`, `oxygene_pct`.
- **Une fonction partagée a des types et une phrase d'explication :**

  ```python
  def comparer(fiches: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
      """Un tableau avec une ligne par critère et une colonne par investigation de `ids`."""
  ```

- **Le calcul va dans `flame/<dossier>/`, l'affichage dans `pages/`.** Un fichier de page reste court et ne contient que des appels à `st.` et aux fonctions de son dossier. C'est ce qui rend le calcul testable.
- **Une fonction fait une seule chose** et tient sur un écran.
- **Au moins un test par fonction partagée,** dans `tests/test_<dossier>.py`. Les tests n'appellent ni Internet ni l'API du LLM.
- **Aucune donnée NASA inventée.** Une valeur absente reste vide ou vaut `INCONNU`.
- **Aucune clé dans le code.** La clé du LLM se lit dans `st.secrets` ; le modèle à copier est `.streamlit/secrets.toml.example`.
- **Pas de code mort :** ni blocs commentés, ni `print` oubliés, ni fichiers `copie_de_...`.
- **three.js reste dans `flame/ui/three/`.** La bibliothèque est chargée avec un numéro de version précis. Python envoie des réglages à la scène ; la scène ne renvoie rien à Python.

## L'IA dans le projet

- **Déclarer l'usage.** Chaque PR dit quel outil d'IA a servi et pour quoi : le règlement demande cette déclaration, et le rôle A la compile à la fin.
- **Donner le contexte à son assistant.** `AGENTS.md` (les règles des agents, lues automatiquement par Claude Code et Codex), `BRIEF_EQUIPE_IA.md` et ce fichier, pour qu'il respecte vos dossiers et le contrat.
- **Coordonner les agents.** Un agent qui modifie le dépôt l'annonce dans l'[issue n°2 « com inter agents »](https://github.com/PA-Andries/space-apps-kit/issues/2) : CLAIM avant de commencer, RELEASE à la fin. Sans CLAIM, son envoi est refusé.
- **Signer honnêtement.** Vous commitez depuis votre compte ; l'IA est co-autrice : `Co-authored-by: Claude <noreply@anthropic.com>`.
