"""Tests de l'assistant. Propriétaire : rôle E. Aucun test n'appelle le vrai Gemini ni le vrai Claude."""

from types import SimpleNamespace

import anthropic
import httpx2
import pandas as pd
import pytest
import requests

from flame.assistant import chatbot, claude, environnement, outils, rag
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
    # Ni clé de Claude par défaut : les tests de Gemini ne dépendent pas des clés de l'ordinateur.
    monkeypatch.setattr(chatbot, "cle_claude", lambda: None)
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)


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


def test_le_catalogue_et_les_fiches_ne_parlent_plus_de_pilier():
    assert "Détecter" not in chatbot.catalogue(FICHES_TEST)
    assert "pilier" not in chatbot.fiches_en_texte(FICHES_TEST)
    assert "pilier" not in rag.COLONNES_SENS


def test_les_fiches_d_un_equipement_gardent_l_ordre_annonce():
    from flame.assistant import EQUIPEMENTS, fiches_pour

    fiches = pd.DataFrame({"id": ["PSI-25", "PSI-10", "PSI-69", "PSI-68"], "nom": ["a", "b", "c", "d"]})
    assert list(fiches_pour("extincteurs", fiches)["id"]) == EQUIPEMENTS["extincteurs"]
    assert fiches_pour("detecteurs", fiches).empty


def test_les_retombees_citent_nasa_et_sautent_les_cases_vides():
    from flame.assistant import instruments_de, liens_terre, retombees_sur_terre

    psi = pd.DataFrame(
        {
            "investigation_id": ["PSI-1", "PSI-2"],
            "acronym": ["UN", "DEUX"],
            "impacts_earth_benefits": ["Texte de NASA.", None],
            "psi_url": ["https://psi.nasa.gov/1", "https://psi.nasa.gov/2"],
        }
    )
    retombees = retombees_sur_terre(psi)
    assert retombees.to_dict("records") == [
        {"id": "PSI-1", "nom": "UN", "texte": "Texte de NASA.", "source": "https://psi.nasa.gov/1"}
    ]
    # Sans les tables PSI (données d'exemple), rien ne plante et rien n'est inventé.
    assert retombees_sur_terre(pd.DataFrame()).empty
    assert instruments_de("PSI-1", pd.DataFrame()).empty
    assert liens_terre(pd.DataFrame()).empty


def test_la_page_equipements_s_ouvre():
    from pathlib import Path

    from streamlit.testing.v1 import AppTest

    page = AppTest.from_file(str(Path(__file__).parent.parent / "pages" / "equipements.py")).run()
    assert not page.exception
    assert [onglet.label for onglet in page.tabs] == ["Detectors", "Extinguishers", "On Earth"]


def test_synthetiser_n_envoie_que_les_fiches_choisies(monkeypatch):
    envois = []

    def faux_post(url, headers, json, timeout):
        envois.append(json)
        return FausseReponse({"candidates": [{"content": {"parts": [{"text": "#### Fire behaviour\nTexte (A)."}]}}]})

    monkeypatch.setattr(chatbot, "cle_api", lambda: "fausse-cle")
    monkeypatch.setattr(chatbot.requests, "post", faux_post)
    assert chatbot.synthetiser(FICHES_TEST, ["A", "C"]).startswith("#### Fire behaviour")
    consigne = envois[0]["system_instruction"]["parts"][0]["text"]
    assert "Fumée des câbles" in consigne and "Tissu en feu" in consigne
    assert "Gouttes de carburant" not in consigne
    assert "tools" not in envois[0]  # la synthèse n'a pas besoin des outils


def test_synthetiser_refuse_une_seule_fiche_et_dit_quand_la_cle_manque(monkeypatch):
    assert chatbot.synthetiser(FICHES_TEST, ["A"]) == chatbot.SYNTHESE_IMPOSSIBLE
    monkeypatch.setattr(chatbot, "cle_api", lambda: None)
    assert chatbot.synthetiser(FICHES_TEST, ["A", "B"]) == chatbot.SANS_CLE


def test_compter_tests_compte_comme_les_pages(monkeypatch):
    """Un test sans pression notée est compté, et le résultat dit combien ont une pression notée."""
    tests = pd.DataFrame(
        {
            "investigation_id": ["A", "A", "B", "B"],
            "oxygene_pct": [35.0, 35.0, 35.0, None],
            "pression_kpa": [50.0, None, 101.0, 50.0],
        }
    )
    monkeypatch.setattr(outils, "charger_tests", lambda: tests)
    monkeypatch.setattr(outils, "charger_fiches", lambda: FICHES_TEST.assign(type_combustible="gaz"))
    lune = outils.compter_tests(oxygene_min_pct=30, pression_max_kpa=70.3)
    assert lune["nb_tests"] == 2
    assert lune["nb_tests_avec_pression_notee"] == 1
    assert lune["investigations"] == [{"id": "A", "nb_tests": 2}]
    assert "nb_tests_avec_pression_notee" not in outils.compter_tests(oxygene_min_pct=30)


# --- Claude ---


def texte_claude(texte: str):
    """Imite une réponse de Claude qui ne contient que du texte."""
    return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=texte)])


def faux_claude(monkeypatch, reponses: list, cle_gemini: str | None = None) -> list[dict]:
    """Branche un faux Claude qui rend `reponses` dans l'ordre (une exception est levée) ; renvoie ses demandes."""
    demandes = []

    def create(**options):
        demandes.append({**options, "messages": list(options["messages"])})
        reponse = reponses[min(len(demandes) - 1, len(reponses)) - 1]  # demandes[0] est le client
        if isinstance(reponse, Exception):
            raise reponse
        return reponse

    def faux_client(api_key, timeout, max_retries):
        demandes.append({"cle": api_key})
        messages = SimpleNamespace(create=create)
        return SimpleNamespace(messages=messages, beta=SimpleNamespace(messages=messages))

    monkeypatch.setattr(claude.anthropic, "Anthropic", faux_client)
    monkeypatch.setattr(chatbot, "cle_claude", lambda: "cle-claude")
    monkeypatch.setattr(chatbot, "cle_api", lambda: cle_gemini)
    return demandes


def erreur_claude(classe, code: int, message: str = "erreur"):
    """Une erreur de l'API d'Anthropic, comme la bibliothèque la lève."""
    requete = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return classe(message, response=httpx2.Response(code, request=requete), body=None)


def test_avec_une_cle_claude_c_est_claude_qui_repond(monkeypatch):
    demandes = faux_claude(monkeypatch, [texte_claude("Réponse (EXEMPLE-A).")])
    historique = [{"role": "user", "content": "Bonjour"}, {"role": "assistant", "content": "Bonjour !"}]
    assert chatbot.repondre("Qu'est-ce que BASS ?", historique, charger_fiches()) == "Réponse (EXEMPLE-A)."
    client, demande = demandes
    assert client == {"cle": "cle-claude"}
    assert demande["model"] == claude.MODELE
    assert "EXEMPLE-A" in demande["system"]  # les fiches partent dans la consigne
    assert [message["role"] for message in demande["messages"]] == ["user", "assistant", "user"]
    assert [outil["name"] for outil in demande["tools"]] == list(outils.OUTILS)
    assert all(outil["input_schema"]["type"] == "object" for outil in demande["tools"])
    assert "fallbacks" not in demande  # l'option de repli ne sert qu'aux modèles qui l'acceptent


def test_claude_appelle_un_outil_puis_repond(monkeypatch):
    appel = SimpleNamespace(type="tool_use", id="outil_1", name="compter_tests", input={"oxygene_min_pct": 30})
    demande_d_outil = SimpleNamespace(stop_reason="tool_use", content=[appel])
    demandes = faux_claude(monkeypatch, [demande_d_outil, texte_claude("Deux tests (EXEMPLE-C, EXEMPLE-D).")])
    reponse = chatbot.repondre("Combien de tests à 30 % d'oxygène ou plus ?", [], charger_fiches())
    assert reponse == "Deux tests (EXEMPLE-C, EXEMPLE-D)."
    # Le second envoi contient la demande de Claude, puis le résultat de l'outil.
    assert demandes[2]["messages"][-2] == {"role": "assistant", "content": [appel]}
    resultat = demandes[2]["messages"][-1]["content"][0]
    assert resultat["type"] == "tool_result" and resultat["tool_use_id"] == "outil_1"
    assert '"nb_tests": 2' in resultat["content"]


def test_claude_ne_tourne_pas_en_rond(monkeypatch):
    appel = SimpleNamespace(type="tool_use", id="outil_1", name="compter_tests", input={})
    demandes = faux_claude(monkeypatch, [SimpleNamespace(stop_reason="tool_use", content=[appel])])
    assert chatbot.repondre("Compte encore", [], charger_fiches()) == chatbot.SANS_REPONSE
    assert len(demandes) - 1 == claude.NB_MAX_TOURS_OUTILS + 1


def test_un_refus_de_claude_donne_un_message_clair(monkeypatch):
    faux_claude(monkeypatch, [SimpleNamespace(stop_reason="refusal", content=[])])
    assert chatbot.repondre("Question", [], charger_fiches()) == claude.REFUS


def test_une_mauvaise_cle_claude_donne_un_message_clair(monkeypatch):
    faux_claude(monkeypatch, [erreur_claude(anthropic.AuthenticationError, 401)])
    assert "ANTHROPIC_API_KEY" in chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())


def test_un_compte_sans_credit_donne_un_message_clair(monkeypatch):
    sans_credit = erreur_claude(anthropic.BadRequestError, 400, "Your credit balance is too low to access the API.")
    faux_claude(monkeypatch, [sans_credit])
    assert "no API credit" in chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())


def test_si_claude_echoue_gemini_prend_le_relais(monkeypatch):
    faux_claude(monkeypatch, [erreur_claude(anthropic.InternalServerError, 529)], cle_gemini="fausse-cle")
    monkeypatch.setattr(chatbot, "fiches_proches", lambda texte, fiches, cle: fiches.head(1))
    monkeypatch.setattr(chatbot.requests, "post", lambda *args, **kwargs: FausseReponse())
    assert chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches()) == "Réponse (EXEMPLE-A)."


def test_si_l_option_de_repli_est_refusee_claude_repond_sans_elle(monkeypatch):
    refus_de_l_option = erreur_claude(anthropic.BadRequestError, 400, "fallbacks: unknown parameter")
    monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-5-5")
    demandes = faux_claude(monkeypatch, [refus_de_l_option, texte_claude("Réponse.")])
    assert chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches()) == "Réponse."
    assert "fallbacks" in demandes[1] and "fallbacks" not in demandes[2]


def test_un_autre_modele_se_choisit_dans_les_secrets(monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "claude-sonnet-5-5")
    demandes = faux_claude(monkeypatch, [texte_claude("Réponse.")])
    chatbot.repondre("Qu'est-ce que BASS ?", [], charger_fiches())
    assert demandes[1]["model"] == "claude-sonnet-5-5"
    assert demandes[1]["fallbacks"] == "default"


def test_sans_cle_gemini_la_recherche_se_fait_par_mots():
    choisies = chatbot.choisir_fiches("tissu", [], FICHES_TEST, None)
    assert list(choisies["id"]) == ["C"]


def test_la_cle_du_modele_a_copier_ne_compte_pas(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", claude.SECRET_A_REMPLIR)
    monkeypatch.setattr(claude.st, "secrets", {})
    assert claude.cle_claude() is None
    monkeypatch.setenv("ANTHROPIC_API_KEY", " sk-ant-exemple ")
    assert claude.cle_claude() == "sk-ant-exemple"


def test_synthetiser_passe_par_claude_sans_outils(monkeypatch):
    demandes = faux_claude(monkeypatch, [texte_claude("#### Fire behaviour\nTexte (A).")])
    assert chatbot.synthetiser(FICHES_TEST, ["A", "C"]).startswith("#### Fire behaviour")
    assert "Fumée des câbles" in demandes[1]["system"] and "tools" not in demandes[1]
