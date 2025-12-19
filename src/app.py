import streamlit as st
import time

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
# USER PROFILE & 3D AVATAR
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
            f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        )
        st.sidebar.image(avatar_url, width=120)
        st.sidebar.caption("3D Avatar (auto-generated, privacy-safe)")


# ---------------------------------------------------------
# SESSION UTILITIES
# ---------------------------------------------------------
def init_session_utilities():
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

    if "history" not in st.session_state:
        st.session_state.history = []


# ---------------------------------------------------------
# IMPRESSIVE ISL MODE (AVATAR + STEP-SYNC EXPLANATION)
# ---------------------------------------------------------
def highlight_question_keywords(question_text: str):
    keywords = [
        "sum", "difference", "total", "equal",
        "greater", "less", "add", "subtract"
    ]

    highlighted = question_text
    for word in keywords:
        highlighted = highlighted.replace(
            word, f"**{word.upper()}**"
        )

    st.markdown("### 🧠 Key Focus Areas")
    st.markdown(highlighted)


def render_impressive_isl_mode(question_data):
    st.success("🤟 ISL Accessibility Mode Active")

    isl_avatar_url = (
        "https://api.dicebear.com/7.x/bottts/svg?seed=isl_explainer"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(isl_avatar_url, width=160)
        st.caption("ISL Sign Avatar")

    with col2:
        st.markdown("### 📖 Visual Explanation (ISL-Assisted)")
        st.info(
            "Explanation is presented step-by-step for sign-language learners "
            "using visual sequencing instead of audio."
        )

        steps = [
            "Identify the **important words or numbers** in the question.",
            "Understand **what the question is asking**.",
            "Apply the **correct rule or concept**.",
            "Choose the **best answer** from the options."
        ]

        for step in steps:
            st.write("👉 " + step)
            time.sleep(0.35)


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
        "🎯 Demo Mode (stable behaviour for live demo)",
        key="demo_mode"
    )

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl", "hybrid"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    # Start / Restart Quiz (STABLE)
    if st.button("Start / Restart Quiz"):
        with st.spinner("Initializing quiz engine..."):
            time.sleep(0.3)
            st.session_state["engine"] = QuizEngine(mode, subject)
            st.session_state["solo_started"] = True
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

    # ---- ISL MODE ADDITION ----
    if mode == "isl":
        highlight_question_keywords(q.get("question", ""))
        render_impressive_isl_mode(q)
    # --------------------------

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
                    "selected": selected,
                    "correct": q.get("answer")
                })

            engine.next_question()
            st.experimental_rerun()

    if st.session_state.history:
        with st.expander("🕘 Session History (Last 3 Attempts)"):
            for item in st.session_state.history[-3:]:
                st.write(
                    f"**Q:** {item['question']}  \n"
                    f"**Your Answer:** {item['selected']}"
                )


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

    elif page_name == "admin_ai":
        ai_quiz_builder()

    else:
        st.error("Unknown page.")


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
