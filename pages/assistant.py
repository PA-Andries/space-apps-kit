"""Page Assistant. Propriétaire : rôle E (Assistant). Les textes affichés sont en anglais.

L'historique vit dans `st.session_state["assistant_historique"]` : le bouton chatbot des autres pages
peut s'en servir aussi, pour que la conversation continue d'une page à l'autre.
"""

import streamlit as st

from flame.assistant import repondre
from flame.commun import charger_fiches, get_scenario
from flame.ui import label

st.title("Assistant")
habitat = get_scenario().get("habitat")
st.caption(
    f"Answers are based on the NASA investigation records and on your environment ({label(habitat)}), "
    "which you can change on the My environment page. They cite the investigations they use, "
    'and say "I don\'t know" when the records do not hold the answer.'
)

historique = st.session_state.setdefault("assistant_historique", [])
for message in historique:
    st.chat_message(message["role"]).write(message["content"])

question = st.chat_input("Ask a question about the experiments", key="assistant_question")
if question:
    st.chat_message("user").write(question)
    with st.spinner("Searching the investigation records…"):
        reponse = repondre(question, historique, charger_fiches())
    st.chat_message("assistant").write(reponse)
    historique.append({"role": "user", "content": question})
    historique.append({"role": "assistant", "content": reponse})
