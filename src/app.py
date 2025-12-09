import streamlit as st

# -------- FIXED IMPORTS (DO NOT CHANGE) --------
from frontend.ui import apply_theme, render_mode_picker, render_subject_picker, render_question_UI
from frontend.dashboard import render_dashboard
from backend.logic import QuizEngine
from ai.ai_builder import ai_quiz_builder
from live.live_sync import init_live_session, live_session_page
from revision.revision_ui import render_revision_page


# -------- RESET BUTTON --------
def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# -------- SIDEBAR NAVIGATION --------
def sidebar_navigation():
    pages = {
        "📘 Solo Quiz": "solo",
        "🌐 Live Session": "live",
        "🔁 Revision Lab": "revision",
        "📊 Dashboard": "dashboard",
        "🤖 Admin / AI Quiz": "admin_ai"
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]


# -------- ENSURE ENGINE EXISTS --------
def ensure_engine():
    if "engine" not in st.session_state:
        if st.session_state.get("mode") and st.session_state.get("subject"):
            st.session_state.engine = QuizEngine(
                st.session_state.mode,
                st.session_state.subject
            )


# -------- SOLO QUIZ MODE --------
def solo_quiz_page():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        st.success("🎉 Quiz Complete!")
        st.balloons()
        if st.button("📊 View Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    render_question_UI(question)

    col1, col2 = st.columns(2)
    with col1:
        if engine.current_index > 0 and st.button("⬅ Back"):
            engine.current_index -= 1
            st.rerun()

    with col2:
        if st.button("Next ➜"):
            engine.next_question()
            st.rerun()


# -------- MAIN APP --------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    apply_theme()

    # Reset App
    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    st.session_state.page = sidebar_navigation()

    # ROUTING
    if st.session_state.page == "solo":
        if "mode" not in st.session_state:
            render_mode_picker()
            return

        if "subject" not in st.session_state:
            render_subject_picker()
            return

        ensure_engine()
        solo_quiz_page()

    elif st.session_state.page == "dashboard":
        render_dashboard(st.session_state.get("engine"))

    elif st.session_state.page == "revision":
        render_revision_page(st.session_state.get("engine"))

    elif st.session_state.page == "live":
        init_live_session()
        live_session_page(st.session_state.get("engine"), {})

    elif st.session_state.page == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("⚠ Unknown navigation state.")


if __name__ == "__main__":
    main()
