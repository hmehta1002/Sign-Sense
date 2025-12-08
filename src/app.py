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


# ------------------------- SESSION STATE -------------------------

def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "answered": False,
        "user_answer": None,
        "feedback": None,
        "page": "quiz"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()

# ------------------------- QUIZ LOGIC -------------------------

def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        render_results(engine)
        if st.button("🔁 Restart Quiz"):
            reset_all()
            st.experimental_rerun()
        return

    # NORMAL QUESTION DISPLAY
    answer = render_question(
        question,
        st.session_state.mode,
        engine.current_index + 1,
        len(engine.questions)
    )

    # SUBMIT ANSWER
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            st.session_state.user_answer = answer
            st.session_state.feedback = engine.check_answer(answer)
            st.session_state.answered = True
            st.experimental_rerun()

    # AFTER ANSWERING — SHOW FEEDBACK + CONTROLS
    if st.session_state.answered:
        fb = st.session_state.feedback

        if fb["correct"]:
            st.success(f"✔ Correct! +{fb['points']} points")
        else:
            st.error(f"❌ Incorrect — Correct: **{fb['correct_answer']}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous"):
                if engine.current_index > 0:
                    engine.current_index -= 1
                st.session_state.answered = False
                st.experimental_rerun()

        with col2:
            if st.button("Next ➡"):
                engine.next_question()
                st.session_state.answered = False
                st.experimental_rerun()
# ------------------------- NAVIGATION -------------------------

def sidebar():
    st.sidebar.title("📍 Menu")

    if st.sidebar.button("🔁 Reset App"):
        reset_all()
        st.experimental_rerun()

    return st.sidebar.radio(
        "Go to:",
        ["Quiz", "Performance Dashboard"]
    )

