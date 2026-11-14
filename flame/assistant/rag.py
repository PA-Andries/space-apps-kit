"""L'étape « recherche » du RAG : retrouver les fiches dont le sens est le plus proche de la question.

Chaque fiche est transformée une seule fois en embedding (une liste de nombres qui représente son sens)
par l'API Gemini, puis gardée en cache. À chaque question, seule la question est transformée,
et on garde les fiches les plus proches. On n'envoie donc plus toutes les fiches au LLM.
"""

import pandas as pd
import requests
import streamlit as st

MODELE_EMBEDDING = "gemini-embedding-001"
URL_EMBEDDING = "https://generativelanguage.googleapis.com/v1beta/models/{modele}:batchEmbedContents"
DIMENSION = 768  # nombres par embedding : assez pour comparer, léger à garder en mémoire
NB_FICHES = 6  # fiches détaillées envoyées au LLM pour chaque question
TAILLE_LOT = 100  # Gemini accepte au plus 100 textes par appel
TAILLE_MAX_TEXTE = 8000  # caractères gardés par fiche pour son embedding
DELAI_MAX_S = 30
COLONNES_SENS = [
    "id",
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


def texte_pour_embedding(fiche: dict) -> str:
    """Le texte d'une fiche qui porte son sens (nom, objectif, résumé…), sans les cases vides."""
    morceaux = [
        f"{colonne}: {fiche[colonne]}" for colonne in COLONNES_SENS if colonne in fiche and pd.notna(fiche[colonne])
    ]
    return "\n".join(morceaux)[:TAILLE_MAX_TEXTE]


def calculer_embeddings(textes: list[str], cle: str, tache: str) -> list[list[float]]:
    """Un embedding par texte, par lots de 100. `tache` : RETRIEVAL_DOCUMENT ou RETRIEVAL_QUERY.

    Lève `requests.RequestException` si l'appel échoue.
    """
    vecteurs = []
    for debut in range(0, len(textes), TAILLE_LOT):
        demandes = [
            {
                "model": f"models/{MODELE_EMBEDDING}",
                "content": {"parts": [{"text": texte}]},
                "taskType": tache,
                "outputDimensionality": DIMENSION,
            }
            for texte in textes[debut : debut + TAILLE_LOT]
        ]
        reponse = requests.post(
            URL_EMBEDDING.format(modele=MODELE_EMBEDDING),
            headers={"x-goog-api-key": cle},
            json={"requests": demandes},
            timeout=DELAI_MAX_S,
        )
        reponse.raise_for_status()
        vecteurs += [embedding["values"] for embedding in reponse.json()["embeddings"]]
    return vecteurs


@st.cache_data(show_spinner=False)
def embeddings_des_fiches(textes: tuple[str, ...], _cle: str) -> list[list[float]]:
    """Les embeddings des fiches, calculés une seule fois tant que leurs textes ne changent pas.

    Le `_` devant `_cle` dit à Streamlit de ne pas se servir de la clé pour le cache.
    """
    return calculer_embeddings(list(textes), _cle, "RETRIEVAL_DOCUMENT")


def similarite(a: list[float], b: list[float]) -> float:
    """La similarité cosinus : proche de 1 quand les deux textes ont un sens proche."""
    produit = sum(x * y for x, y in zip(a, b, strict=True))
    normes = sum(x * x for x in a) ** 0.5 * sum(y * y for y in b) ** 0.5
    return produit / normes if normes else 0.0


def fiches_proches(question: str, fiches: pd.DataFrame, cle: str, nombre: int = NB_FICHES) -> pd.DataFrame:
    """Les `nombre` fiches dont le sens est le plus proche de `question`, la plus proche en premier.

    Lève `requests.RequestException` si Gemini ne répond pas.
    """
    if len(fiches) <= nombre:
        return fiches
    textes = tuple(texte_pour_embedding(fiche) for fiche in fiches.to_dict("records"))
    vecteurs_fiches = embeddings_des_fiches(textes, cle)
    vecteur_question = calculer_embeddings([question], cle, "RETRIEVAL_QUERY")[0]
    scores = [similarite(vecteur_question, vecteur) for vecteur in vecteurs_fiches]
    meilleures = sorted(range(len(scores)), key=lambda position: scores[position], reverse=True)[:nombre]
    return fiches.iloc[meilleures]
