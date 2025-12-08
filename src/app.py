import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header, render_mode_selection, render_subject_selection,
    render_question, render_results
)
from frontend.dashboard import render_dashboard


# ---------------- Session Setup ---------------- #

def initialize_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "page": "home",
        "answered": False,
        "user_answer": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quiz():
    st.session_state.mode = None
    st.session_state.subject = None
    st.session_state.engine = None
    st.session_state.page = "home"
    st.session_state.answered = False
    st.session_state.user_answer = None


# ---------------- App UI Logic ---------------- #

def quiz_page():
    engine = st.session_state.engine

    question = engine.get_current_question()
    total = len(engine.questions)
    index = engine.current_index + 1

    st.write(f"📘 **Question {index}/{total}**")

    if not st.session_state.answered:
        st.session_state.user
