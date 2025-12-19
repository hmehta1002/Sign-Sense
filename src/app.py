import streamlit as st
import time
import re

from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page


# ---------------------------------------------------------
# RESET APP
# ---------------------------------------------------------
def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()


# ---------------------------------------------------------
# USER PROFILE
# ---------------------------------------------------------
def render_user_profile():
    if "username" not in st.session_state:
        st.session_state.username = ""

    st.sidebar.subheader("User Profile")

    username = st.sidebar.text_input(
        "Enter your name",
        value=st.session_state.username,
        placeholder="Demo User"
    )

    if username:
        st.session_state.username = username
        st.sidebar.caption("Accessibility features enabled")


# ---------------------------------------------------------
# SESSION UTILITIES
# ---------------------------------------------------------
def init_session_utilities():
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

    if "history" not in st.session_state:
        st.session_state.history = []


# ---------------------------------------------------------
# ISL NUMBER VISUAL CUES (GUARANTEED RENDER)
# ---------------------------------------------------------
def render_isl_number_signs(question_text: str):
    numbers = re.findall(r"\b\d+\b", question_text)
    numbers = list(dict.fromkeys(numbers))[:2]

    if not numbers:
        return

    st.markdown("### ISL Number Focus")

    cols = st.columns(len(numbers))
    for col, num in zip(cols, numbers):
        with col:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 14px;
                    text-align: center;
                    background-color: #020617;
                ">
                    <div style="font-size: 28px; font-weight: 600;">{num}</div>
                    <div style="font-size: 12px; color: #94a3b8;">
                        Visual number cue for ISL learners
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------------
# ISL EXPLANATION PANEL (PROFESSIONAL)
# ---------------------------------------------------------
def render_isl_explanation(question_data):
    st.success("ISL Accessibility Mode Active")

    st.markdown("### ISL Visual Explanation Panel")
    st.caption(
        "Visual, non-audio guidance designed for Indian Sign Language learners."
    )

    if question_data and "question" in question_data:
        st.markdown(
            f"**Question Focus:** {question_data['question']}"
        )

    steps = [
        "Identify the numbers and mathematical terms.",
        "Understand what operation or comparison is required.",
        "Apply the relevant rule or simplification.",
        "Select the correct equivalent expression."
    ]

    for step in steps:
        st.write(f"- {step}")


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
def sidebar_navigation():
    pages = {
        "Solo Quiz": "solo",
        "Live Session": "live",
        "Revision Lab": "revision",
        "Dashboard": "dashboard",
        "Admin / AI Quiz Builder": "admin_ai",
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]


# ---------------------------------------------------------
# SOLO QUIZ PAGE
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("Solo Quiz")

    init_session_utilities()

    st.checkbox(
        "Demo Mode (stable for live demo)",
        key="demo_mode"
    )

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    # Start / Restart Quiz
    if st.button("Start / Restart Quiz"):
        with st.spinner("Initializing quiz engine..."):
            time.sleep(0.3)
            st.session_state["engine"] = QuizEngine(mode, subject)
        st.experimental_rerun()

    engine = st.session_state.get("engine")

    if not engine:
        st.info("Click Start / Restart Quiz to begin.")
        return

    engine.mode = mode
    engine.subject = subject

    q = engine.get_current_question()

    if q is None:
        st.success("Quiz complete.")
        if st.button("View Dashboard"):
            st.session_state["page"] = "dashboard"
            st.experimental_rerun()
        return

    selected = render_question_UI(q, mode)

    # ISL MODE SUPPORT
    if mode == "isl":
        render_isl_number_signs(q.get("question", ""))
        render_isl_explanation(q)

    st.caption(
        "Answers are evaluated using quiz logic and AI-assisted difficulty tuning."
    )

    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("Back"):
                engine.current_index -= 1
                st.experimental_rerun()

    with col2:
        if st.button("Next"):
            if selected:
                engine.check_answer(selected)
                st.session_state.history.append({
                    "question": q.get("question"),
                    "selected": selected
                })
            engine.next_question()
            st.experimental_rerun()


# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
def route_page(page_name: str):

    if page_name == "solo":
        solo_quiz_page()

    elif page_name == "dashboard":
        render_dashboard(st.session_state.get("engine"))

    elif page_name == "revision":
        render_revision_page(st.session_state.get("engine"))

    elif page_name == "live":
        engine = st.session_state.get("engine")
        if not engine:
            st.warning("Start a quiz first.")
            return
        from live.live_sync import live_session_page
        live_session_page(engine, {})

    elif page_name == "admin_ai":
        ai_quiz_builder()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    render_user_profile()

    if st.sidebar.button("Reset App"):
        reset_app()

    page = sidebar_navigation()
    st.session_state["page"] = page
    route_page(page)


if __name__ == "__main__":
    main()
