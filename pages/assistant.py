"""Page Assistant. Propriétaire : rôle E (Assistant). Les textes affichés sont en anglais.

L'historique vit dans `st.session_state["assistant_historique"]` : le bouton chatbot des autres pages
peut s'en servir aussi, pour que la conversation continue d'une page à l'autre.
"""

import time

import streamlit as st

from flame.assistant import repondre
from flame.commun import charger_fiches, get_scenario
from flame.ui import assistant_mascot, label, talking

st.title("Assistant")
habitat = get_scenario().get("habitat")
st.caption(
    f"Answers are based on the NASA investigation records and on your environment ({label(habitat)}), "
    "which you can change on the My environment page. They cite the investigations they use, "
    'and say "I don\'t know" when the records do not hold the answer.'
)

historique = st.session_state.setdefault("assistant_historique", [])
# La conversation, puis la petite flamme (fixée en bas à droite, debout sur la zone de saisie).
conversation = st.container()
with conversation:
    for message in historique:
        st.chat_message(message["role"]).write(message["content"])
assistant_mascot()


def mot_a_mot(texte: str):
    """La réponse mot à mot, pour qu'elle s'écrive à l'écran pendant que la flamme parle."""
    for mot in texte.split(" "):
        yield mot + " "
        time.sleep(0.03)


question = st.chat_input("Ask a question about the experiments", key="assistant_question")
if question:
    with conversation:
        st.chat_message("user").write(question)
        # La flamme parle pendant la recherche et pendant que la réponse s'écrit.
        with talking():
            with st.spinner("Searching the investigation records…"):
                reponse = repondre(question, historique, charger_fiches())
            st.chat_message("assistant").write_stream(mot_a_mot(reponse))
    historique.append({"role": "user", "content": question})
    historique.append({"role": "assistant", "content": reponse})
