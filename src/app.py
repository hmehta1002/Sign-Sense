import streamlit as st

# Import UI functions
from frontend.ui import (
    apply_theme,
    render_mode_picker,
    render_subject_picker,
    render_question_UI,
)

# Imported pages
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page


# ---------------------------------------------------------
# RESET APPLICATION
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

    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    return pages[selection]


# ---------------------------------------------------------
# ENSURE QUIZ ENGINE EXISTS
# ---------------------------------------------------------
def ensure_engine():
    if "engine" not in st.session_state:
        mode = st.session_state.get("mode")
        subject = st.session_state.get("subject")

        if mode and subject:
            st.session_state.engine = QuizEngine(mode, subject)


# ---------------------------------------------------------
# SOLO QUIZ LOGIC
# ---------------------------------------------------------
def solo_quiz_page():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # Quiz completed
    if question is None:
        st.success("🎉 Quiz Complete!")
        st.balloons()

        if st.button("📊 View Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()

        return

    # Render question UI
    selected = render_question_UI(question)

    # Navigation buttons
    col1, col2 = st.columns(2)

    # Back button
    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.rerun()

    # Next button
    with col2:
        if st.button("Next ➜"):
            engine.next_question()
            st.rerun()


# ---------------------------------------------------------
# PAGE ROUTER
# ---------------------------------------------------------
def route_page(page_name):
    if page_name == "solo":

        # Step 1 — Mode not chosen yet
        if "mode" not in st.session_state:
            render_mode_picker()
            return

        # Step 2 — Subject not chosen yet
        if "subject" not in st.session_state:
            render_subject_picker()
            return

        # Step 3 — Engine setup
        ensure_engine()

        # Step 4 — Run the quiz
        solo_quiz_page()

    elif page_name == "dashboard":
        render_dashboard(st.session_state.get("engine"))

    elif page_name == "revision":
        render_revision_page(st.session_state.get("engine"))

    elif page_name == "live":
        init_live_session()
        live_session_page(st.session_state.get("engine"), {})

    elif page_name == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("⚠ Unknown page requested.")


# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    # Theme
    apply_theme()

    # Reset button
    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    # Navigation
    current_page = sidebar_navigation()
    st.session_state.page = current_page

    # Routing
    route_page(current_page)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
