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


# ---------------------- SESSION MANAGEMENT ----------------------

def init_session():
    if "engine" not in st.session_state:
        st.session_state.engine = None

    if "page" not in st.session_state:
        st.session_state.page = "Quiz"

    if "mode" not in st.session_state:
        st.session_state.mode = None

    if "subject" not in st.session_state:
        st.session_state.subject = None


# --------------------------- REVISION MODE ----------------------------

def render_revision_mode():
    st.subheader("🔁 Revision Mode")

    if not st.session_state.engine or not st.session_state.engine.history:
        st.warning("⚠ Complete at least one quiz first.")
        return

    wrong = [q for q in st.session_state.engine.history if not q["correct"]]

    if not wrong:
        st.success("🎉 No mistakes! Nothing to revise.")
        return

    st.write("Here are the questions you struggled with:")

    for item in wrong:
        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.08);
                border:1px solid #ff4f8b;
                padding:10px;
                margin:10px;
                border-radius:10px;
            ">
            ❌ <b>{item['question_id']}</b><br>
            Correct Answer: <b>{item['correct_answer']}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Start Adaptive Review Session"):
        st.info("Coming soon: Flashcards + step-by-step reteaching modules.")


# --------------------------- QUIZ FLOW ----------------------------

def quiz_flow():
    # Step 1: Learning mode
    if not st.session_state.mode:
        st.session_state.mode = render_mode_selection()
        return

    # Step 2: Subject choice
    if not st.session_state.subject:
        st.session_state.subject = render_subject_selection()
        return

    # Step 3: Create quiz engine if not exists
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(st.session_state.mode, st.session_state.subject)

    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # Step 4: If finished → show results
    if question is None:
        render_results(engine)
        return

    # Step 5: Render question UI
    selected, hint = render_question(question, engine, st.session_state.mode)

    # Submit button
    if st.button("Submit Answer"):
        feedback = engine.check_answer(selected)

        if feedback["correct"]:
            st.success(f"✔ Correct! You earned {feedback['points']} points.")
        else:
            st.error(f"❌ Incorrect. Correct answer: {feedback['correct_answer']}")

        st.info(f"⏱ Time Taken: {round(feedback['time_taken'], 2) if feedback['time_taken'] else 'N/A'} seconds")

        # Next question button
        if st.button("Next ➜"):
            engine.next_question()
            st.rerun()


# --------------------------- MAIN APP ----------------------------

def main():
    st.set_page_config(
        page_title="SignSense",
        page_icon="🧠",
        layout="wide"
    )

    init_session()
    render_header()

    # Reset session state for showing modes again
    st.sidebar.markdown("---")
    if st.sidebar.button("🔁 Reset Setup"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Sidebar Navigation
    page = st.sidebar.radio(
        "📍 Navigation",
        ["Quiz", "Performance Dashboard", "Revision Mode"]
    )
    st.session_state.page = page

    # Page Router
    if page == "Quiz":
        quiz_flow()

    elif page == "Performance Dashboard":
        if st.session_state.engine:
            render_dashboard(st.session_state.engine)
        else:
            st.warning("🚨 Take a quiz first before viewing analytics.")

    elif page == "Revision Mode":
        render_revision_mode()


# --------------------------- RUN APP ----------------------------

main()
