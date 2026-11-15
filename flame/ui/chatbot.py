"""Flamy on every page: the mascot in the bottom-right corner, and a small chat window that opens on a click.

The answers come from the assistant (role E, `flame.assistant.repondre`). `flame.ui` may not import
`flame.assistant` (rule 5 of CONTRIBUTING.md), so `app.py` hands the function in: `show_top_bar(repondre)`.
The conversation lives in `st.session_state["assistant_historique"]`, as on role E's page.
"""

import time
from collections.abc import Callable

import streamlit as st

from flame.commun import charger_fiches
from flame.ui.home import talking
from flame.ui.scene import mascot_scene

HISTORY = "assistant_historique"  # the same history as the Assistant page (role E)
AVATARS = {"assistant": ":material/local_fire_department:"}


def _word_by_word(text: str):
    """The answer word by word, so that it is written on screen while Flamy talks."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


@st.dialog(" ", width="small")  # the header below names Flamy
def _chat_window(answer: Callable) -> None:
    """The small chat window: Flamy, the conversation, and a box to ask a question."""
    # A compact header, as in a messaging app: a small Flamy and one line on where its answers come from.
    with st.container(key="ui_flamy_header", horizontal=True, vertical_alignment="center", gap="small"):
        with st.container(key="ui_flamy_face", width=64):
            mascot_scene(height=64, calm=True)
        st.html(
            '<div class="ff-chat-who"><b>Flamy</b><span>Answers from NASA\'s investigation records, '
            "with its sources</span></div>"
        )
    history = st.session_state.setdefault(HISTORY, [])
    conversation = st.container(height=380, key="ui_flamy_conversation", border=False)
    with conversation:
        if not history:
            st.chat_message("assistant", avatar=AVATARS["assistant"]).write(
                "Hi, I'm Flamy! Ask me about NASA's fire experiments in microgravity."
            )
        for message in history:
            st.chat_message(message["role"], avatar=AVATARS.get(message["role"])).write(message["content"])
    question = st.chat_input("Ask Flamy…", key="ui_flamy_question")
    if question:
        with conversation:
            st.chat_message("user").write(question)
            # Flamy talks while it searches and while the answer is written.
            with talking():
                with st.spinner("Flamy is searching the investigation records…"):
                    reply = answer(question, history, charger_fiches())
                st.chat_message("assistant", avatar=AVATARS["assistant"]).write_stream(_word_by_word(reply))
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reply})


def flamy_corner(answer: Callable | None) -> None:
    """Flamy in the bottom-right corner of the page; a click opens the chat window.

    `answer(question, history, fiches) -> str`: the assistant's function, handed in by `app.py`.
    """
    if answer is None:
        return
    with st.container(key="ui_flamy"):
        mascot_scene(height=96)
        if st.button("Flamy", icon=":material/forum:", key="ui_flamy_open"):
            _chat_window(answer)
