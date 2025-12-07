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

def quiz_flow():
    # Step 1: mode selection
    if not st.session_state.mode:
        st.session_state.mode = render_mode_selection()
        return

    # Step 2: subject selection
    if not st.session_state.subject:
        st.session_state.subject = render_subject_selection()
        return

    # Step 3: initialize quiz engine
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # end of quiz
    if not question:
        render_results(engine)
        return

    selected, hint = render_question(question, engine, st.session_state.mode)

    if st.button("Submit Answer", key=f"submit_{engine.index}"):
        feedback = engine.check_answer(selected)

        if feedback["correct"]:
            st.success(f"✔ Correct! +{feedback['points']} points")
        else:
            st.error(f"❌ Wrong! Correct answer: {feedback['correct_answer']}")

        st.info(f"⏱ Time: {round(feedback['time_taken'],2)} sec")

        if st.button("Next ➜", key=f"next_{engine.index}"):
            engine.next_question()
            st.rerun()

def get_sidebar():
    if st.sidebar.button("🔁 Reset Setup", key="reset_button"):
        for key in ["engine", "mode", "subject"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    return st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Performance Dashboard", "Revision Mode"],
        key="nav_radio"
    )

def revision_mode():
    st.title("🔁 Review mistakes")
    if not st.session_state.engine or not st.session_state.engine.history:
        st.warning("Complete a quiz first")
        return

    mistakes = [q for q in st.session_state.engine.history if not q["correct"]]

    if not mistakes:
        st.success("🎉 No mistakes to revise!")
        return

    for m in mistakes:
        st.write(f"❌ **{m['question_id']}** → correct: **{m['correct_answer']}**")

def main():
    st.set_page_config(page_title="SignSense", page_icon="🧠", layout="wide")
    init_session()
    
    render_header()
    page = get_sidebar()

    if page == "Quiz":
        quiz_flow()

    elif page == "Performance Dashboard":
        if st.session_state.engine:
            render_dashboard(st.session_state.engine)
        else:
            st.warning("🚨 Take a quiz first")

    elif page == "Revision Mode":
        revision_mode()

if __name__ == "__main__":
    main()
