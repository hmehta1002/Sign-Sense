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

def init_state():
    if "mode" not in st.session_state:
        st.session_state.mode = None
    if "subject" not in st.session_state:
        st.session_state.subject = None
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "answered" not in st.session_state:
        st.session_state.answered = False


# ---------------------- SIDEBAR ----------------------

def sidebar_nav():
    if st.sidebar.button("🔁 Reset All"):
        st.session_state.clear()
        st.rerun()

    return st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Dashboard", "Revision"],
        index=0
    )


# ---------------------- QUIZ FLOW ----------------------

def quiz_page():

    # Step 1: Choose learning mode
    if not st.session_state.mode:
        render_mode_selection()
        return

    # Step 2: Choose subject
    if not st.session_state.subject:
        render_subject_selection()
        return

    # Step 3: Create engine once
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine = st.session_state.engine
    question = engine.get_current_question()

    # Step 4: end of quiz
    if question is None:
        render_results(engine)
        return

    # Step 5: show question
    selected, _ = render_question(question, engine)

    # Step 6: submit answer
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            result = engine.check_answer(selected)
            st.session_state.answered = True

            if result["correct"]:
                st.success(f"✔ Correct! +{result['points']} points")
            else:
                st.error(f"❌ Wrong — Correct: {result['correct_answer']}")

            st.info(f"⏱ Time taken: {result['time']} seconds")
            st.rerun()

    # Step 7: next
    else:
        if st.button("Next ➜"):
            engine.next_question()
            st.session_state.answered = False

            # Clear stored radio button value
            for key in list(st.session_state.keys()):
                if key.startswith("answer_"):
                    del st.session_state[key]

            st.rerun()


# ---------------------- REVISION ----------------------

def revision_page():
    st.title("🔁 Review Mistakes")

    if not st.session_state.engine or not st.session_state.engine.history:
        st.warning("Take a quiz first.")
        return

    wrong = [q for q in st.session_state.engine.history if not q["correct"]]

    if not wrong:
        st.success("🎉 No mistakes — you're amazing!")
        return

    for q in wrong:
        st.write(f"❌ {q['question']} → Correct: **{q['correct_answer']}**")


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
            st.warning("📌 Take a quiz first to unlock analytics.")
    elif page == "Revision":
        revision_page()


if __name__ == "__main__":
    main()
