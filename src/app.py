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


# ---------------------- SESSION SETUP ----------------------

def init_session():
    defaults = {
        "engine": None,
        "mode": None,
        "subject": None,
        "answered": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------- QUIZ FLOW ----------------------

def quiz_flow():

    # Step 1 → Select mode
    if not st.session_state.mode:
        render_mode_selection()
        return

    # Step 2 → Select subject
    if not st.session_state.subject:
        render_subject_selection()
        return

    # Step 3 → Create quiz engine if not created
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine = st.session_state.engine
    question = engine.get_current_question()

    # Step 4 → End of quiz
    if question is None:
        render_results(engine)
        return

    # Step 5 → Render question
    selected, _ = render_question(question, engine, st.session_state.mode)

    # Step 6 → Submit answer
    if not st.session_state.answered:
        if st.button("Submit Answer", key=f"submit_{engine.index}"):
            result = engine.check_answer(selected)
            st.session_state.answered = True

            if result["correct"]:
                st.success(f"🎉 Correct! +{result['points']} pts")
            else:
                st.error(f"❌ Wrong. Correct: {result['correct_answer']}")

            st.info(f"⏱ Time: {result['time']} sec")
            st.experimental_rerun()

    # Step 7 → Next Question button only after answering
    else:
        if st.button("Next ➜", key=f"next_{engine.index}"):
            engine.next_question()
            st.session_state.answered = False
            st.experimental_rerun()


# ---------------------- SIDEBAR NAVIGATION ----------------------

def sidebar_nav():
    if st.sidebar.button("🔁 Reset", key="reset"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

    return st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Dashboard", "Revision Mode"],
        key="nav"
    )


# ---------------------- REVISION MODE ----------------------

def revision_mode():
    st.title("🔁 Review Mistakes")

    if not st.session_state.engine or not st.session_state.engine.history:
        st.warning("Take a quiz first before reviewing mistakes.")
        return

    mistakes = [entry for entry in st.session_state.engine.history if not entry["correct"]]

    if not mistakes:
        st.success("🎉 No mistakes — awesome!")
        return

    for m in mistakes:
        st.write(f"❌ {m['question']} — Correct: **{m['correct_answer']}**")


# ---------------------- MAIN APP ----------------------

def main():
    st.set_page_config(page_title="SignSense", page_icon="🧠", layout="wide")

    init_session()
    render_header()
    page = sidebar_nav()

    if page == "Quiz":
        quiz_flow()

    elif page == "Dashboard":
        if st.session_state.engine:
            render_dashboard(st.session_state.engine)
        else:
            st.warning("⚠️ No quiz data yet — take a quiz first.")

    elif page == "Revision Mode":
        revision_mode()


if __name__ == "__main__":
    main()
