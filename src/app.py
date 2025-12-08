import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header,
    render_mode_selection,
    render_subject_selection,
    render_question,
    render_results
)
from frontend.dashboard import render_dashboard


# ------------------------- SESSION CONTROL -------------------------

def init_state():
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "subject" not in st.session_state:
        st.session_state.subject = None
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "answered" not in st.session_state:
        st.session_state.answered = False
    if "user_answer" not in st.session_state:
        st.session_state.user_answer = None
    if "page" not in st.session_state:
        st.session_state.page = "quiz"


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


# ------------------------- QUIZ HANDLER -------------------------

def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    if question is None:
        render_results(engine)

        if st.button("🔄 Restart Quiz"):
            reset_all()
            st.experimental_rerun()
        return

    # Show question
    answer = render_question(
        question,
        st.session_state.mode,
        engine.current_index + 1,
        len(engine.questions)
    )

    # Submit button
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            st.session_state.user_answer = answer
            st.session_state.feedback = engine.check_answer(answer)
            st.session_state.answered = True
            st.experimental_rerun()

    # After answer: show feedback + next/back controls
    if st.session_state.answered:
        feedback = st.session_state.feedback
        if feedback["correct"]:
            st.success(f"✔ Correct! +{feedback['points']} points")
        else:
            st.error(f"❌ Incorrect — Correct answer: **{feedback['correct_answer']}**")

        col1, col2 = st.columns(2)

        with col
