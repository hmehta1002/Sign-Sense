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


def init_session():
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "subject" not in st.session_state:
        st.session_state.subject = None
    if "answered" not in st.session_state:
        st.session_state.answered = False


def quiz_flow():
    # Step 1 → Mode select
    if not st.session_state.mode:
        st.session_state.mode = render_mode_selection()
        return

    # Step 2 → Subject select
    if not st.session_state.subject:
        st.session_state.subject = render_subject_selection()
        return

    # Step 3 → Create engine once
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        render_results(engine)
        return

    selected, _ = render_question(question, engine, st.session_state.mode)

    # SUBMIT Button
    if not st.session_state.answered:
        if st.button("Submit Answer", key=f"submit_{engine.index}"):
            feedback = engine.check_answer(selected)
            st.session_state.answered = True

            if feedback["correct"]:
                st.success(f"Correct! +{feedback['points']} points")
            else:
                st.error(f"Incorrect ❌ — Correct answer: {feedback['correct_answer']}")

            st.info(f"Time: {feedback['time']} sec")

            st.experimental_rerun()

    # NEXT Button only after answering
    if st.session_state.answered:
        if st.button("Next ➜", key=f"next_{engine.index}"):
            engine.next_question()
            st.session_state.answered = False
            st.experimental_rerun()


def sidebar_nav():
    if st.sidebar.button("🔁 Reset", key="reset_btn"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

    return st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Dashboard", "Revision Mode"],
        key="nav"
    )


def revision_mode():
    st.title("🔁 Review Mistakes")
    if not st.session_state.engine or not st.session_state.engine.history:
        st.warning("Complete a quiz first")
        return

    wrong = [x for x in st.session_state.engine.history if not x["correct"]]

    if not wrong:
        st.success("No mistakes — amazing! 🎉")
        return

    for q in wrong:
        st.write(f"❌ {q['question']} → Correct: **{q['correct_answer']}**")


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
            st.warning("Take a quiz first.")
    elif page == "Revision Mode":
        revision_mode()


if __name__ == "__main__":
    main()
