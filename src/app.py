import streamlit as st
from frontend.ui import (
    render_header,
    render_mode_selection,
    render_subject_selection,
    render_question,
    render_results,
)
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine


# ---------------------- SESSION INIT ----------------------

def init_state():
    defaults = {
        "mode": None,
        "subject": None,
        "engine": None,
        "answered": False,
        "adhd_profile": "balanced",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------- SIDEBAR NAV ----------------------

def sidebar_nav():
    if st.sidebar.button("🔁 Reset All", key="reset_all"):
        st.session_state.clear()
        st.rerun()

    page = st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Dashboard", "Revision"],
        index=0,
        key="nav",
    )
    return page


# ---------------------- QUIZ PAGE ----------------------

def quiz_page():
    # Step 1: mode
    if not st.session_state.mode:
        render_mode_selection()
        return

    # Step 2: subject
    if not st.session_state.subject:
        render_subject_selection()
        return

    # Step 3: engine
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # No more questions
    if question is None:
        render_results(engine)
        return

    selected, _ = render_question(question, engine)

    # Submit
    if not st.session_state.answered:
        if st.button("Submit Answer", key=f"submit_{engine.index}"):
            result = engine.check_answer(selected)
            st.session_state.answered = True

            # ADHD hybrid: update pacing profile
            if st.session_state.mode == "adhd":
                st.session_state.adhd_profile = engine.get_pacing_profile()

            if result["correct"]:
                st.success(f"✔ Correct! +{result['points']} points")
                # Kahoot-ish "wow" moment on streak
                if engine.streak >= 3:
                    st.balloons()
            else:
                st.error(f"❌ Wrong — Correct: {result['correct_answer']}")

            if result["time"] is not None:
                st.info(f"⏱ Time taken: {result['time']} seconds")

            st.rerun()

    # Next question
    else:
        if st.button("Next ➜", key=f"next_{engine.index}"):
            engine.next_question()
            st.session_state.answered = False

            # Clear stored answers for radio widgets
            for key in list(st.session_state.keys()):
                if key.startswith("answer_"):
                    del st.session_state[key]

            st.rerun()


# ---------------------- REVISION PAGE ----------------------

def revision_page():
    st.title("🔁 Review Mistakes")

    engine: QuizEngine | None = st.session_state.engine
    if not engine or not engine.history:
        st.warning("Take a quiz first to see mistakes.")
        return

    mistakes = [row for row in engine.history if not row["correct"]]

    if not mistakes:
        st.success("🎉 No mistakes — excellent work!")
        return

    for m in mistakes:
        st.write(f"❌ {m['question']} → Correct: **{m['correct_answer']}**")


# ---------------------- MAIN ----------------------

def main():
    st.set_page_config(page_title="SignSense", page_icon="🧠", layout="wide")
    init_state()
    render_header()

    page = sidebar_nav()

    if page == "Quiz":
        quiz_page()
    elif page == "Dashboard":
        if st.session_state.engine:
            render_dashboard(st.session_state.engine)
        else:
            st.warning("No quiz data yet. Take a quiz first.")
    elif page == "Revision":
        revision_page()


if __name__ == "__main__":
    main()
