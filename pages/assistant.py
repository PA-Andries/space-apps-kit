"""Page Assistant. Propriétaire : rôle E (Assistant)."""

import streamlit as st

from flame.assistant import repondre
from flame.commun import charger_fiches

st.title("Assistant")

historique = st.session_state.setdefault("assistant_historique", [])
for message in historique:
    st.chat_message(message["role"]).write(message["content"])

question = st.chat_input("Posez une question sur les expériences", key="assistant_question")
if question:
    st.chat_message("user").write(question)
    reponse = repondre(question, historique, charger_fiches())
    st.chat_message("assistant").write(reponse)
    historique.append({"role": "user", "content": question})
    historique.append({"role": "assistant", "content": reponse})
