import streamlit as st

from frontend.ui import apply_theme, render_mode_picker, render_subject_picker, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page


# ---------------- RESET ENTIRE APP ----------------
def reset_app():
    st.session_state.clear()
    st.experimental_rerun()


# ---------------- SIDEBAR NAVIGATION ----------------
def sidebar_navigation():
    pages = {
        "📘 Solo Quiz": "solo",
        "🌐 Live Session": "live",
        "🔁 Revision Lab": "revision",
        "📊 Dashboard": "dashboard",
        "🤖 Admin / AI Quiz": "admin_ai",
    }

    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    return pages[selection]


# ---------------- ENGINE SETUP ----------------
def ensure_engine():
    if "engine" not in st.session_state:
        mode = st.session_state.get("mode")
        subject = st.session_state.get("subject")

        if mode and subject:
            st.session_state.engine = QuizEngine(mode, subject)
# ---------------- SOLO QUIZ PAGE ----------------
def solo_quiz_page():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        st.success("🎉 Quiz Complete!")
        st.balloons()

        if st.button("📊 View Dashboard"):
            st.session_state.page = "dashboard"
            st.experimental_rerun()

        return

    # Render the actual question UI
    render_question_UI(question)

    # Navigation buttons
    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0 and st.button("⬅ Back"):
            engine.current_index -= 1
            st.experimental_rerun()

    with col2:
        if st.button("Next ➜"):
            engine.next_question()
            st.experimental_rerun()


# ---------------- ROUTER ----------------
def route_page(page_name):
    if page_name == "solo":
        if "mode" not in st.session_state:
            render_mode_picker()
            return

        if "subject" not in st.session_state:
            render_subject_picker()
            return

        ensure_engine()
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
# ---------------- MAIN APPLICATION ----------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    apply_theme()

    # Reset button
    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    # Navigation
    current_page = sidebar_navigation()
    st.session_state.page = current_page

    # Route to correct page
    route_page(current_page)


# --------------- ENTRY POINT ----------------
if __name__ == "__main__":
    main()
