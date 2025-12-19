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
# USER PROFILE & AVATAR
# ---------------------------------------------------------
def render_user_profile():
    if "username" not in st.session_state:
        st.session_state.username = ""

    st.sidebar.subheader("👤 User Profile")

    username = st.sidebar.text_input(
        "Enter your name",
        value=st.session_state.username,
        placeholder="Demo User"
    )

    if username:
        st.session_state.username = username
        avatar_url = (
            f"https://api.dicebear.com/7.x/adventurer-neutral/svg?seed={username}"
        )
        st.sidebar.image(avatar_url, width=110)
        st.sidebar.caption("User Avatar")


# ---------------------------------------------------------
# SESSION UTILITIES
# ---------------------------------------------------------
def init_session_utilities():
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

    if "history" not in st.session_state:
        st.session_state.history = []


# ---------------------------------------------------------
# ISL NUMBER SIGNS (REAL, SAFE)
# ---------------------------------------------------------
def render_isl_number_signs(question_text: str):
    numbers = re.findall(r"\b\d+\b", question_text)
    numbers = list(dict.fromkeys(numbers))[:2]  # max 2 numbers

    if not numbers:
        return

    st.markdown("### 🔢 ISL Number Signs")

    cols = st.columns(len(numbers))
    for col, num in zip(cols, numbers):
        with col:
            st.image(
                f"https://isl-dataset.netlify.app/numbers/{num}.png",
                width=90
            )
            st.caption(f"ISL sign for {num}")


# ---------------------------------------------------------
# ISL EXPLANATION (IMPROVED, NOT WEIRD)
# ---------------------------------------------------------
def render_isl_explanation(question_data):
    st.success("🤟 ISL Accessibility Mode Active")

    isl_avatar_url = (
        "https://api.dicebear.com/7.x/adventurer-neutral/svg?seed=isl_guide"
    )

    st.markdown("### 📖 Visual Explanation (ISL-Assisted)")
    st.caption(
        "Visual sequencing designed for Indian Sign Language learners."
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        st.image(isl_avatar_url, width=100)
        st.caption("ISL Guide")

    with col2:
        if question_data and "question" in question_data:
            st.markdown(
                f"🧠 **Question focus:** {question_data['question']}"
            )

        steps = [
            "Look at the **numbers and key words**.",
            "Understand **what is being asked**.",
            "Apply the **correct rule or concept**.",
            "Choose the **best answer**."
        ]

        for step in steps:
            st.write("👉 " + step)
            time.sleep(0.25)


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
def sidebar_navigation():
    pages = {
        "📘 Solo Quiz": "solo",
        "🌐 Live Session": "live",
        "🔁 Revision Lab": "revision",
        "📊 Dashboard": "dashboard",
        "🤖 Admin / AI Quiz Builder": "admin_ai",
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]


# ---------------------------------------------------------
# SOLO QUIZ PAGE
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("📘 Solo Quiz")

    init_session_utilities()

    st.checkbox(
        "🎯 Demo Mode (stable for live demo)",
        key="demo_mode"
    )

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    # Start / Restart
    if st.button("Start / Restart Quiz"):
        with st.spinner("Initializing quiz engine..."):
            time.sleep(0.3)
            st.session_state["engine"] = QuizEngine(mode, subject)
        st.experimental_rerun()

    engine = st.session_state.get("engine")

    if not engine:
        st.info("Click **Start / Restart Quiz** to begin.")
        return

    engine.mode = mode
    engine.subject = subject

    q = engine.get_current_question()

    if q is None:
        st.success("🎉 Quiz complete!")
        if st.button("📊 View Dashboard"):
            st.session_state["page"] = "dashboard"
            st.experimental_rerun()
        return

    selected = render_question_UI(q, mode)

    # ---------- ISL MODE ----------
    if mode == "isl":
        render_isl_number_signs(q.get("question", ""))
        render_isl_explanation(q)
    # -----------------------------

    st.caption(
        "ℹ️ Answers are evaluated using quiz logic and AI-assisted difficulty tuning."
    )

    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.experimental_rerun()

    with col2:
        if st.button("Next ➜"):
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

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    page = sidebar_navigation()
    st.session_state["page"] = page
    route_page(page)


if __name__ == "__main__":
    main()
