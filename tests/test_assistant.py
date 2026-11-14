"""Tests de l'assistant. Propriétaire : rôle E. Aucun test n'appelle le vrai Gemini."""

import pandas as pd
import pytest
import requests

from flame.assistant import chatbot, environnement, outils, rag
from flame.commun import charger_fiches, charger_tests

SCENARIO_LUNE = {
    "habitat": "Base lunaire",
    "oxygene_pct": (30.0, None),
    "pression_kpa": (None, 70.3),
    "gravite": 0.165,
    "type_combustible": [],
    "debit_air_cm_s": (None, None),
    "pilier": None,
    "profil": "Ingénieur",
}


@pytest.fixture(autouse=True)
def sans_scenario(monkeypatch):
    """Par défaut, aucun environnement choisi : les tests ne dépendent pas de la mémoire de Streamlit."""
    monkeypatch.setattr(chatbot, "scenario_courant", lambda: {})


class FausseReponse:
    """Imite une réponse HTTP de Gemini : `contenu` est le JSON renvoyé."""

    def __init__(self, contenu: dict | None = None, code: int = 200):
        self.status_code = code
        self.contenu = contenu or {"candidates": [{"content": {"parts": [{"text": "Réponse (EXEMPLE-A)."}]}}]}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return self.contenu


def faux_embeddings(appels: list[str]):
    """Un faux service d'embeddings : un texte qui parle de fumée vaut [1, 0], les autres [0, 1]."""

    def post(url, headers, json, timeout):
        appels.append(json["requests"][0]["taskType"])
        textes = [demande["content"]["parts"][0]["text"].lower() for demande in json["requests"]]
        vecteurs = [[1.0, 0.0] if "fum" in texte else [0.0, 1.0] for texte in textes]
        return FausseReponse({"embeddings": [{"values": vecteur} for vecteur in vecteurs]})

    return post


FICHES_TEST = pd.DataFrame(
    {
        "id": ["A", "B", "C"],
        "nom": ["Fumée des câbles", "Gouttes de carburant", "Tissu en feu"],
        "pilier": ["Détecter", "Éteindre", "Prévenir"],
        "resume": ["Mesure de la fumée.", "Extinction de gouttes.", "Propagation sur un tissu."],
    }
)


def test_sans_cle_l_assistant_le_dit(monkeypatch):
    monkeypatch.setattr(chatbot, "cle_api", lambda: None)
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert "LLM_API_KEY" in reponse


def test_la_consigne_existe():
    assert "je ne sais pas" in chatbot.lire_prompt("systeme")


def test_les_fiches_en_texte_gardent_les_id():
    fiches = charger_fiches()
    texte = chatbot.fiches_en_texte(fiches)
    assert all(f"id: {identifiant}" in texte for identifiant in fiches["id"])
    assert "nan" not in texte


def test_l_historique_est_traduit_pour_gemini():
    historique = [{"role": "user", "content": "Bonjour"}, {"role": "assistant", "content": "Salut"}]
    messages = chatbot.messages_gemini("Et BASS ?", historique)
    assert [message["role"] for message in messages] == ["user", "model", "user"]
    assert messages[-1]["parts"][0]["text"] == "Et BASS ?"


def test_la_similarite_cosinus():
    assert rag.similarite([1.0, 0.0], [2.0, 0.0]) == 1.0
    assert rag.similarite([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_la_recherche_garde_les_fiches_les_plus_proches(monkeypatch):
    monkeypatch.setattr(rag.requests, "post", faux_embeddings([]))
    proches = rag.fiches_proches("Qui a étudié la fumée ?", FICHES_TEST, "fausse-cle", nombre=1)
    assert list(proches["id"]) == ["A"]


def test_les_fiches_ne_sont_transformees_qu_une_fois(monkeypatch):
    appels = []
    monkeypatch.setattr(rag.requests, "post", faux_embeddings(appels))
    rag.fiches_proches("la fumée ?", FICHES_TEST, "fausse-cle", nombre=1)
    rag.fiches_proches("les gouttes ?", FICHES_TEST, "fausse-cle", nombre=1)
    assert appels.count("RETRIEVAL_DOCUMENT") == 1  # les fiches : une seule fois, puis le cache
    assert appels.count("RETRIEVAL_QUERY") == 2  # une question : un petit appel à chaque fois


def test_si_les_embeddings_echouent_on_cherche_par_mots(monkeypatch):
    def en_panne(*args, **kwargs):
        raise requests.ConnectionError

    monkeypatch.setattr(chatbot, "fiches_proches", en_panne)
    choisies = chatbot.choisir_fiches("tissu", [], FICHES_TEST, "fausse-cle")
    assert list(choisies["id"]) == ["C"]


def test_la_question_precedente_aide_la_recherche():
    historique = [{"role": "user", "content": "Parle-moi de la fumée"}, {"role": "assistant", "content": "…"}]
    assert chatbot.texte_a_chercher("et ensuite ?", historique) == "Parle-moi de la fumée\net ensuite ?"
    assert chatbot.texte_a_chercher("bonjour", []) == "bonjour"


def test_la_consigne_n_envoie_que_les_fiches_utiles():
    consigne = chatbot.consigne_systeme(FICHES_TEST.head(1), FICHES_TEST)
    assert all(f"- {identifiant} :" in consigne for identifiant in FICHES_TEST["id"])  # la liste courte
    assert "Mesure de la fumée." in consigne  # le détail de la fiche utile
    assert "Extinction de gouttes." not in consigne  # pas le détail des autres


def test_repondre_envoie_les_fiches_a_gemini(monkeypatch):
    envoye = {}

    def faux_post(url, headers, json, timeout):
        envoye.update(url=url, headers=headers, json=json)
        return FausseReponse()

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert reponse == "Réponse (EXEMPLE-A)."
    assert envoye["headers"]["x-goog-api-key"] == "fausse-cle"
    assert "fausse-cle" not in envoye["url"]
    assert "EXEMPLE-A" in envoye["json"]["system_instruction"]["parts"][0]["text"]


def test_gemini_surcharge_donne_un_message_clair(monkeypatch):
    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", lambda *args, **kwargs: FausseReponse(code=503))
    reponse = chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert "overloaded" in reponse


def test_gemini_trop_lent_donne_un_message_clair(monkeypatch):
    def trop_lent(*args, **kwargs):
        raise requests.Timeout

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", trop_lent)
    assert "too long" in chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())


# --- L'environnement de l'utilisateur ---


def test_l_environnement_est_decrit_avec_ses_bornes():
    texte = environnement.decrire_environnement(SCENARIO_LUNE)
    assert "Habitat : Base lunaire" in texte
    assert "Oxygène : au moins 30 %" in texte
    assert "Pression : au plus 70.3 kPa" in texte
    assert "Gravité : 0.165 g" in texte
    assert "Combustibles : tous" in texte
    assert "Pilier" not in texte  # les piliers sont abandonnés (décision du 14 nov. 17h00)


def test_un_environnement_sans_chiffre_reste_inconnu():
    mars = {"habitat": "Base martienne", "oxygene_pct": (None, None), "pression_kpa": (None, None), "gravite": None}
    texte = environnement.decrire_environnement(mars)
    assert "Oxygène : inconnu" in texte
    assert "Pression : inconnu" in texte
    assert "Gravité : inconnue" in texte
    assert environnement.decrire_environnement({}) == ""


def test_une_plage_s_ecrit_simplement():
    assert environnement.plage((19, 23), "%") == "de 19 à 23 %"
    assert environnement.plage((None, None), "%") is None
    assert environnement.plage(21, "%") == "21 %"  # l'ancien scénario donnait un seul nombre
    assert environnement.gravite_en_texte(0.0) == "microgravité (0 g)"


def test_repondre_donne_l_environnement_a_gemini(monkeypatch):
    envoye = {}

    def faux_post(url, headers, json, timeout):
        envoye.update(json=json)
        return FausseReponse()

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot, "scenario_courant", lambda: SCENARIO_LUNE)
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    chatbot.repondre("Quelles expériences me servent ?", [], charger_fiches())
    consigne = envoye["json"]["system_instruction"]["parts"][0]["text"]
    assert "Habitat : Base lunaire" in consigne
    assert "au moins 30 %" in consigne


# --- Les outils que Gemini peut appeler ---


def test_compter_tests_respecte_les_plages():
    assert outils.compter_tests()["nb_tests"] == len(charger_tests())
    riches = outils.compter_tests(oxygene_min_pct=30)
    assert riches["nb_tests"] == 2
    lune = outils.compter_tests(oxygene_min_pct=30, pression_max_kpa=70.3)
    assert lune["nb_tests"] == 1
    assert lune["investigations"] == [{"id": "EXEMPLE-C", "nb_tests": 1}]


def test_compter_tests_filtre_les_combustibles():
    solides = outils.compter_tests(types_combustible=["solide"])
    assert solides["nb_tests"] == 3
    assert [investigation["id"] for investigation in solides["investigations"]] == ["EXEMPLE-A"]


def test_filtrer_par_habitat_classe_par_score(monkeypatch):
    table = pd.DataFrame(
        {
            "habitat_id": ["moon_base", "moon_base", "moon_base", "space_station"],
            "investigation_id": ["PSI-1", "PSI-2", "PSI-2", "PSI-3"],
            "acronym": ["UN", "DEUX", "DEUX", "TROIS"],
            "score": [40, 90, 10, 100],  # PSI-2 a deux lignes, comme dans l'ancienne table par pilier
            "why": ["peu de tests", "tests à 30 % d'O2", "autre pilier", "station"],
        }
    )
    monkeypatch.setattr(outils, "charger_table_psi", lambda nom: table)
    resultat = outils.filtrer_par_habitat("Base lunaire")
    assert [investigation["id"] for investigation in resultat["investigations"]] == ["PSI-2", "PSI-1"]
    assert resultat["investigations"][0]["score_sur_100"] == 90
    assert "jugement" in outils.DECLARATIONS[0]["description"]


def test_filtrer_par_habitat_refuse_un_habitat_inconnu():
    assert "erreur" in outils.filtrer_par_habitat("Vénus")
    assert outils.filtrer_par_habitat("Base lunaire")["investigations"] == []  # pas de table dans les exemples


def test_un_outil_en_erreur_ne_fait_pas_planter_l_assistant():
    assert "erreur" in outils.executer_outil("outil_inexistant", {})
    assert "erreur" in outils.executer_outil("compter_tests", {"argument_inconnu": 1})


def test_gemini_appelle_un_outil_puis_repond(monkeypatch):
    demandes = []
    appel = {"functionCall": {"name": "compter_tests", "args": {"oxygene_min_pct": 30}}}
    reponses = [
        FausseReponse({"candidates": [{"content": {"role": "model", "parts": [appel]}}]}),
        FausseReponse({"candidates": [{"content": {"parts": [{"text": "Deux tests (EXEMPLE-C, EXEMPLE-D)."}]}}]}),
    ]

    def faux_post(url, headers, json, timeout):
        demandes.append(json)
        return reponses[len(demandes) - 1]

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    reponse = chatbot.repondre("Combien de tests à 30 % d'oxygène ou plus ?", [], charger_fiches())
    assert reponse == "Deux tests (EXEMPLE-C, EXEMPLE-D)."
    assert demandes[0]["tools"][0]["functionDeclarations"] == outils.DECLARATIONS
    # Le second envoi contient la demande de Gemini, puis le résultat de l'outil.
    assert demandes[1]["contents"][-2] == {"role": "model", "parts": [appel]}
    resultat = demandes[1]["contents"][-1]["parts"][0]["functionResponse"]
    assert resultat["name"] == "compter_tests"
    assert resultat["response"]["nb_tests"] == 2


def test_gemini_ne_tourne_pas_en_rond(monkeypatch):
    demandes = []
    appel = {"functionCall": {"name": "compter_tests", "args": {}}}

    def faux_post(url, headers, json, timeout):
        demandes.append(json)
        return FausseReponse({"candidates": [{"content": {"parts": [appel]}}]})

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    assert chatbot.repondre("Compte encore", [], charger_fiches()) == chatbot.SANS_REPONSE
    assert len(demandes) == chatbot.NB_MAX_TOURS_OUTILS + 1
