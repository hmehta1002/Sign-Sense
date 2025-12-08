import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header, render_mode_selection, render_subject_selection,
    render_question, render_results
)
from frontend.dashboard import render_dashboard


# ---------- SESSION INITIALIZATION ----------

def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "page": "home",
        "answered": False,
        "user_answer": None,
        "feedback": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
# ---------- QUIZ LOGIC ----------

def quiz_flow():
    engine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        render_results(engine)

        if st.button("🔁 Restart Quiz"):
            reset_app()
            st.experimental_rerun()
        return

    # Display question
    user_answer = render_question(
        question,
        st.session_state.mode,
        engine.current_index + 1,
        len(engine.questions)
    )

    # Submit
    if not st.session_state.answered:
        if st.button("Submit"):
           
