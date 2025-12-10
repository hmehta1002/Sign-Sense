import streamlit as st

from frontend.ui import apply_theme, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from revision.revision_ui import render_revision_page


# ---------------------------------------------------------
# RESET APP
# ---------------------------------------------------------
def reset_app():
    st.session_state.clear()
    st.rerun()


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
# ENSURE ENGINE EXISTS
# ---------------------------------------------------------
def ensure_engine(mode: str, subject: str):
    """Create QuizEngine if not present."""
    if "engine" not in st.session_state:
        st.session_state["engine"] = QuizEngine(mode, subject)
    return st.session_state["engine"]


# ---------------------------------------------------------
# SOLO QUIZ PAGE
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("📘 Solo Quiz")

    # Accessibility + Subject selection
    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"],
        index=0,
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    # Start/Restart
    if st.button("Start / Restart Quiz"):
        st.session_state["engine"] = QuizEngine(mode, subject)

    engine: QuizEngine | None = st.session_state.get("engine")

    if not engine:
        st.info("Click 'Start / Restart Quiz' to begin.")
        return

    # Sync engine mode & subject
    engine.mode = mode
    engine.subject = subject

    # Get current question
    question = engine.get_current_question()

    if question is None:
        st.success("🎉 Quiz complete!")
        if st.button("📊 View Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()
        return

    # Render question UI
    selected = render_question_UI(question, mode)

    col1, col2 = st.columns(2)

    # Back Button
    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.rerun()

    # Next Button
    with col2:
        if st.button("Next ➜"):
            if selected is not None:
                try:
                    engine.check_answer(selected)
                except Exception:
                    pass
            engine.next_question()
            st.rerun()


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
            st.warning("Start a quiz first to initialize the question engine.")
            return

        from live.live_sync import live_session_page
        live_session_page(engine, {})
        return

    elif page_name == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("Unknown page.")


# ---------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    apply_theme()

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    page = sidebar_navigation()
    st.session_state["page"] = page

    route_page(page)


if __name__ == "__main__":
    main()
