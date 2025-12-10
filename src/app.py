"""
src/app.py

Robust main application router for SignSense.
This file is defensive: missing modules won't crash the app; instead,
a helpful placeholder is shown asking you to create the missing file.
"""

import streamlit as st
from importlib import import_module

# ---------- Helper to import modules safely ----------
def safe_import(module_path: str, attr: str = None):
    """
    Try to import `module_path`. If it fails, return a placeholder object.
    If attr is provided, return that attribute from the module.
    """
    try:
        mod = import_module(module_path)
        if attr:
            return getattr(mod, attr)
        return mod
    except Exception as e:
        # Return a placeholder that, when called, will render an informative page
        def placeholder(*args, **kwargs):
            st.error(f"Missing module or error importing `{module_path}`.")
            st.write("Full error (developer):")
            st.code(str(e))
            st.write("Fix: create the file/module or check for typos in the path.")
            return None
        return placeholder

# ---------- Safe imports (placeholders if missing) ----------
# UI pieces (these are expected to exist)
apply_theme = safe_import("frontend.ui", "apply_theme")
render_mode_picker = safe_import("frontend.ui", "render_mode_picker")
render_subject_picker = safe_import("frontend.ui", "render_subject_picker")
render_question_UI = safe_import("frontend.ui", "render_question_UI")

# Optional pages (dashboard / revision / live / ai)
render_dashboard = safe_import("frontend.dashboard", "render_dashboard")
render_revision_page = safe_import("revision.revision_ui", "render_revision_page")
init_live_session = safe_import("live.live_sync", "init_live_session")
live_session_page = safe_import("live.live_sync", "live_session_page")
ai_quiz_builder = safe_import("ai.ai_builder", "ai_quiz_builder")

# Core backend (QuizEngine) — show placeholder if missing
QuizEngine = safe_import("backend.logic", "QuizEngine")

# -------------------- App helpers --------------------
def reset_app():
    """Clear session state and rerun."""
    st.session_state.clear()
    st.rerun()


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


def ensure_engine():
    """Initialize QuizEngine safely if available and if mode+subject known."""
    if "engine" not in st.session_state:
        mode = st.session_state.get("mode")
        subject = st.session_state.get("subject")
        if mode and subject:
            try:
                st.session_state.engine = QuizEngine(mode, subject)
            except Exception as e:
                st.error("Failed to initialize QuizEngine.")
                st.write("Error:")
                st.code(str(e))
                st.session_state.engine = None


# -------------------- Pages --------------------
def solo_quiz_page():
    engine = st.session_state.get("engine")
    if not engine:
        st.error("Quiz engine not initialized.")
        if st.button("Initialize engine"):
            ensure_engine()
            st.rerun()
        return

    question = engine.get_current_question()

    # Completed
    if question is None:
        st.success("🎉 Quiz Complete!")
        try:
            st.balloons()
        except Exception:
            pass

        if st.button("📊 View Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return

    # Render the question (render_question_UI expected to return selected)
    selected = render_question_UI(question)

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if engine.current_index > 0:
            if st.button("⬅ Back"):
                engine.current_index -= 1
                st.rerun()

    with col2:
        if st.button("Next ➜"):
            # If check_answer exists on engine, call it before moving on
            try:
                # if user selected an option, record it
                if selected is not None and hasattr(engine, "check_answer"):
                    engine.check_answer(selected)
            except Exception:
                # ignore engine check errors — keep moving
                pass
            engine.next_question()
            st.rerun()


def dashboard_page():
    engine = st.session_state.get("engine")
    render_dashboard(engine)


def revision_page():
    engine = st.session_state.get("engine")
    render_revision_page(engine)


def live_page():
    # init_live_session and live_session_page are placeholders if module missing
    try:
        init_live_session()
    except Exception:
        pass
    live_session_page(st.session_state.get("engine"), {})


def admin_ai_page():
    ai_quiz_builder()


# -------------------- Router --------------------
def route_page(page_name: str):
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
        dashboard_page()

    elif page_name == "revision":
        revision_page()

    elif page_name == "live":
        live_page()

    elif page_name == "admin_ai":
        admin_ai_page()

    else:
        st.error("⚠ Unknown page requested.")


# -------------------- Main --------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")

    # Apply theme (if available)
    try:
        apply_theme()
    except Exception:
        # apply_theme might be a placeholder; ignore errors
        pass

    # Sidebar reset
    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    # Navigation selection
    current_page = sidebar_navigation()
    st.session_state.page = current_page

    # Route
    route_page(current_page)


if __name__ == "__main__":
    main()
