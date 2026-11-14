# Brief d'équipe pour assistant IA — projet « Flame in Freefall »

## À toi, l'assistant IA qui lis ce fichier

Tu vas aider un membre d'une équipe de six personnes pendant un hackathon de 48 heures. Chaque membre de l'équipe a donné ce même fichier à son propre assistant, pour que tous les assistants proposent des choses compatibles entre elles.

La personne va se présenter en disant « je suis [prénom] » ou « je suis le rôle [lettre] ». Retrouve son rôle dans la section 7, puis réponds dans cet ordre :

1. Rappelle-lui son rôle, ses fichiers et son binôme, en deux ou trois lignes.
2. Demande-lui l'heure qu'il est, si elle ne l'a pas dite, pour la situer dans le planning (section 8).
3. Dis-lui quoi faire maintenant, étape par étape, et quel est son prochain livrable avec son heure limite.
4. Propose de l'accompagner sur la première étape.

Ce qu'il faut savoir sur l'équipe : c'est leur premier hackathon et ils débutent en code. Explique simplement, sans jargon non expliqué, et donne du code court, complet et prêt à coller, plutôt que des fragments.

Pour que les six assistants restent alignés, tiens-toi à ces règles :

- **Ne change ni les outils, ni l'organisation du site, ni les noms de colonnes, ni les noms de fichiers, ni les fonctions partagées** décrits ici. Si tu penses qu'un changement est nécessaire, dis à la personne d'en parler au rôle A (Intégration) au lieu de l'appliquer.
- **Ne fais modifier à la personne que ses propres fichiers** (section 6). Si sa demande touche le fichier de quelqu'un d'autre, dis-lui de s'adresser au propriétaire.
- **Respecte les règles de `CONTRIBUTING.md`** : c'est là que sont écrites les règles de collaboration et de code. Avant chaque envoi, fais lancer `uv run verifier`.
- **N'invente jamais une donnée NASA.** Si une valeur n'est pas dans un document que la personne t'a fourni, écris « inconnu ». Un site crédible avec des trous vaut mieux qu'un site complet avec des chiffres faux.
- **Préfère la solution la plus simple qui marche.** L'objectif est un site qui fonctionne samedi 19h, pas un site parfait.

## 1. Le projet en bref

- **Événement :** NASA Space Apps Challenge 2026, défi « Flame in Freefall ». Samedi 14 et dimanche 15 novembre 2026.
- **Ce que demande NASA :** un tableau de bord web, propulsé par une IA, qui résume, classe et interprète les expériences NASA de combustion en microgravité, pour en tirer des enseignements de sécurité incendie pour l'exploration spatiale.
- **Les trois objectifs suggérés par l'énoncé :**
  1. Identifier les investigations les plus utiles à chaque habitat : vaisseau, station, base lunaire, base martienne, rover pressurisé.
  2. Extraire des données utiles à la modélisation prédictive de l'inflammabilité.
  3. Mettre en avant la recherche utile aux équipements de sécurité de demain.
- **Bonus possible :** les applications sur Terre (extincteurs à brouillard d'eau, détection de fumée, équipement des pompiers).
- **Notre mission (recadrage du samedi 14 novembre, validé par PA) :** l'utilisateur décrit l'environnement qu'il étudie (habitat, oxygène, pression, gravité, combustible). Le tableau de bord lui montre où se situent les tests NASA en microgravité par rapport à ces conditions, classe et explique les investigations utiles, fournit les données pour la modélisation et la recherche utile aux équipements de demain. Il dit clairement ce qu'on ne sait pas : aucune donnée en gravité partielle. Une IA répond aux questions en citant ses sources.
- **Public visé :** étudiants, chercheurs et ingénieurs en aérospatial.
- **À rendre :** le lien du site en ligne, une vidéo très courte (30 secondes maximum d'après les règles 2025, à confirmer) ou 7 slides, et une page projet.
- **Notre heure limite interne :** dimanche 20h00. Gel des fonctionnalités dimanche 14h00.

## 2. L'essentiel du sujet

- **En microgravité, il n'y a pas d'air chaud qui monte.** La flamme devient une sphère bleue, alimentée lentement en oxygène par diffusion.
- **L'oxygène et le débit d'air sont les deux paramètres clés** de l'inflammabilité.
- **NASA organise la sécurité incendie en trois piliers :** prévenir, détecter, éteindre. Ils viennent du contexte de la consigne, pas de ses objectifs : sur le site, ils servent de filtre et d'étiquette, pas de note dans le classement.
- **Atmosphères à connaître :**
  - Terre : 21 % d'oxygène, 14,7 psi (environ 101 kPa). Source : énoncé.
  - Base lunaire et rovers pressurisés : 30 % d'oxygène ou plus, 10,2 psi (70,3 kPa) ou moins. Source : énoncé. Ce sont des **bornes** : le site les montre comme une zone, jamais comme un point.
  - Combinaison spatiale : 100 % d'oxygène, 4,3 psi (environ 30 kPa). Source : énoncé.
  - Vaisseau et station : 21 %, environ 101 kPa. **Hypothèse à sourcer**, absente de l'énoncé.
  - Base martienne : **inconnu**. L'énoncé ne donne aucun chiffre ; le site n'en affiche aucun.
- **Il n'existe aucune donnée en gravité lunaire ou martienne dans la base NASA.** Les résultats en microgravité et sur Terre encadrent ce qui se passe entre les deux. Le site montre ces bornes et n'invente aucune prédiction.
- **Hors sujet :** les fusées et leurs carburants.

## 3. Les données

Deux sources NASA, toutes deux traitées par le rôle B :

- **PSI (Physical Sciences Informatics)** pour les investigations et leurs tests : https://psi.nasa.gov/physci/repo/search?q=combustion
- **NTRS (NASA Technical Reports Server)** pour les rapports et articles : https://ntrs.nasa.gov/api/openapi/ . Son API est publique et sans clé ; `flame/pipeline/ntrs.py` l'interroge déjà (environ 1 077 rapports pour « microgravity combustion »).

PSI n'a pas d'API. On consulte les pages à la main et on télécharge quelques petits fichiers. La recherche « combustion » donne 26 résultats : 19 investigations en vol, 5 études au sol, 2 hors sujet.

### Les 19 investigations en vol

| N° PSI | Code | Ce qui brûle, et où | Pilier | Priorité |
| --- | --- | --- | --- | --- |
| PSI-26 | BASS | Tissu, boîte à gants MSG | Prévenir | 1 |
| PSI-25 | BASS-II | Solides, MSG | Prévenir, Éteindre | 1 |
| PSI-98 | Saffire-I | Grand échantillon de tissu, cargo Cygnus | Prévenir | 1 |
| PSI-99 | Saffire-II | Idem | Prévenir | 1 |
| PSI-100 | Saffire-III | Idem | Prévenir | 1 |
| PSI-102 | SAME | Fumées de matériaux, MSG | Détecter | 1 |
| PSI-101 | SAME-R | Fumées de matériaux, MSG | Détecter | 1 |
| PSI-47 | DAFT / DAFT-2 | Pas de flamme : test d'un compteur de particules | Détecter | 1 |
| PSI-69 | FLEX | Gouttes de carburant liquide, MDCA dans le CIR | Éteindre | 1 |
| PSI-20 | ACME BRE | Gaz imitant un matériau, CIR | Prévenir | 1 |
| PSI-159 | ACME CFI-G | Gaz, CIR ; tests les plus riches en oxygène | Prévenir | 2 |
| PSI-68 | FLEX-2 | Gouttes de carburant, MDCA dans le CIR | Éteindre | 2 |
| PSI-39 | CFI | Gouttes de carburant, MDCA dans le CIR | Prévenir | 2 |
| PSI-22 | ACME E-FIELD Flames | Gaz, CIR ; imite la gravité partielle | Lune et Mars | 2 |
| PSI-107 | SPICE | Gaz, MSG | Détecter | 2 |
| PSI-106 | SLICE | Gaz, MSG | Fondamental | 3 |
| PSI-10 | ACME Flame Design | Gaz, CIR | Fondamental | 3 |
| PSI-21 | ACME CLD Flame | Gaz, CIR | Fondamental | 3 |
| PSI-23 | ACME s-Flame | Gaz, CIR | Fondamental | 3 |

Les colonnes Pilier et Priorité sont une proposition de l'équipe. Priorité 1 = à mettre en fiche en premier.

Les 5 études au sol réutilisent des données de vol pour construire des modèles : PSI-117 et PSI-142 (données FLEX), PSI-62 (BASS), PSI-60 (SPICE), PSI-115 (SAME). SoFIE, FLARE et FM2 ne sont pas dans PSI : pas de fiche.

### Quoi télécharger sur une page PSI

Dans la section « Data files and documents », trois choses seulement :

1. Les fichiers CSV du dossier « Experimental table » (une ligne par test).
2. Le rapport final PDF du dossier « Reports ».
3. Le fichier `.zip` du dossier « Investigation Metadata Files ».

On ignore « Raw Data » et « Engineering Documents », qui pèsent des centaines de gigaoctets. On copie aussi le texte de la section « Description ».

### Les trois tableaux du site (noms de colonnes figés)

`data/investigations.csv` — une ligne par investigation :

| Colonne | Contenu |
| --- | --- |
| `id` | Code court, par exemple `FLEX` |
| `psi` | Numéro PSI, par exemple `PSI-69` |
| `nom` | Nom complet |
| `pilier` | `Prévenir`, `Détecter`, `Éteindre` ; plusieurs valeurs séparées par `;` |
| `priorite` | 1, 2 ou 3 |
| `objectif` | Une ou deux phrases |
| `type_combustible` | `solide`, `liquide`, `gaz` ou `aucun` |
| `combustible` | Ce qui brûle, sa forme et sa taille |
| `materiel` | Par exemple `MSG`, `CIR / MDCA`, `Cygnus` |
| `oxygene_min`, `oxygene_max` | Plage d'oxygène testée, en % |
| `pression_kpa` | Pression testée, en kPa |
| `debit_air` | Vitesse de l'air, en cm/s |
| `ce_qui_varie` | Ce qui change d'un test à l'autre |
| `capteurs` | Ce qui a été mesuré, et comment |
| `habitats` | Habitats concernés, séparés par `;` |
| `nb_tests` | Nombre de tests, si connu |
| `resume` | Cinq lignes en langage simple |
| `source_psi`, `doi`, `source_rapport` | Liens et références |
| `verifie_par` | Initiales de la personne qui a validé la fiche ; vide = fiche non affichée |

`data/tests.csv` — une ligne par test : `investigation_id`, `test_id`, `combustible`, `oxygene_pct`, `pression_kpa`, `debit_air_cm_s`, `resultat`, `source`.

`data/publications.csv` — une ligne par rapport NTRS : `ntrs_id`, `titre`, `annee`, `auteurs`, `resume`, `url`, `investigation_id` (la fiche à laquelle le rapport se rattache, vide si aucune).

La liste de référence des colonnes est dans `flame/commun/constantes.py`, et un test vérifie que les trois fichiers la respectent. Tant que `data/investigations.csv` n'existe pas, le site tourne sur les données fictives de `data/exemples/`, pour que personne n'attende le rôle B.

Conversions utiles : une fraction d'oxygène (colonne `XO2` de PSI) × 100 = pourcentage ; 1 bar = 100 kPa ; 1 atm = 101,3 kPa ; 1 psi = 6,895 kPa.

Une valeur inconnue reste vide ou vaut `inconnu`. Elle n'est jamais devinée.

## 4. Les outils (ne pas en changer)

- **Python 3.12** pour tout, **Streamlit** pour le site, **pandas** pour les tableaux, **Plotly Express** pour les graphiques.
- **three.js** pour la scène 3D, affichée dans Streamlit par `flame/ui/scene.py`. Python envoie des réglages à la scène ; la scène ne renvoie rien.
- **uv** pour installer le même environnement chez tout le monde : `uv sync`, puis `uv run ...`. Jamais `pip install`.
- **API d'un LLM** pour l'assistant. La clé est rangée dans les Secrets de Streamlit Community Cloud, jamais dans le code.
- **GitHub + GitHub Desktop** : une branche courte par tâche, une pull request (PR), fusion quand `uv run verifier` est passé.
- **`uv run verifier`** : vérifie la mise en forme, les règles de code et les tests sur son ordinateur. Des garde-fous (`.githooks/`) relancent ces vérifications à chaque envoi et refusent un commit qui sort de son dossier.
- **Streamlit Community Cloud** pour la mise en ligne : chaque fusion dans `main` met le site à jour.

Pas de base de données, pas de serveur séparé, pas de React. Le rôle B choisit comment il remplit les fiches (Google Sheets ou script) ; seuls comptent les trois CSV de `data/`.

## 5. L'organisation du site

Le site part de l'**environnement de l'utilisateur**, pas des données ni des piliers (recadrage du samedi 14 novembre, validé par PA). Le parcours :

1. Je décris mon environnement.
2. Je vois où sont les tests NASA par rapport à mes conditions.
3. Je lis les investigations classées, et ce qu'on ne sait pas.
4. Je compare ou j'exporte les données.
5. Je pose mes questions à l'assistant.

L'environnement choisi en page 1 est mémorisé pour toutes les pages et rappelé dans la barre latérale. Tout l'affichage est en anglais.

| Page | Fichier | Rôle | Objectif NASA | Onglets | Ce que l'utilisateur reçoit |
| --- | --- | --- | --- | --- | --- |
| 1. My environment | `pages/accueil.py` | F (graphique : D) | Point d'entrée | — | Son environnement mémorisé, le graphique des tests avec ceux qui correspondent surlignés, un compteur, les 3 investigations les plus pertinentes |
| 2. Investigations | `pages/recherche.py` | C | 1 | Classement · Fiche · Ce qu'on ne sait pas | Les investigations classées pour son environnement, avec la raison du classement, le détail de chaque fiche et les trous de données |
| 3. Data | `pages/donnees.py` (à créer) | D | 2 | Carte · Tableau + CSV · Variables et capteurs | Le grand graphique des conditions testées, les tests filtrés et téléchargeables, ce que chaque investigation a mesuré et fait varier |
| 4. Compare | `pages/comparateur.py` | D | 1 et 2 | (ceux de la page actuelle) | Portraits côte à côte, points communs et différences, conditions testées situées par rapport à l'environnement |
| 5. Equipment and Earth | `pages/equipements.py` (à créer) | E | 3 + bonus | Détecter · Éteindre · Sur Terre | La recherche utile aux détecteurs et extincteurs de demain, et les retombées sur Terre, avec leurs sources |
| 6. Assistant | `pages/assistant.py` | E | Tous | — | Une réponse fondée sur les fiches et sur son environnement, avec les `id`, ou « je ne sais pas » |

**La page 1 en détail.** À gauche, un formulaire :
- **Type d'habitat**, qui pré-remplit l'oxygène, la pression et la gravité, chacun avec sa source ou « inconnu ». Les valeurs restent modifiables.
- **Combustible** (solide, liquide, gaz), **débit d'air** (optionnel) et **pilier** (optionnel, « tous » par défaut).

À droite, le graphique et un compteur, par exemple « 66 tests · 2 investigations · 0 en gravité partielle ». En bas, les 3 investigations les plus pertinentes. La flamme 3D reste, en petit, comme illustration.

**Le graphique des conditions testées.** Aucun test n'a les trois mesures à la fois (O₂, pression et débit d'air) : un nuage en 3D serait vide. On montre donc **deux vues 2D qui partagent l'axe de l'oxygène** :
- **O₂ × pression** : 1 022 tests, des flammes de gaz et des gouttes. La pression est en échelle logarithmique.
- **O₂ × débit d'air** : 131 tests de solides (BASS-II, Saffire), dont la pression n'est pas notée.

Chaque point est un vrai test de `data/tests.csv`. Le graphique dessine les zones sourcées (Terre, base lunaire et rover en zone, combinaison) et surligne les tests qui correspondent à l'environnement choisi. Mars n'a pas de zone. D part des fonctions `carte()` et `points()` de `flame/comparateur/`. Le même graphique sert en page 1 et en page 3.

Bonus, seulement si tout le reste marche dimanche 9h : mode profil (même fiche expliquée différemment selon le public), brief téléchargeable par habitat, quiz « Mythe ou réalité ».

### Le code commun : `flame/commun/` (propriété du rôle A)

Toutes les pages passent par ce dossier pour lire les données et le scénario. Utilise exactement ces noms :

```python
from flame.commun import ATMOSPHERES, HABITATS, INCONNU, PILIERS, PROFILS
from flame.commun import charger_fiches, charger_publications, charger_tests, get_scenario

fiches = charger_fiches()  # un DataFrame pandas, une ligne par investigation validée
scenario = get_scenario()  # {"habitat": ..., "pilier": ..., "profil": ...}
```

`ATMOSPHERES` donne, pour chaque habitat, l'oxygène en % et la pression en kPa. Base lunaire et rover : chiffres de l'énoncé. Les autres sont des hypothèses à valider.

**À faire par le rôle A (recadrage) :**
- **Étendre le scénario**, avec les clés prévues `habitat`, `oxygene_pct`, `pression_kpa`, `gravite`, `type_combustible`, `debit_air_cm_s`, `pilier` (optionnel) et `profil`. Jusque-là, les clés actuelles de `get_scenario()` restent valables.
- **Corriger `ATMOSPHERES`** comme décrit en section 2 : Mars inconnue, la Lune et le rover en bornes.

### Ce que chaque dossier offre aux autres

Chaque dossier expose ses fonctions dans son `__init__.py`. Les versions de départ existent déjà et marchent sur les données d'exemple ; chaque rôle les remplace par la vraie version sans changer leur nom ni leurs paramètres.

| Dossier | Rôle | Fonction | Ce qu'elle fait |
| --- | --- | --- | --- |
| `flame/pipeline/` | B | `chercher_publications(question, nombre)` | Interroge l'API NTRS ; sert à fabriquer `data/publications.csv` |
| `flame/recherche/` | C | `rechercher(question, fiches, scenario)` | Renvoie les fiches triées, avec une colonne `score` |
| `flame/comparateur/` | D | `comparer(fiches, ids)` | Renvoie un tableau, une colonne par investigation |
| `flame/assistant/` | E | `repondre(question, historique, fiches)` | Renvoie le texte de la réponse |
| `flame/ui/` | F | `afficher_cadre()`, `carte_fiche(fiche)`, `scene_3d(gravite, oxygene)` | La barre latérale, l'affichage d'une fiche, la scène three.js |

### Le score du classement (rôle C)

Depuis le recadrage, **le pilier ne compte plus dans le score.** C'est un **filtre**, qui montre seulement les investigations utiles au pilier choisi, et une **étiquette** (« primaire », « secondaire » ou « indirect », c'est-à-dire le jugement de l'équipe).

Le score sur 100 repose sur les preuves, et il est affiché avec sa raison :

- **Atmosphère (40 points) :** des tests ont été faits dans les conditions de l'environnement (O₂ et pression).
- **Combustible (25 points) :** les solides comptent le plus, car un habitat contient surtout des tissus et des plastiques ; puis les liquides, puis les gaz.
- **Gravité (20 points) :** les résultats s'appliquent directement (microgravité pour un vaisseau ou une station) ou ne sont qu'une borne (Lune, Mars ; seule E-FIELD Flames imite une gravité partielle).
- **Données (15 points) :** le nombre de tests disponibles.

Ces poids sont un jugement d'équipe : le site le dit. La pertinence par habitat s'appuie sur `data/psi/relevance.csv` (rôle B), sans son poids de pilier. Elle ne s'appuie plus sur la colonne `habitats` des fiches, calculée sur la seule plage d'oxygène, qui laisse 14 fiches sur 24 sans habitat.

## 6. Organisation du dépôt

```text
app.py                      liste des pages, rien d'autre           rôle A
flame/commun/               contrat : colonnes, données, scénario   rôle A
flame/pipeline/             API NTRS, préparation des CSV           rôle B
flame/recherche/            moteur de recherche et score            rôle C
flame/comparateur/          comparaison d'investigations            rôle D
flame/assistant/            chatbot, consignes dans prompts/        rôle E
flame/ui/                   cadre, composants, three/ (three.js)    rôle F
pages/accueil.py                                                    rôle F
pages/recherche.py                                                  rôle C
pages/comparateur.py                                                rôle D
pages/donnees.py            page Data (à créer)                     rôle D
pages/assistant.py                                                  rôle E
pages/equipements.py        page Equipment and Earth (à créer)      rôle E
data/                       les trois CSV du site                   rôle B
data/exemples/              données fictives pour développer        rôle A
tests/test_<dossier>.py     un fichier de tests par rôle
tests/test_app.py           chaque page s'ouvre sans erreur         rôle A
tests/test_contrat.py       les CSV respectent les colonnes         rôle A
pitch/                      vidéo, sous-titres, page projet         rôle A
pyproject.toml, uv.lock     bibliothèques                           rôle A
.githooks/, AGENTS.md       garde-fous et règles des agents IA      rôle A
.streamlit/config.toml      couleurs du site                        rôle F
CONTRIBUTING.md             règles de collaboration et de code
DECISIONS.md                journal des décisions                   rôle A
GUIDE_SOURCES.md            guide détaillé des sources NASA
```

Le calcul est dans `flame/<dossier>/`, l'affichage dans `pages/`. Un fichier de page reste court.

## 7. Les six rôles

| Rôle | Prénom | Mission | Binôme |
| --- | --- | --- | --- |
| A. Intégration et pitch | Clément, **remplacé par PA** pendant son absence | Fusionne les PR, garde le site en ligne, tient `flame/commun/` et les garde-fous, valide chaque fiche, règle les poids du score, prépare les 20 questions de référence, la vidéo, la page projet et le README | B |
| B. Données | PA | Interroge l'API NTRS, lit les pages PSI, produit `investigations.csv`, `tests.csv`, `publications.csv` et les tables de `data/psi/` | A |
| C. Recherche | Martin | La page Investigations : classement sur les preuves avec sa raison, pilier en filtre, détail de chaque fiche, « ce qu'on ne sait pas » | E |
| D. Comparateur | Hugo | Le graphique des conditions testées (pages 1 et 3), la page Data et la page Compare | F |
| E. Assistant | Ethan | Le chatbot d'aide (consignes, appel du LLM, réponses qui citent les fiches et tiennent compte de l'environnement) et la page Equipment and Earth | C |
| F. Interface et 3D | Mathéo | L'habillage Streamlit, les composants partagés, la scène three.js et la page 1 « My environment » avec son formulaire | D |

Pourquoi ces binômes : A valide les fiches que B produit ; l'assistant de E s'appuie sur le moteur de C pour retrouver les bonnes fiches ; le comparateur de D a besoin des composants et des graphiques de F.

### Ce que chaque rôle fait, étape par étape

- **Samedi jusqu'à 13h — démarrer.** Chacun installe le dépôt, lance le site sur les données d'exemple et ouvre sa première PR. A met le site en ligne. B commence par les 10 investigations de priorité 1.
- **Samedi 13h à 19h — les pages.** C, D, E et F construisent leur page sur les données d'exemple, puis sur les vraies dès que B les livre. E branche le LLM. A valide les fiches de B et écrit le texte de la vidéo.
- **Samedi 17h à 22h — le recadrage.**
  - A : étend le scénario partagé et corrige `ATMOSPHERES` (section 5). Attribue `pages/donnees.py` à D et `pages/equipements.py` à E dans `CONTRIBUTING.md` et dans `COULOIRS` de `src/space_apps_kit/regles.py`. Ajoute les nouvelles pages à `app.py` dès que leurs fichiers existent.
  - F : construit le formulaire de la page 1.
  - D : construit le graphique des conditions testées, à partir de `carte()` et `points()`.
  - C : sort le pilier du score et affiche la raison du classement.
  - B : dans `relevance.csv`, renomme « Réagir » en « Éteindre », retire le poids du pilier et confirme l'O₂ de BASS et Saffire-III.
- **Samedi 22h à 1h — l'intelligence.**
  - D : page Data (tableau filtré + CSV).
  - C : onglet « Ce qu'on ne sait pas ».
  - E : l'assistant lit l'environnement de la page 1 et reçoit des outils (filtre par habitat, comptage de tests). E teste l'assistant sur les 20 questions de référence ; A note les réponses.
  - F : branche le graphique de D en page 1.
- **Dimanche 9h à 14h — solidifier.** E livre la page Equipment and Earth. Corrections, textes clairs, bonus qui marchent déjà. Ce qui ne marche pas à 11h est abandonné.
- **Dimanche après 14h — raconter.** Le code est gelé. Tout le monde aide A sur la vidéo, les sous-titres anglais et la page projet. A garde le site en ligne.

Les binômes testent la page l'un de l'autre cinq minutes à chaque point d'étape, et se remplacent en cas de blocage.

## 8. Le planning

| Moment | Ce qui doit être vrai |
| --- | --- |
| Samedi 13h | Squelette du site en ligne ; chacun fait tourner le site chez soi et a ouvert une première PR |
| Samedi 16h | Les 10 fiches de priorité 1 sont dans `data/`, validées par le rôle A |
| Samedi 18h | Recadrage inscrit dans ce brief ; scénario étendu et `ATMOSPHERES` sourcées (rôle A) |
| Samedi 19h | Le site en ligne fonctionne sur un téléphone avec les vraies données |
| Samedi 22h | Page 1 avec formulaire et graphique des conditions testées ; classement sans pilier dans le score |
| Samedi 1h | Page Data (tableau + CSV) ; l'assistant lit l'environnement ; au moins 15 réponses justes sur les 20 questions de référence |
| Nuit | Au moins 5 heures de sommeil ; aucune fusion entre 2h et 8h |
| Dimanche 9h | Page Equipment and Earth ; choix des bonus à garder |
| Dimanche 14h | Gel des fonctionnalités |
| Dimanche 20h | Soumission envoyée |

Mini-points de 10 minutes à 12h, 16h et 22h samedi, 12h dimanche : qu'ai-je fini, que fais-je ensuite, qu'est-ce qui me bloque.

## 9. Travailler à plusieurs sans se gêner

Les règles complètes sont dans `CONTRIBUTING.md`. L'essentiel :

- **Un dossier, une personne.** On ne modifie jamais le fichier d'un autre ; on lui demande.
- **Les fichiers partagés passent par le rôle A :** `app.py`, `flame/commun/`, `pyproject.toml`, `uv.lock`. Pour ajouter une bibliothèque, on la demande au rôle A.
- **Le cycle, toutes les une à deux heures :** Pull de `main`, nouvelle branche `dossier/sujet`, modifier ses fichiers, `uv run verifier`, Commit, Push, pull request, fusion.
- **Tester avant d'envoyer :** `uv run streamlit run app.py`, puis vérifier sa page.
- **Si GitHub Desktop affiche « conflict », on ne clique sur rien** et on appelle le rôle A.
- **Bloqué depuis 30 minutes :** on écrit dans le salon `#entraide` ce qu'on a essayé.

## 10. Les garde-fous

- **Pas de source, pas d'affichage.** Chaque information du site renvoie vers sa page PSI ou son rapport.
- **Une fiche sans initiales dans `verifie_par` n'est pas affichée.**
- **L'IA du site répond uniquement à partir des fiches** et a le droit de dire « je ne sais pas ».
- **Aucun chiffre inventé pour la Lune ou Mars.** Mars : atmosphère inconnue, le site n'affiche rien. Lune et rover : une zone (≥ 30 % d'O₂, ≤ 70,3 kPa), jamais un point inventé.
- **La clé d'API ne va jamais dans un fichier du dépôt.**
- **Les gros fichiers PSI ne vont pas dans le dépôt** : seuls les trois CSV de synthèse.
- **Les données d'exemple ne sont jamais présentées comme réelles** : tant qu'elles servent, le site l'affiche en haut de chaque page.
- **Une phrase sur le site :** outil d'aide à la compréhension, pas une certification de sécurité.
