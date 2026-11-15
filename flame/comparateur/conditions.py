"""Les conditions testées face à l'environnement de l'utilisateur : les tests qui correspondent, et leur graphique.

Aucun test n'a à la fois l'oxygène, la pression et le débit d'air : le graphique a donc deux vues
qui partagent l'axe de l'oxygène. Les textes renvoyés pour l'affichage sont en anglais.
"""

import pandas as pd
import plotly.graph_objects as go

from flame.comparateur.comparaison import famille_combustible

SANS_BORNE = (None, None)

# Repli tant que le scénario étendu (lot A du recadrage) n'est pas dans `main` : les plages de chaque
# habitat, avec les valeurs de `conditions_habitat`. Un habitat absent d'ici n'a aucune plage connue.
PLAGES_PAR_HABITAT = {
    "Vaisseau": {"oxygene_pct": (19, 23), "pression_kpa": (90, 110)},
    "Station": {"oxygene_pct": (19, 23), "pression_kpa": (90, 110)},
    "Base lunaire": {"oxygene_pct": (30, None), "pression_kpa": (None, 70.3)},
    "Rover pressurisé": {"oxygene_pct": (30, None), "pression_kpa": (None, 70.3)},
}

# Les zones dessinées sur le graphique, avec l'origine de leurs chiffres. Mars n'en a pas : l'énoncé ne donne rien.
ZONES = [
    {
        "nom": "Earth and ISS",
        "source": "to be sourced",
        "oxygene_pct": (19, 23),
        "pression_kpa": (90, 110),
        "couleur": "37, 99, 235",
    },
    {
        "nom": "Moon base and rover",
        "source": "statement",
        "oxygene_pct": (30, None),
        "pression_kpa": (None, 70.3),
        "couleur": "224, 102, 42",
    },
]
COMBINAISON = {"nom": "Spacesuit", "source": "statement", "oxygene_pct": 100, "pression_kpa": 29.6}

VUES = {
    "pression": ("pression_kpa", "Pressure (kPa, log scale)"),
    "debit": ("debit_air_cm_s", "Air flow (cm/s)"),
}
AXE_OXYGENE = (8, 104)
AXE_PRESSION = (20, 700)
# Une couleur par investigation, la même dans les deux vues.
COULEURS = [
    "#e0662a",
    "#2563eb",
    "#15803d",
    "#9333ea",
    "#db2777",
    "#0891b2",
    "#ca8a04",
    "#475569",
    "#b91c1c",
    "#4d7c0f",
    "#7c2d12",
    "#1e3a8a",
]
OPACITE_ESTOMPEE = 0.25

# Le graphique de répartition : une vue d'ensemble, pas un outil d'analyse. Trois couleurs seulement,
# selon la règle 60-30-10 du site : les surfaces restent neutres, l'encre de structure porte la masse
# des tests, et l'orange de la flamme est réservé à ce qui correspond à l'environnement de l'utilisateur.
PAS_REPARTITION = 5  # largeur d'une tranche d'oxygène, en points de pourcentage
BORNES_REPARTITION = list(range(0, 105, PAS_REPARTITION))
COULEUR_STRUCTURE = "#7d86a8"  # 30 % : tous les tests (le gris-bleu du site, lisible sur la page de nuit)
COULEUR_ACCENT = "#e8622a"  # 10 % : les tests de l'environnement (le même orange que primaryColor)
COULEUR_ENCRE = "#e9ecf8"  # le trait de la frontière et ses mots (le textColor du thème sombre)


def plages_du_scenario(scenario: dict) -> dict:
    """Les plages de conditions de l'environnement : oxygène, pression, débit d'air (min, max) et combustibles.

    Une clé absente du scénario prend la plage de son habitat ; `None` veut dire « pas de borne ».
    """
    repli = PLAGES_PAR_HABITAT.get(scenario.get("habitat"), {})
    return {
        "oxygene_pct": tuple(scenario.get("oxygene_pct") or repli.get("oxygene_pct", SANS_BORNE)),
        "pression_kpa": tuple(scenario.get("pression_kpa") or repli.get("pression_kpa", SANS_BORNE)),
        "debit_air_cm_s": tuple(scenario.get("debit_air_cm_s") or SANS_BORNE),
        "type_combustible": list(scenario.get("type_combustible") or []),
    }


def environnement_defini(scenario: dict) -> bool:
    """Vrai si l'environnement donne au moins une condition : sinon, aucun test ne peut lui « correspondre »."""
    plages = plages_du_scenario(scenario)
    bornes = [borne for cle in ("oxygene_pct", "pression_kpa", "debit_air_cm_s") for borne in plages[cle]]
    return any(borne is not None for borne in bornes) or bool(plages["type_combustible"])


def decrire_plage(plage: tuple, unite: str) -> str:
    """Une plage en mots : « at least 30 % », « at most 70.3 kPa », « 19 to 23 % », ou une chaîne vide."""
    mini, maxi = plage
    if mini is None and maxi is None:
        return ""
    if maxi is None:
        return f"at least {mini:g} {unite}"
    if mini is None:
        return f"at most {maxi:g} {unite}"
    return f"{mini:g} to {maxi:g} {unite}"


def decrire_environnement(scenario: dict) -> str:
    """Les conditions de l'environnement en une phrase courte, ou une chaîne vide s'il n'en donne aucune."""
    plages = plages_du_scenario(scenario)
    libelles = (
        ("oxygene_pct", "oxygen", "%"),
        ("pression_kpa", "pressure", "kPa"),
        ("debit_air_cm_s", "air flow", "cm/s"),
    )
    morceaux = [f"{nom} {decrire_plage(plages[cle], unite)}" for cle, nom, unite in libelles]
    return ", ".join(morceau for morceau in morceaux if not morceau.endswith(" "))


def _dans(valeurs: pd.Series, plage: tuple) -> pd.Series:
    """Vrai pour chaque valeur dans la plage. Sans borne, tout passe ; sinon une valeur absente ne passe pas."""
    mini, maxi = plage
    if mini is None and maxi is None:
        return pd.Series(True, index=valeurs.index)
    dedans = valeurs.notna()
    if mini is not None:
        dedans &= valeurs >= mini
    if maxi is not None:
        dedans &= valeurs <= maxi
    return dedans


def tests_correspondants(tests: pd.DataFrame, fiches: pd.DataFrame, scenario: dict) -> pd.DataFrame:
    """Les tests dans les plages d'oxygène, de pression, de débit d'air et de combustible de l'environnement.

    L'oxygène et le débit doivent être notés dès que l'environnement leur donne une borne. La pression
    n'est vérifiée que lorsqu'elle est notée : la colonne `pression_notee` dit si elle l'est, pour qu'on
    puisse compter à part les tests dont on ne sait pas s'ils respectent la pression.
    """
    plages = plages_du_scenario(scenario)
    garde = _dans(tests["oxygene_pct"], plages["oxygene_pct"]) & _dans(
        tests["debit_air_cm_s"], plages["debit_air_cm_s"]
    )
    garde &= tests["pression_kpa"].isna() | _dans(tests["pression_kpa"], plages["pression_kpa"])
    if plages["type_combustible"]:
        familles = dict(zip(fiches["id"], fiches["type_combustible"].map(famille_combustible), strict=True))
        garde &= tests["investigation_id"].map(familles).isin(plages["type_combustible"])
    return tests[garde].assign(pression_notee=tests.loc[garde, "pression_kpa"].notna())


def _rectangle(x: tuple, y: tuple) -> tuple[list, list]:
    return [x[0], x[1], x[1], x[0], x[0]], [y[0], y[0], y[1], y[1], y[0]]


def _bornes(plage: tuple, axe: tuple) -> tuple:
    """Une plage dont les bornes absentes sont remplacées par les bords de l'axe."""
    return (axe[0] if plage[0] is None else plage[0], axe[1] if plage[1] is None else plage[1])


def graphique_conditions(tests: pd.DataFrame, fiches: pd.DataFrame, scenario: dict, vue: str = "pression") -> go.Figure:
    """Le graphique des conditions testées : chaque point est un test, de la couleur de son investigation.

    Les tests qui correspondent à l'environnement sont pleins et cerclés, les autres estompés.

    `vue="pression"` : oxygène × pression, la pression en échelle logarithmique.
    `vue="debit"` : oxygène × débit d'air (les solides, dont la pression n'est pas notée).
    Les zones dessinées sont celles de `ZONES` et la combinaison spatiale ; Mars n'en a pas.
    """
    colonne, titre_y = VUES[vue]
    visibles = tests.dropna(subset=["oxygene_pct", colonne])
    noms = dict(zip(fiches["id"], fiches["nom"], strict=True))
    correspondants = tests_correspondants(tests, fiches, scenario).index if environnement_defini(scenario) else []
    surlignes = visibles[visibles.index.isin(correspondants)]
    autres = visibles[~visibles.index.isin(correspondants)]
    axe_y = AXE_PRESSION if vue == "pression" else (visibles[colonne].min() - 5, visibles[colonne].max() + 5)

    figure = go.Figure()
    for zone in ZONES:
        # Dans la vue du débit d'air, une zone n'a que sa plage d'oxygène : c'est une bande verticale.
        y = _bornes(zone["pression_kpa"], AXE_PRESSION) if vue == "pression" else axe_y
        xs, ys = _rectangle(_bornes(zone["oxygene_pct"], AXE_OXYGENE), y)
        precision = "" if vue == "pression" else ", oxygen only"
        figure.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                fill="toself",
                fillcolor=f"rgba({zone['couleur']}, 0.13)",
                line={"color": f"rgba({zone['couleur']}, 0.55)", "width": 1},
                # La légende ne porte que le nom : la provenance est dans l'infobulle, au survol.
                name=zone["nom"],
                hoverinfo="text",
                hovertext=f"{zone['nom']} — {zone['source']}{precision}",
            )
        )
    if vue == "pression":
        figure.add_trace(
            go.Scatter(
                x=[COMBINAISON["oxygene_pct"]],
                y=[COMBINAISON["pression_kpa"]],
                mode="markers",
                marker={"symbol": "star", "size": 14, "color": "#7c3aed"},
                name=COMBINAISON["nom"],
                hovertemplate=(f"Spacesuit: 100 % oxygen, 29.6 kPa — {COMBINAISON['source']}<extra></extra>"),
            )
        )
    # Les tests de chaque investigation sont regroupés : une couleur et une ligne de légende par investigation.
    # Ceux qui correspondent à l'environnement sont pleins et cerclés, les autres estompés.
    avec_oxygene = sorted(tests.dropna(subset=["oxygene_pct"])["investigation_id"].unique())
    couleurs = {identifiant: COULEURS[rang % len(COULEURS)] for rang, identifiant in enumerate(avec_oxygene)}
    estompe = OPACITE_ESTOMPEE if len(surlignes) else 0.7
    for identifiant, groupe in autres.groupby("investigation_id", sort=True):
        nom = noms.get(identifiant, identifiant)
        dans_la_legende = identifiant not in set(surlignes["investigation_id"])
        figure.add_trace(
            _points(groupe, colonne, noms, nom, couleurs[identifiant], estompe, identifiant, dans_la_legende)
        )
    for identifiant, groupe in surlignes.groupby("investigation_id", sort=True):
        # Pas de « (matches) » dans la légende : ces tests se reconnaissent à leur cercle (voir `_points`).
        nom = noms.get(identifiant, identifiant)
        figure.add_trace(
            _points(groupe, colonne, noms, nom, couleurs[identifiant], 0.95, identifiant, True, cercle=True)
        )

    figure.update_xaxes(title_text="Oxygen (%)", range=list(AXE_OXYGENE))
    if vue == "pression":
        figure.update_yaxes(title_text=titre_y, type="log", tickvals=[20, 30, 50, 70, 100, 200, 300, 500])
    else:
        figure.update_yaxes(title_text=titre_y, range=list(axe_y))
    figure.update_layout(legend_title_text="", margin={"t": 30, "b": 40, "l": 50, "r": 10}, height=480)
    return figure


def _points(
    lignes: pd.DataFrame,
    colonne: str,
    noms: dict,
    nom: str,
    couleur: str,
    opacite: float,
    groupe: str,
    dans_la_legende: bool,
    cercle: bool = False,
) -> go.Scatter:
    """Les points d'une investigation ; `groupe` relie dans la légende ses tests pleins et ses tests estompés."""
    details = pd.DataFrame(
        {
            "investigation": lignes["investigation_id"].map(lambda identifiant: noms.get(identifiant, identifiant)),
            "test": lignes["test_id"].astype(str),
            "combustible": lignes["combustible"].fillna("not recorded").astype(str),
        }
    )
    marqueur = {"color": couleur, "size": 9 if cercle else 7, "opacity": opacite}
    if cercle:
        marqueur["line"] = {"color": "#1f2937", "width": 1}
    return go.Scatter(
        x=lignes["oxygene_pct"],
        y=lignes[colonne],
        mode="markers",
        marker=marqueur,
        name=nom,
        legendgroup=groupe,
        showlegend=dans_la_legende,
        customdata=details.to_numpy(),
        hovertemplate="%{customdata[0]} · test %{customdata[1]}<br>%{customdata[2]}<br>"
        "oxygen %{x} %, %{y}<extra></extra>",
    )


def _tranches(valeurs: pd.Series, centres: list[float]) -> pd.Series:
    """Chaque valeur d'oxygène rangée dans sa tranche, repérée par le centre de la tranche."""
    return pd.cut(valeurs, bins=BORNES_REPARTITION, right=False, labels=centres, ordered=False)


def graphique_repartition(
    tests: pd.DataFrame, fiches: pd.DataFrame, scenario: dict, frontiere: float | None = None
) -> go.Figure:
    """La répartition des tests NASA sur l'axe de l'oxygène : une lecture en une seconde.

    Les barres grises comptent tous les tests dont l'oxygène est noté ; la part orange est celle qui
    tombe dans l'environnement de l'utilisateur. `frontiere` trace, si elle est donnée, l'oxygène le plus
    haut auquel un vrai échantillon solide a été testé : au-delà, plus aucune mesure de matériau.
    Aucune légende : tout est écrit sur le graphique.
    """
    centres = [borne + PAS_REPARTITION / 2 for borne in BORNES_REPARTITION[:-1]]
    oxygene = pd.to_numeric(tests["oxygene_pct"], errors="coerce")
    visibles = tests[oxygene.notna()]
    correspondants = tests_correspondants(tests, fiches, scenario).index if environnement_defini(scenario) else []
    dans_l_environnement = visibles.index.isin(correspondants)
    rangees = _tranches(oxygene[oxygene.notna()], centres)
    compte_accent = rangees[dans_l_environnement].value_counts().reindex(centres, fill_value=0)
    compte_autres = rangees[~dans_l_environnement].value_counts().reindex(centres, fill_value=0)

    figure = go.Figure()
    for compte, couleur, suffixe in (
        (compte_autres, COULEUR_STRUCTURE, "outside your environment"),
        (compte_accent, COULEUR_ACCENT, "in your environment"),
    ):
        figure.add_trace(
            go.Bar(
                x=centres,
                y=compte.to_numpy(),
                marker={"color": couleur, "line": {"width": 0}},
                width=PAS_REPARTITION * 0.86,
                hovertemplate=("oxygen %{customdata} %%<br>%{y} test(s) " + suffixe + "<extra></extra>"),
                customdata=[f"{borne:g}–{borne + PAS_REPARTITION:g}" for borne in BORNES_REPARTITION[:-1]],
                showlegend=False,
            )
        )

    plages = plages_du_scenario(scenario)
    if environnement_defini(scenario) and any(borne is not None for borne in plages["oxygene_pct"]):
        debut, fin = _bornes(plages["oxygene_pct"], (BORNES_REPARTITION[0], BORNES_REPARTITION[-1]))
        figure.add_vrect(
            x0=debut,
            x1=fin,
            fillcolor=COULEUR_ACCENT,
            opacity=0.08,
            line={"color": COULEUR_ACCENT, "width": 1},
            layer="below",
            # À droite : la frontière des solides écrit son étiquette à gauche, elles ne se chevauchent pas.
            annotation={"text": "your environment", "font": {"size": 11, "color": COULEUR_ACCENT}},
            annotation_position="top right",
        )
    if frontiere is not None:
        figure.add_vline(
            x=frontiere,
            line={"color": COULEUR_ENCRE, "width": 1.5, "dash": "dot"},
            annotation={"text": f"no solid tested above {frontiere:g} %", "font": {"size": 11, "color": COULEUR_ENCRE}},
            annotation_position="top right",
        )

    figure.update_xaxes(title_text="Oxygen (%)", range=[0, BORNES_REPARTITION[-1]], dtick=10)
    figure.update_yaxes(title_text="NASA tests", rangemode="tozero", gridcolor="rgba(160,175,255,0.12)")
    figure.update_layout(
        barmode="stack",
        bargap=0,
        height=260,
        margin={"t": 30, "b": 40, "l": 55, "r": 10},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return figure
