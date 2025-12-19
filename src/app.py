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
# INLINE DEMO AVATAR (ALWAYS RENDERS)
# ---------------------------------------------------------
def render_isl_demo_avatar():
    st.markdown(
        """
        <svg width="110" height="140" viewBox="0 0 110 140"
             xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="5" width="100" height="130" rx="18"
                fill="#0f172a" stroke="#334155" stroke-width="2"/>
          <circle cx="55" cy="45" r="18" fill="#cbd5e1"/>
          <rect x="25" y="70" width="60" height="40" rx="18"
                fill="#94a3b8"/>
          <text x="55" y="128"
                font-size="10"
                fill="#cbd5e1"
                text-anchor="middle">
            ISL Demo Avatar
          </text>
        </svg>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# QUESTION-SPECIFIC REASONING FLOW (ISL + ADHD)
# ---------------------------------------------------------
def render_reasoning_graph(question_text: str):
    numbers = re.findall(r"\b\d+\b", question_text)
    ops = []

    if "÷" in question_text or "/" in question_text:
        ops.append("Division")
    if "×" in question_text or "*" in question_text:
        ops.append("Multiplication")
    if "+" in question_text:
        ops.append("Addition")
    if "-" in question_text:
        ops.append("Subtraction")

    rule = "Left-to-right evaluation"
    if ("+" in question_text or "-" in question_text) and \
       ("×" in question_text or "÷" in question_text):
        rule = "BODMAS / Operator precedence"

    st.markdown("### Reasoning Flow (Question-Specific)")

    cols = st.columns(4)

    with cols[0]:
        st.markdown(f"""
        <div style="border:1px solid #334155;border-radius:12px;
        padding:14px;text-align:center;background:#020617;">
        <b>Numbers</b><br>{', '.join(numbers)}
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div style="border:1px solid #334155;border-radius:12px;
        padding:14px;text-align:center;background:#020617;">
        <b>Operations</b><br>{' → '.join(ops)}
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div style="border:1px solid #334155;border-radius:12px;
        padding:14px;text-align:center;background:#020617;">
        <b>Rule Applied</b><br>{rule}
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f"""
        <div style="border:1px solid #334155;border-radius:12px;
        padding:14px;text-align:center;background:#020617;">
        <b>Outcome</b><br>Final Answer
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------
# ISL EXPLANATION PANEL
# ---------------------------------------------------------
def render_isl_explanation(question_data):
    st.success("ISL Accessibility Mode Active")

    st.markdown("### ISL Visual Explanation Panel")
    st.caption("Visual, non-audio guidance for Indian Sign Language learners.")

    col1, col2 = st.columns([2, 6])
    with col1:
        render_isl_demo_avatar()

    with col2:
        st.markdown(f"**Question Focus:** {question_data['question']}")
        steps = [
            "Identify the numbers and operators.",
            "Follow the correct operation order.",
            "Apply the mathematical rule.",
            "Select the correct answer."
        ]
        for s in steps:
            st.write(f"- {s}")


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

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    if st.button("Start / Restart Quiz"):
        st.session_state["engine"] = QuizEngine(mode, subject)
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start / Restart Quiz to begin.")
        return

    q = engine.get_current_question()
    if q is None:
        st.success("Quiz complete.")
        return

    selected = render_question_UI(q, mode)

    if mode in ["isl", "adhd"]:
        render_reasoning_graph(q["question"])

    if mode == "isl":
        render_isl_explanation(q)

    col1, col2 = st.columns(2)
    with col2:
        if st.button("Next"):
            if selected:
                engine.check_answer(selected)
            engine.next_question()
            st.experimental_rerun()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()
    render_user_profile()
    page = sidebar_navigation()
    if page == "solo":
        solo_quiz_page()


if __name__ == "__main__":
    main()
