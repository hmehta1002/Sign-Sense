import streamlit as st
from backend.logic import QuizEngine
from frontend.ui import (
    render_header,
    render_mode_selection,
    render_subject_selection,
    render_question,
    render_results,
)
from frontend.dashboard import render_dashboard


# ---------- STATE ----------

def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "answered": False,
        "feedback": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()


# ---------- QUIZ FLOW ----------

def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    q = engine.get_current_question()

    if q is None:
        render_results(engine)
        if st.button("🔁 Restart Quiz"):
            reset_app()
            st.experimental_rerun()
        return

    total = len(engine.questions)
    idx = engine.current_index + 1

    answer = render_question(q, st.session_state.mode, idx, total)

    if not st.session_state.answered:
        if st.button("Submit Answer"):
            fb = engine.check_answer(answer)
            st.session_state.feedback = fb
            st.session_state.answered = True
            st.experimental_rerun()
    else:
        fb = st.session_state.feedback
        if fb["correct"]:
            st.success(f"✔ Correct! +{fb['points']} points")
        else:
            st.error(f"❌ Incorrect — correct: **{fb['correct_answer']}**")

        if fb["time"] is not None:
            st.info(f"⏱ Time taken: {fb['time']} sec")

        if st.button("Next ➡"):
            engine.next_question()
            st.session_state.answered = False
            st.experimental_rerun()


# ---------- SIDEBAR ----------

def sidebar_nav():
    st.sidebar.title("📍 Navigation")
    if st.sidebar.button("🔁 Reset App"):
        reset_app()
        st.experimental_rerun()

    page = st.sidebar.radio(
        "Go to:",
        ["Quiz", "Dashboard"],
        index=0,
        key="page_nav"
    )
    return page


# ---------- MAIN ----------

def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    init_state()

    page = sidebar_nav()

    # Step 1: mode
    if st.session_state.mode is None:
        render_mode_selection()
        return

    # Step 2: subject
    if st.session_state.subject is None:
        render_subject_selection()
        return

    # Step 3: engine
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(
            st.session_state.mode,
            st.session_state.subject,
        )

    render_header(st.session_state.mode)

    if page == "Quiz":
        quiz_flow()
    else:
        render_dashboard(st.session_state.engine)


if __name__ == "__main__":
    main()
