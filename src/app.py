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


# ------------------------------------------------------------
# SESSION INITIALIZATION
# ------------------------------------------------------------
def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "answered": False,
        "user_answer": None,
        "feedback": None,
        "page": "Quiz"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


# ------------------------------------------------------------
# QUIZ FLOW
# ------------------------------------------------------------
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

    # Display UI for question
    answer = render_question(
        question,
        st.session_state.mode,
        engine.current_index + 1,
        len(engine.questions)
    )

    # Submit logic
    if not st.session_state.answered:
        if st.button("Submit"):
            st.session_state.feedback = engine.check_answer(answer)
            st.session_state.user_answer = answer
            st.session_state.answered = True
            st.experimental_rerun()

    # After submission feedback
    if st.session_state.answered:
        fb = st.session_state.feedback

        if fb["correct"]:
            st.success(f"✔ Correct! +{fb['points']} pts")
        else:
            st.error(f"❌ Incorrect — Correct answer: **{fb['correct_answer']}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous Question"):
                if engine.current_index > 0:
                    engine.current_index -= 1
                st.session_state.answered = False
                st.experimental_rerun()

        with col2:
            if st.button("Next ➡"):
                engine.next_question()
                st.session_state.answered = False
                st.experimental_rerun()


# ------------------------------------------------------------
# SIDEBAR NAV
# ------------------------------------------------------------
def sidebar_menu():
    st.sidebar.title("📍 Navigation")

    if st.sidebar.button("🔁 Reset App"):
        reset_app()
        st.experimental_rerun()

    return st.sidebar.radio(
        "Choose Page:",
        ["Quiz", "Performance Dashboard"]
    )


# ------------------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    init_state()

    # Sidebar navigation
    current_page = sidebar_menu()

    # Step 1 — Mode selection
    if st.session_state.mode is None:
        st.session_state.mode = render_mode_selection()
        return

    # Step 2 — Subject selection
    if st.session_state.subject is None:
        st.session_state.subject = render_subject_selection()
        return

    # Step 3 — Initialize quiz engine once
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(
            st.session_state.mode,
            st.session_state.subject
        )

    # Header
    render_header(st.session_state.mode)

    # Page control
    if current_page == "Quiz":
        quiz_flow()
    else:
        render_dashboard(st.session_state.engine)


# ------------------------------------------------------------
# REQUIRED ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
