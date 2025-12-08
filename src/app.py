import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header, render_mode_selection, render_subject_selection,
    render_question, render_results
)
from frontend.dashboard import render_dashboard


# ----------- INITIALIZATION -----------

def init_state():
    if "mode" not in st.session_state: st.session_state.mode = None
    if "subject" not in st.session_state: st.session_state.subject = None
    if "engine" not in st.session_state: st.session_state.engine = None
    if "page" not in st.session_state: st.session_state.page = "home"
    if "answered" not in st.session_state: st.session_state.answered = False
    if "user_answer" not in st.session_state: st.session_state.user_answer = None


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


# ----------- QUIZ SECTION -----------

def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    q = engine.get_current_question()

    if q is None:
        render_results(engine)
        if st.button("🔄 Restart Quiz"):
            reset_app()
            st.experimental_rerun()
        return

    # Render question
    user_answer = render_question(
        q, st.session_state.mode, engine.current_index + 1, len(engine.questions)
    )

    # Show Submit button only if not answered
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            st.session_state.user_answer = user_answer
            st.session_state.feedback = engine.check_answer(user_answer)
            st.session_state.answered = True
            st.experimental_rerun()

    # After answer
