"""Recherche par mots : quels mots de la question se retrouvent dans le texte d'une fiche."""

import re
import unicodedata

import pandas as pd

COLONNES_TEXTE = [
    "id",
    "psi",
    "nom",
    "pilier",
    "objectif",
    "type_combustible",
    "combustible",
    "materiel",
    "ce_qui_varie",
    "capteurs",
    "habitats",
    "resume",
]
# Petits mots d'une question qui ne disent rien du sujet cherché.
MOTS_VIDES = {
    "les",
    "des",
    "une",
    "aux",
    "est",
    "sur",
    "dans",
    "pour",
    "avec",
    "sans",
    "que",
    "qui",
    "quel",
    "quelle",
    "quels",
    "quelles",
    "comment",
    "the",
    "and",
    "for",
    "with",
    "what",
    "which",
    "how",
}
LONGUEUR_MIN_MOT = 3


def simplifier(texte: str) -> str:
    """Le texte en minuscules, sans accents ni ponctuation : « Éteindre, l'oxygène » -> « eteindre l oxygene »."""
    sans_accents = unicodedata.normalize("NFKD", str(texte)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", sans_accents.lower()).strip()


def mots_de_la_question(question: str) -> list[str]:
    """Les mots utiles de la question, simplifiés et sans doublon."""
    mots = [mot for mot in simplifier(question).split() if len(mot) >= LONGUEUR_MIN_MOT and mot not in MOTS_VIDES]
    return list(dict.fromkeys(mots))


def texte_des_fiches(fiches: pd.DataFrame) -> pd.Series:
    """Pour chaque fiche, tout son texte simplifié, entouré d'espaces pour repérer les débuts de mot."""
    colonnes = [colonne for colonne in COLONNES_TEXTE if colonne in fiches.columns]
    brut = fiches[colonnes].fillna("").astype(str).agg(" ".join, axis=1)
    return " " + brut.map(simplifier) + " "


def compter_mots_trouves(fiches: pd.DataFrame, mots: list[str]) -> pd.Series:
    """Pour chaque fiche, combien de mots de `mots` commencent un mot de son texte (« flam » trouve « flamme »)."""
    texte = texte_des_fiches(fiches)
    trouves = pd.Series(0, index=fiches.index)
    for mot in mots:
        trouves += texte.str.contains(" " + mot, regex=False).astype(int)
    return trouves
