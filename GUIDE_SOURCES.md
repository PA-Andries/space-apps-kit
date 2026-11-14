# Guide des sources NASA

*Défi « Flame in Freefall », NASA Space Apps 2026. Mis à jour le 14 novembre 2026.*

**La recherche « combustion » de PSI renvoie 26 résultats : 19 investigations en vol, 5 études au sol et 2 hors sujet.** Chaque page contient des centaines, parfois des milliers de fichiers, mais trois petits fichiers par investigation nous suffisent.

## Sommaire

- [Quelle source sert quel objectif](#quelle-source-sert-quel-objectif)
- [PSI en détail : les 26 résultats](#psi-en-détail--les-26-résultats)
- [Anatomie d'une page PSI](#anatomie-dune-page-psi--quoi-lire-quoi-télécharger-quoi-ignorer)
- [Les neuf autres sources en détail](#les-neuf-autres-sources-en-détail)

## Quelle source sert quel objectif

PSI répond aux trois objectifs de l'énoncé. Les autres sources servent à comprendre PSI, à raconter l'enjeu et à remplir la page bonus.

| Objectif de l'énoncé | Sources qui y répondent | Ce que le site en fait |
| --- | --- | --- |
| Identifier les investigations utiles à chaque habitat (vaisseau, station, base lunaire ou martienne, rover) | PSI, section Description de chaque page ; NASA Combustion Science pour le résumé | Page Classement |
| Extraire des données pour la modélisation prédictive | PSI, section Experimental Table (fichiers CSV) ; les 5 études au sol, qui montrent comment ces données ont déjà servi à modéliser | Table des tests filtrable et exportable ; lien entre une expérience en vol et les modèles qui l'utilisent |
| Mettre en avant la recherche utile aux équipements de demain | PSI : SAME, SAME-R, DAFT, FLEX, BASS-II ; Researcher's Guide (extincteurs à brouillard d'eau, détecteurs) | Vue par pilier : prévenir, détecter, éteindre |
| Résumer et comparer les investigations | PSI, NASA Combustion Science, énoncé (familles de matériel) | Catalogue et Comparateur |
| Option : applications sur Terre | Les trois fiches Spinoff ; Researcher's Guide | Page « Retombées sur Terre » |
| Convaincre le jury de l'enjeu | Apollo 1, Apollo 13, Mir, vidéo ScienceCasts | Page d'accueil et vidéo de pitch |

## PSI en détail : les 26 résultats

Source : la [recherche « combustion » de PSI](https://psi.nasa.gov/physci/repo/search?q=combustion), relevée par l'équipe le 14 novembre 2026. Les colonnes Pilier et Priorité sont une proposition, à valider par l'Expert.

### Les 19 investigations en vol

| N° PSI | Investigation | Ce qui brûle, et où | Ce qu'elle cherche | Pilier | Priorité |
| --- | --- | --- | --- | --- | --- |
| PSI-26 | BASS | Tissu coton et fibre de verre, dans la boîte à gants MSG | Relier le test au sol NASA-STD-6001 à l'inflammabilité réelle en apesanteur | Prévenir | 1 |
| PSI-25 | BASS-II | Solides, soufflerie dans le MSG | Allumage et combustion ; alimente les modèles qui servent à concevoir détection et extinction | Prévenir, Éteindre | 1 |
| PSI-98 | Saffire-I | Grand échantillon de tissu Sibal, dans un cargo Cygnus | Vitesse de croissance d'un grand feu ; limites d'inflammabilité comparées au test au sol | Prévenir | 1 |
| PSI-99 | Saffire-II | Suite de Saffire-I, cargo Cygnus | Mêmes objectifs que Saffire-I | Prévenir | 1 |
| PSI-100 | Saffire-III | Suite de Saffire-I, cargo Cygnus | Mêmes objectifs que Saffire-I | Prévenir | 1 |
| PSI-102 | SAME | Fumées de matériaux, dans le MSG | Taille des particules de fumée en apesanteur | Détecter | 1 |
| PSI-101 | SAME-R | Comme SAME, avec un nouveau matériau (Pyrell, une mousse ignifuge) | Taille des particules de fumée | Détecter | 1 |
| PSI-47 | DAFT / DAFT-2 | Pas de flamme : essai du compteur de particules P-Trak | Vérifier l'instrument avant SAME | Détecter | 1 |
| PSI-69 | FLEX | Gouttes de carburant liquide, appareil MDCA dans le CIR | Limites d'inflammabilité, efficacité des gaz extincteurs, indice limite d'oxygène | Éteindre | 1 |
| PSI-20 | ACME BRE | Gaz imitant un matériau, dans le CIR | Conditions de combustion en air calme selon les propriétés du matériau | Prévenir | 1 |
| PSI-159 | ACME CFI-G | Propane, n-butane, n-pentane, dans le CIR | Flammes froides, normales et « inversées » ; d'après l'énoncé, les tests les plus riches en O₂ (jusqu'à 85 %) | Prévenir | 2 |
| PSI-68 | FLEX-2 | Gouttes de carburant, MDCA dans le CIR | Étend FLEX : pression de 0,5 à 3 atm, O₂ de 10 à 40 % | Éteindre | 2 |
| PSI-39 | CFI | Gouttes de n-dodécane, MDCA dans le CIR | Flammes froides, de 0,25 à 5 atm | Prévenir | 2 |
| PSI-22 | ACME E-FIELD Flames | Gaz, dans le CIR | Effet d'un champ électrique sur la flamme ; d'après l'énoncé, la seule imitation de la gravité partielle | Lune et Mars | 2 |
| PSI-107 | SPICE | Gaz, dont le méthane, dans le MSG | Point de fumée : à partir de quand une flamme produit de la suie | Détecter | 2 |
| PSI-106 | SLICE | Gaz, dont le méthane, dans le MSG | Structure et stabilité des flammes | Fondamental | 3 |
| PSI-10 | ACME Flame Design | Gaz, dans le CIR | Limites de formation de la suie | Fondamental | 3 |
| PSI-21 | ACME CLD Flame | Gaz, dans le CIR | Données pour tester les modèles numériques de flammes | Fondamental | 3 |
| PSI-23 | ACME s-Flame | Gaz, brûleur sphérique dans le CIR | Flammes sphériques comparées aux simulations | Fondamental | 3 |

**Comment lire les priorités :** 1 = citée par l'énoncé comme directement liée à la sécurité incendie, à mettre en fiche samedi matin. 2 = utile pour un point précis (oxygène élevé, pression, gravité partielle), samedi après-midi. 3 = recherche fondamentale, une fiche courte suffit.

### Les 5 études au sol

Ce sont des équipes de recherche qui ont réutilisé les données PSI pour construire des modèles. Elles illustrent parfaitement le deuxième objectif de l'énoncé.

| N° PSI | Étude | Données en vol réutilisées |
| --- | --- | --- |
| PSI-117 | Simulation 3D de flammes froides soumises à des perturbations | FLEX (PSI-69) |
| PSI-142 | Transitions des flammes froides près de l'extinction | FLEX (PSI-69) |
| PSI-62 | Modèle de propagation de flamme, comparé aux expériences BASS | BASS et BASS-II (PSI-26, PSI-25) |
| PSI-60 | Analyse des images de SPICE : la suie sur Terre et en apesanteur | SPICE (PSI-107) |
| PSI-115 | Simulation de la formation des fumées | SAME (PSI-102) |

Idée pour le site : sur la fiche de FLEX, BASS, SPICE et SAME, afficher « données déjà réutilisées par N études de modélisation ». C'est une preuve concrète de leur valeur.

### Les 2 résultats hors sujet

- **PSI-181** (soudures, science des matériaux) et **PSI-108** (STDCE-1, physique des fluides) ne ressortent que parce que le mot « combustion » apparaît dans leur texte. On les écarte.

### Ce que cette liste nous apprend

- **Les six expériences ACME sont présentes** : BRE, CFI-G, E-FIELD Flames, Flame Design, CLD Flame, s-Flame.
- **SoFIE, FLARE et FM2 sont absentes**, tout comme les données en gravité lunaire ou martienne. L'énoncé l'annonçait.
- **Seules Saffire-I, -II et -III figurent** dans la liste.
- **Dix investigations de priorité 1** suffisent à couvrir les trois piliers. C'est notre objectif réaliste pour samedi 13h.

## Anatomie d'une page PSI : quoi lire, quoi télécharger, quoi ignorer

**Une page PSI ressemble à une armoire : quelques documents de synthèse sur le dessus, et des milliers de fichiers bruts au fond.** Exemple relevé sur la page PSI-159 (ACME CFI-G) : 1,90 To et 3 756 fichiers. Nous n'ouvrons que le dessus de l'armoire.

| Section de la page | Ce qu'on y trouve (exemple PSI-159) | Ce qu'on en fait |
| --- | --- | --- |
| En-tête | Numéro PSI, titre, taille totale, DOI, domaine et sous-domaine (« Flames of Gaseous Fuels »), licence CC0-1.0 | Colonnes `id`, `nom`, `source_psi` ; le DOI sert à citer la source |
| Description | Type de projet, plateforme (ISS), agences, centre NASA, objectifs numérotés, contacts | Colonne `objectif` : on copie le texte, l'IA le résume |
| Experimental Table | Un ou plusieurs tableaux CSV : une ligne par test. Pour PSI-159, deux tableaux (flammes normales, flammes inversées) ; le second compte 1 016 tests, avec le carburant, la pression (`approx p (bar)`) et la fraction d'oxygène (`XO2`) | Le cœur de l'objectif « extraire des données » : colonnes `oxygene_min`, `oxygene_max`, `pression_kpa`, `combustible`, `ce_qui_varie` |
| Modeling Table | Tableau de résultats de simulation ; vide pour PSI-159 | À regarder surtout sur les 5 études au sol |
| Read Me | Notice d'utilisation des données ; vide pour PSI-159 | À lire quand elle existe : elle explique les colonnes |
| Hardware | Matériel utilisé (ACME, Combustion Integrated Rack) | Sert à regrouper les investigations par famille |
| Representative Images/Videos | Quelques images ou vidéos de flammes | Illustrations pour le site et la vidéo, avec crédit NASA |
| Data files and documents | Dossiers : Metadata, Reports, Engineering Documents, Experimental table, Raw Data, Representative Images | Voir « Quoi télécharger » ci-dessous |
| Publications | Articles scientifiques avec auteurs et DOI | Colonne `source_rapport` ; preuve que l'expérience a produit des résultats |
| Version History | Date de mise en ligne et liste de tous les fichiers | Deux chiffres pour le site : nombre de fichiers et taille |

### Quoi télécharger : trois petits fichiers par investigation

1. **Le ou les tableaux du dossier « Experimental table »** (fichiers `.csv`). C'est le résumé de tous les tests.
2. **Le rapport final du dossier « Reports »** (un PDF, par exemple `PSI-159_Reports_FinalRpt_ACME.CFI-G.pdf`). C'est lui qu'on donne à l'IA pour remplir la fiche.
3. **Le fichier du dossier « Investigation Metadata Files »** (un `.zip` de 8 Ko pour PSI-159). Il contient la description structurée de l'investigation.

### Quoi ignorer

- **Le dossier « Raw Data »** : réglages de caméras, images et mesures brutes. C'est lui qui pèse des centaines de gigaoctets.
- **Le dossier « Engineering Documents »** : la conception du matériel, inutile pour nos fiches.

### La routine, 10 minutes par investigation

1. Ouvrir la page PSI et copier le texte de la section Description dans le Google Sheet.
2. Télécharger les trois fichiers dans un dossier partagé nommé comme l'investigation (`PSI-69_FLEX/`).
3. Noter le DOI, la taille totale et le nombre de fichiers.
4. Passer à la suivante, dans l'ordre des priorités.

> Ne mettez pas les gros fichiers PSI dans le dépôt GitHub : seuls les petits CSV de synthèse y ont leur place, dans `data/`.

**L'argument à retenir pour le pitch :** notre site transforme 1,90 To et 3 756 fichiers en une fiche de dix lignes. C'est exactement le problème que pose l'énoncé : des données difficiles à trouver, à comparer et à interpréter.

## Les neuf autres sources en détail

### NASA Combustion Science : le résumé de chaque investigation

[Ouvrir la page](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/)

- **Contenu :** un paragraphe simple par investigation, en trois groupes.
- **En cours :** FM2 (première expérience de combustion sur un autre astre, à la gravité lunaire), SoFIE (allumage et extinction de solides dans l'ISS), FLARE (projet international pour estimer l'inflammabilité en apesanteur à partir de tests au sol).
- **Archivées :** ACME, BASS, DAFT, FLEX, Saffire, SAME, SLICE, SPICE.
- **Équipements :** le CIR, seul meuble de l'ISS dédié à la combustion, avec une chambre de 100 litres ; et le MDCA, l'appareil à gouttes.
- **Usage :** point de départ de la colonne `resume`. FM2, SoFIE et FLARE alimentent un encart « Ce qui arrive ensuite ».
- **Limites :** le paragraphe sur Saffire ne dit presque rien ; BASS-II, SAME-R, FLEX-2 et CFI n'ont pas de paragraphe à eux.

### Researcher's Guide : le manuel de fond

[Page de présentation](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) · [PDF](https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf?emrc=c9b273)

| Pages | Chapitre | Ce qu'on en tire |
| --- | --- | --- |
| 8 à 10 | Pourquoi étudier la combustion en apesanteur | Les explications simples pour la page d'accueil |
| 11 à 29 | Résultats par famille : gouttes (FLEX), flammes de gaz (SLICE, ACME), solides (BASS), sécurité incendie | Le contexte de chaque fiche |
| 30 à 35 | Points marquants et leçons apprises | Les « idées reçues », les flammes froides, la sécurité incendie : matière des 20 questions de référence |
| 36 à 42 | Pistes de recherche futures | L'objectif « équipements de demain » |
| 43 à 46 | Équipements : CIR, MSG | Le lexique du matériel |

- **Chiffres utiles :** le MDCA brûle des gouttes de 1 à 5 mm, de 0 à 3 atm, jusqu'à 40 % d'oxygène ; le MSG est une boîte à gants de 255 litres, en service depuis 2002.
- **Pour l'objectif « équipements » :** extincteurs à brouillard d'eau qui remplacent ceux au CO₂ ; détecteurs à adapter, car les particules de fumée n'ont pas la même taille en apesanteur.
- **Limite :** écrit en 2015. SoFIE y est annoncé pour 2019 et les expériences ACME y sont décrites avant leur vol.

### Vidéo ScienceCasts

[Voir la vidéo](https://www.youtube.com/watch?v=W1oXykoz9zg)

- **Contenu :** 3,6 minutes d'introduction à la recherche sur la combustion dans l'ISS, publiée en mars 2018. Déjà vue et résumée par l'équipe.
- **Usage :** mise en contexte, et inspiration pour le rythme et les images de notre propre vidéo.

### Apollo 1, Apollo 13 et Mir : les trois récits

| Source | Les faits | La leçon | Pilier illustré |
| --- | --- | --- | --- |
| [Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) | 27 janvier 1967, test au sol. Cabine en oxygène pur, arc électrique probable, feu très rapide. L'équipage meurt asphyxié ; la trappe en trois parties ne s'ouvre pas sous la pression | Matériaux inflammables strictement limités, combinaisons résistantes au feu, trappe unique ouvrable en trois secondes environ | Prévenir |
| [Apollo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) | Avril 1970. Un thermostat non mis à jour laisse chauffer un réservoir d'oxygène pendant un test ; l'isolation abîmée provoque l'explosion en vol | Réservoirs redessinés, troisième réservoir ajouté, câblage gainé d'acier | Prévenir |
| [Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) | 24 février 1997, six personnes à bord. Un générateur d'oxygène s'enflamme : flamme d'un mètre, métal en fusion, fumée dense, accès à un Soyouz coupé. Trois extincteurs utilisés ; la flamme s'éteint seule après plusieurs minutes | Entraînement des équipages revu ; l'ISS a des systèmes d'oxygène redondants | Détecter, Éteindre |

- **Usage :** la page d'accueil et l'ouverture de la vidéo. Mir est le récit le plus visuel.
- **Limite :** ce sont des récits, pas des données. Ils n'entrent pas dans le tableau des fiches.

### Les trois fiches Spinoff : les retombées sur Terre

| Source | Ce que NASA a apporté | Lien avec nos investigations |
| --- | --- | --- |
| [Fireman's Air Tanks](https://spinoff.nasa.gov/node/9582) (1976) | Bouteilles d'air de pompiers : environ 20 livres pour 30 minutes d'air, soit 13 livres de moins, et une pression doublée à 4 500 psi | Technologie des combinaisons spatiales |
| [Fire Detector](https://spinoff.nasa.gov/node/9407) (1978) | Un détecteur conçu pour la navette, qui distingue les particules de combustion de la poussière ; adapté aux mines | Même question que SAME et DAFT : reconnaître la fumée |
| [Fire Attire](https://spinoff.nasa.gov/node/9918) (1982) | Projet FIRES : une tenue de pompier repensée avec les matériaux légers et résistants au feu des combinaisons Apollo | Le pilier Prévenir : le choix des matériaux |

- **Usage :** la page bonus « Retombées sur Terre », avec les extincteurs à brouillard d'eau cités par l'énoncé. Trois courts paragraphes suffisent.
- **Limite :** ces fiches datent des années 1970 et 1980. On les présente comme des exemples historiques.
