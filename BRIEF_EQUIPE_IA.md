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

- **Ne change ni les outils, ni l'organisation du site, ni les noms de colonnes, ni les noms de fichiers** décrits ici. Si tu penses qu'un changement est nécessaire, dis à la personne d'en parler au Capitaine (rôle A) au lieu de l'appliquer.
- **Ne fais modifier à la personne que ses propres fichiers.** Si sa demande touche le fichier de quelqu'un d'autre, dis-lui de s'adresser au propriétaire.
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
- **Public visé :** étudiants, chercheurs et ingénieurs en aérospatial.
- **À rendre :** le lien du site en ligne, une vidéo très courte (30 secondes maximum d'après les règles 2025, à confirmer) ou 7 slides, et une page projet.
- **Notre heure limite interne :** dimanche 20h00. Gel des fonctionnalités dimanche 14h00.

## 2. L'essentiel du sujet

- **En microgravité, il n'y a pas d'air chaud qui monte.** La flamme devient une sphère bleue, alimentée lentement en oxygène par diffusion.
- **L'oxygène et le débit d'air sont les deux paramètres clés** de l'inflammabilité.
- **NASA organise la sécurité incendie en trois piliers :** prévenir, détecter, éteindre. Tout le site s'appuie sur ces trois mots.
- **Atmosphères à connaître (chiffres de l'énoncé) :**
  - Terre : 21 % d'oxygène, 14,7 psi (environ 101 kPa).
  - Base lunaire et rovers pressurisés : 30 % d'oxygène ou plus, 10,2 psi (environ 70 kPa) ou moins.
  - Combinaison spatiale : 100 % d'oxygène, 4,3 psi (environ 30 kPa).
- **Il n'existe aucune donnée en gravité lunaire ou martienne dans la base NASA.** Les résultats en microgravité et sur Terre encadrent ce qui se passe entre les deux. Le site montre ces bornes et n'invente aucune prédiction.
- **Hors sujet :** les fusées et leurs carburants.

## 3. Les données

Tout vient de PSI (Physical Sciences Informatics), la base publique de NASA : https://psi.nasa.gov/physci/repo/search?q=combustion

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

### Les deux tableaux du site (noms de colonnes figés)

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

Conversions utiles : une fraction d'oxygène (colonne `XO2` de PSI) × 100 = pourcentage ; 1 bar = 100 kPa ; 1 atm = 101,3 kPa ; 1 psi = 6,895 kPa.

Une valeur inconnue reste vide ou vaut `inconnu`. Elle n'est jamais devinée.

## 4. Les outils (ne pas en changer)

- **Python** pour tout, **Streamlit** pour le site, **pandas** pour les tableaux, **Plotly Express** pour les graphiques.
- **Google Sheets** pour remplir les fiches à plusieurs ; le Capitaine l'exporte en CSV.
- **API d'un LLM** pour l'IA du site. La clé est rangée dans les Secrets de Streamlit Community Cloud, jamais dans le code.
- **GitHub + GitHub Desktop** pour partager le code, sans branches : tout le monde travaille sur `main`, chacun dans ses fichiers.
- **Streamlit Community Cloud** pour la mise en ligne : chaque Push met le site à jour.

Pas de base de données, pas de serveur séparé, pas de React. Avec une vingtaine de fiches, tout tient dans deux fichiers CSV et dans un seul message envoyé à l'IA.

## 5. L'organisation du site

Le site part de la question de l'utilisateur (« j'ai tel habitat, tel besoin »), pas des données.

| Page | Fichier | Ce que l'utilisateur donne | Ce qu'il reçoit |
| --- | --- | --- | --- |
| Accueil « Mon scénario » | `app.py` | Un habitat, un pilier, un profil | Le scénario est mémorisé pour toutes les pages ; aperçu des investigations les plus utiles |
| Classement | `pages/1_Classement.py` | Le scénario | Les investigations triées par score, avec l'explication de chaque rang |
| Fiches | `pages/2_Fiches.py` | Une investigation choisie | La fiche en dix lignes, avec les liens PSI |
| Comparateur | `pages/3_Comparateur.py` | Deux ou trois investigations | Points communs et différences, rédigés par l'IA |
| Données et carte des lacunes | `pages/4_Donnees.py` | Des filtres : combustible, oxygène, pression | Le tableau des tests, téléchargeable ; un graphique oxygène × pression où chaque point est un test, avec la zone « base lunaire » dessinée par-dessus |
| Assistant | `pages/5_Assistant.py` | Une question libre | Une réponse fondée sur les fiches, avec leurs `id`, ou « je ne sais pas » |

Bonus, seulement si tout le reste marche dimanche 9h : mode profil (même fiche expliquée différemment selon le public), brief téléchargeable par habitat, page « Retombées sur Terre », quiz « Mythe ou réalité », curseur de gravité de 0 g à 1 g.

### Le code commun : `utils.py` (propriété du Capitaine)

Toutes les pages passent par ce fichier pour lire les données et le scénario. C'est le seul lien technique entre les pages : utilise exactement ces noms.

```python
import pandas as pd
import streamlit as st

HABITATS = ["Vaisseau", "Station", "Base lunaire", "Base martienne", "Rover pressurisé"]
PILIERS = ["Prévenir", "Détecter", "Éteindre"]
PROFILS = ["Étudiant", "Chercheur", "Ingénieur"]

# Atmosphère type de chaque habitat : (oxygène en %, pression en kPa).
# Base lunaire et rover : chiffres de l'énoncé. Les autres sont des hypothèses à valider.
ATMOSPHERES = {
    "Vaisseau": (21, 101),
    "Station": (21, 101),
    "Base lunaire": (30, 70),
    "Base martienne": (30, 70),
    "Rover pressurisé": (30, 70),
}


@st.cache_data
def charger_fiches():
    fiches = pd.read_csv("data/investigations.csv")
    return fiches[fiches["verifie_par"].notna()]


@st.cache_data
def charger_tests():
    return pd.read_csv("data/tests.csv")


def get_scenario():
    return {
        "habitat": st.session_state.get("habitat", "Base lunaire"),
        "pilier": st.session_state.get("pilier", "Prévenir"),
        "profil": st.session_state.get("profil", "Étudiant"),
    }
```

Dans une page, on écrit `from utils import charger_fiches, get_scenario`. L'accueil enregistre les choix avec `st.session_state["habitat"] = ...`, et de même pour `"pilier"` et `"profil"`.

### Le score du classement

Un score sur 100, affiché avec son détail pour rester explicable :

- **Pilier (40 points) :** l'investigation correspond au pilier choisi.
- **Oxygène (25 points) :** la plage testée couvre l'oxygène de l'habitat, ou s'en approche.
- **Combustible (20 points) :** les solides comptent le plus, car un habitat contient surtout des tissus et des plastiques ; puis liquides, puis gaz.
- **Données (15 points) :** nombre de tests disponibles.

Ces poids sont un point de départ ; le rôle F les ajuste avec le rôle B.

## 6. Organisation du dépôt

```text
app.py                     accueil « Mon scénario »      rôle A
utils.py                   code commun                   rôle A
requirements.txt           bibliothèques                 rôle A
data/investigations.csv    les fiches                    rôle A (export du Google Sheet)
data/tests.csv             les tests                     rôle A (fourni par le rôle D)
pages/1_Classement.py                                    rôle B
pages/2_Fiches.py                                        rôle C
pages/3_Comparateur.py                                   rôle C
pages/4_Donnees.py                                       rôle D
pages/5_Assistant.py                                     rôle E
prompts/                   consignes données à l'IA      rôle E
pitch/                     vidéo, sous-titres            rôle F
README.md                                                rôle F
GUIDE_SOURCES.md           guide détaillé des sources NASA
```

## 7. Les six rôles

Prénoms à compléter par l'équipe avant d'envoyer ce fichier.

| Rôle | Prénom | Mission | Investigations à mettre en fiche d'ici samedi 13h | Binôme |
| --- | --- | --- | --- | --- |
| A. Capitaine | (à compléter) | Page d'accueil, `utils.py`, mise en ligne, export des données, dépannage des autres | Aucune : il met en ligne le squelette du site avec trois fiches d'exemple | F |
| B. Classement | (à compléter) | Le score et la page Classement | BASS, BASS-II | C |
| C. Fiches et Comparateur | (à compléter) | Les pages Fiches et Comparateur | Saffire-I, Saffire-II, Saffire-III | B |
| D. Données et carte | (à compléter) | La page Données, la carte oxygène × pression, la préparation de `tests.csv` à partir des CSV de PSI | FLEX, ACME BRE, avec leurs tableaux de tests | E |
| E. IA | (à compléter) | La page Assistant, les consignes de l'IA, le résumé des fiches, puis le mode profil et le brief | SAME, SAME-R | D |
| F. Qualité et pitch | (à compléter) | Validation de chaque fiche, 20 questions de référence, réglage des poids du score, vidéo, page projet, README | DAFT, puis relecture des fiches des autres | A |

### Ce que chaque rôle fait, étape par étape

- **Samedi jusqu'à 13h — la collecte.** Tout le monde sauf A remplit ses fiches dans le Google Sheet, en suivant la routine de la section 3. A met le squelette du site en ligne.
- **Samedi 13h à 19h — les pages.** Chacun construit sa page avec les vraies données. E branche l'IA. F valide les fiches et écrit le texte de la vidéo. Les investigations de priorité 2 sont mises en fiche par qui a du temps.
- **Samedi 19h à 1h — l'intelligence.** B affine le score avec F. E teste l'assistant sur les 20 questions de référence ; F note les réponses. D termine la carte des lacunes. C ajoute au comparateur le texte rédigé par l'IA.
- **Dimanche 9h à 14h — solidifier.** Corrections, textes clairs, bonus qui marchent déjà. Ce qui ne marche pas à 11h est abandonné.
- **Dimanche après 14h — raconter.** Le code est gelé. B, C, D et E aident F sur la vidéo, les sous-titres anglais et la page projet. A garde le site en ligne.

Les binômes testent la page l'un de l'autre cinq minutes à chaque point d'étape, et se remplacent en cas de blocage.

## 8. Le planning

| Moment | Ce qui doit être vrai |
| --- | --- |
| Samedi 13h | 10 fiches de priorité 1 validées ; squelette du site en ligne |
| Samedi 19h | Le site en ligne fonctionne sur un téléphone avec les vraies données |
| Samedi 1h | Au moins 15 réponses justes sur les 20 questions de référence |
| Nuit | Au moins 5 heures de sommeil ; aucun Push entre 2h et 8h |
| Dimanche 9h | Choix des bonus à garder |
| Dimanche 14h | Gel des fonctionnalités |
| Dimanche 20h | Soumission envoyée |

Mini-points de 10 minutes à 12h, 16h et 22h samedi, 12h dimanche : qu'ai-je fini, que fais-je ensuite, qu'est-ce qui me bloque.

## 9. Travailler à plusieurs sans se gêner

- **Les quatre gestes dans GitHub Desktop, toutes les 30 à 60 minutes :** Pull, modifier ses fichiers, Commit avec un message court, Push.
- **Un fichier, une personne.** On ne modifie jamais le fichier d'un autre ; on lui demande.
- **`utils.py` et `data/` ne sont modifiés que par le rôle A.**
- **Si GitHub Desktop affiche « conflict », on ne clique sur rien** et on appelle le rôle A.
- **Bloqué depuis 30 minutes :** on écrit dans le salon `#entraide` ce qu'on a essayé.
- **Tester avant de pousser :** `streamlit run app.py` dans le terminal, puis vérifier sa page.

## 10. Les garde-fous

- **Pas de source, pas d'affichage.** Chaque information du site renvoie vers sa page PSI ou son rapport.
- **Une fiche sans initiales dans `verifie_par` n'est pas affichée.**
- **L'IA du site répond uniquement à partir des fiches** et a le droit de dire « je ne sais pas ».
- **Aucun chiffre inventé pour la Lune ou Mars.**
- **La clé d'API ne va jamais dans un fichier du dépôt.**
- **Les gros fichiers PSI ne vont pas dans le dépôt** : seuls les deux CSV de synthèse.
- **Une phrase sur le site :** outil d'aide à la compréhension, pas une certification de sécurité.
