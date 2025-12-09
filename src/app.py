import random

import streamlit as st

st.set_page_config(page_title="SignSense", layout="wide")

from backend.logic import QuizEngine
from backend.cloud_store import add_score, get_leaderboard
from frontend.ui import (
    render_header,
    render_mode_picker,
    render_subject_picker,
    render_question,
    render_results,
    render_hud,
)
from frontend.dashboard import render_dashboard


# ---------- SESSION STATE ----------


def init_state():
    defaults = {
        "user_name": "",
        "mode": None,  # 'standard', 'dyslexia', 'adhd', 'isl'
        "subject": None,  # 'math' or 'english'
        "engine": None,  # QuizEngine instance
        "answered": False,  # whether current question has been answered
        "feedback": None,  # last question feedback dict
        "live_session": {
            "code": "",
            "status": "waiting",  # 'waiting', 'in_progress', 'finished'
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            # copy mutable defaults like dict
            if isinstance(v, dict):
                st.session_state[k] = v.copy()
            else:
                st.session_state[k] = v


def reset_app():
    """Clear everything and re-init."""
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()


# ---------- XP & BADGES ----------


def compute_xp_and_badges(engine: "QuizEngine | None"):
    """Derive XP, level and badges from quiz performance."""
    if engine is None or not engine.history:
        return {"xp": 0, "level": 1, "badges": []}

    xp = engine.score
    level = max(1, xp // 200 + 1)

    history = engine.history
    total = len(history)
    correct_count = sum(1 for h in history if h["correct"])

    badges = []

    # High streak badge
    if engine.best_streak >= 3:
        badges.append("🔥 Focus Streaker (3+ correct in a row)")

    # Speed badge
    if any(
        (h.get("time_taken") is not None and h["time_taken"] <= 5)
        for h in history
    ):
        badges.append("⚡ Speedster (answered in ≤ 5s)")

    # Accuracy badge
    if total >= 5 and correct_count / total >= 0.8:
        badges.append("🎯 Accuracy Ace (80%+ correct)")

    # Completion badge
    if total == len(engine.questions):
        badges.append("🏁 Quiz Finisher")

    return {"xp": xp, "level": level, "badges": badges}


# ---------- QUIZ FLOW (SOLO) ----------


def quiz_flow():
    engine: QuizEngine = st.session_state.engine
    question = engine.get_current_question()

    # End of quiz
    if question is None:
        xp_info = compute_xp_and_badges(engine)

        # Determine session code for saving score (SOLO or live session code)
        live = st.session_state.get("live_session", {})
        session_code = live.get("code") or "SOLO"
        user_name = st.session_state.get("user_name") or "Anonymous"

        add_score(
            session_code=session_code,
            name=user_name,
            score=engine.score,
            mode=st.session_state.mode,
            subject=st.session_state.subject,
        )

        render_results(engine, xp_info)
        if st.button("🔁 Restart Quiz"):
            reset_app()
        return

    total = len(engine.questions)
    index = engine.current_index + 1

    answer = render_question(
        question,
        st.session_state.mode,
        index,
        total,
    )

    # First phase: user hasn't submitted yet
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            fb = engine.check_answer(answer)
            st.session_state.feedback = fb
            st.session_state.answered = True

    # Second phase: show feedback + Next button
    else:
        fb = st.session_state.feedback
        if fb is None:
            st.warning("Something went wrong; please try next question.")
        else:
            if fb["correct"]:
                st.success(f"✔ Correct! +{fb['points']} points")
            else:
                st.error(f"❌ Incorrect — correct answer: **{fb['correct_answer']}**")

            if fb["time"] is not None:
                st.info(f"⏱ Time taken: {fb['time']} seconds")

        if st.button("Next ➡"):
            engine.next_question()
            st.session_state.answered = False
            st.session_state.feedback = None


# ---------- REVISION LAB ----------


def revision_lab(engine: "QuizEngine | None"):
    st.subheader("📚 Revision Lab — Fix Your Mistakes")

    if engine is None or not engine.history:
        st.info("Complete at least one quiz to unlock the Revision Lab.")
        return

    wrong = [h for h in engine.history if not h["correct"]]

    if not wrong:
        st.success("🌟 You had no wrong answers! Nothing to revise.")
        return

    st.write(f"You have **{len(wrong)}** questions to revisit.")

    options = [
        f"{i+1}. {item['question'][:60]}..." for i, item in enumerate(wrong)
    ]
    chosen_label = st.selectbox("Pick a question to review:", options=options)
    idx = options.index(chosen_label)
    item = wrong[idx]

    st.markdown(
        f"""
        **Original Question**  
        {item['question']}

        **Your Answer:** {item.get('selected', '—')}  
        **Correct Answer:** ✅ {item['correct_answer']}
        """,
    )

    if "difficulty" in item:
        st.caption(f"Difficulty: {item['difficulty']}")

    st.info(
        "🧠 Use this space to explain why the correct answer is right in your own words. "
        "This mimics an AI explanation step in future versions."
    )
    st.text_area("Your explanation (reflection)", key="revision_explanation", height=120)


# ---------- LIVE SESSION (HOST + CLOUD LEADERBOARD) ----------


def live_session_page(engine: "QuizEngine | None", xp_info: dict):
    st.subheader("🌐 Live Session (Prototype Host View)")

    live = st.session_state.live_session

    col1, col2 = st.columns([2, 1])
    with col1:
        code = st.text_input(
            "Session Code",
            value=live.get("code") or "SIGN123",
            help="Share this with learners so their scores group under one session.",
        )
        live["code"] = (code or "SIGN123").strip()

        status_options = ["waiting", "in_progress", "finished"]
        status = st.selectbox(
            "Session Status",
            options=status_options,
            index=status_options.index(live.get("status", "waiting")),
            help="Prototype toggle to show how sessions move through stages.",
        )
        live["status"] = status

    with col2:
        st.write("**Host Controls (Prototype)**")
        st.write("• Give participants the session code.")
        st.write("• They play the quiz on their device.")
        st.write("• As scores are saved, leaderboard updates here.")
        st.caption(
            "In the full system, this will be powered by WebSockets and a cloud database."
        )

    st.markdown("---")
    st.write("### 👥 Live Leaderboard")

    session_code = live.get("code") or "SIGN123"
    leaderboard = get_leaderboard(session_code)

    if not leaderboard:
        st.info(
            "No scores yet. Once participants complete quizzes using this session "
            "code, their scores will appear here."
        )
    else:
        for i, rec in enumerate(leaderboard, start=1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
            st.write(
                f"{medal} **{rec.get('name','?')}** — {rec.get('score',0)} pts "
                f"· {rec.get('mode','?')}/{rec.get('subject','?')}"
            )

    st.caption(
        "If Firebase is configured, this leaderboard syncs through Firestore. "
        "Otherwise, it runs in-memory for the demo."
    )


# ---------- ADMIN + AI QUIZ BUILDER (NO OVERLAP) ----------


def admin_ai_page(engine: "QuizEngine | None"):
    st.subheader("🧠 Admin & AI Quiz Builder (Prototype)")
    st.write(
        "This panel simulates AI-driven quiz creation. In the full build, an AI "
        "model will read PDFs / notes and auto-generate questions."
    )

    # Subtle styling for the uploader
    st.markdown(
        """
        <style>
        div[data-testid="stFileUploader"] {
            border: 2px dashed #6b46c1;
            padding: 16px;
            border-radius: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        subject = st.selectbox("Target subject", ["math", "english"])
        topic = st.text_input("Topic / concept (e.g., fractions, tenses)")

        num_q = st.slider("Number of questions", 3, 15, 5)
        st.markdown(
            f"<p style='font-size:13px;color:#aaaaaa;'>Selected: {num_q} questions</p>",
            unsafe_allow_html=True,
        )

        generate = st.button(
            "⚡ Generate quiz with AI (simulated)", use_container_width=True
        )

        if generate:
            # We can create a temporary engine to access the full question pool
            temp_engine = QuizEngine(st.session_state.mode or "standard", subject)
            pool = temp_engine.questions

            if topic:
                filtered = [
                    q
                    for q in pool
                    if topic.lower() in q["question"].lower()
                    or any(
                        topic.lower() in h.lower() for h in q.get("hints", [])
                    )
                ]
            else:
                filtered = pool

            if not filtered:
                filtered = pool

            k = min(num_q, len(filtered))
            new_quiz = random.sample(filtered, k=k)

            # Overwrite current engine with new AI-generated quiz
            st.session_state.engine = QuizEngine(
                st.session_state.mode, subject
            )
            st.session_state.engine.questions = new_quiz
            st.session_state.engine.current_index = 0
            st.session_state.engine.history = []
            st.session_state.engine.score = 0
            st.session_state.engine.streak = 0
            st.session_state.engine.best_streak = 0

            st.success(
                f"✅ Simulated AI generated {k} questions for subject '{subject}' "
                f"on topic '{topic or 'general'}'."
            )
            st.info("Go to the Solo Quiz page to play this AI-generated quiz.")

    with col_right:
        st.markdown("##### 📄 Upload PDF / Text (optional)")
        uploaded = st.file_uploader(
            "Upload a document", type=["pdf", "txt"]
        )

        if uploaded is not None:
            st.info(f"📁 File uploaded: `{uploaded.name}`")
            st.caption(
                "In the full version, an AI model will extract key concepts from this file."
            )


# ---------- SIDEBAR NAVIGATION ----------


def sidebar_nav():
    st.sidebar.title("⚡ SignSense")

    st.sidebar.text_input(
        "Your name (for leaderboard)",
        key="user_name",
        placeholder="Enter name",
    )

    if st.sidebar.button("🔁 Reset App"):
        reset_app()

    page = st.sidebar.radio(
        "Go to:",
        ["Solo Quiz", "Live Session", "Revision Lab", "Dashboard", "Admin / AI Quiz"],
        index=0,
        key="nav_page",
    )
    return page


# ---------- MAIN ----------


def main():
    init_state()

    page = sidebar_nav()

    # Step 1: pick mode
    if st.session_state.mode is None:
        render_mode_picker()
        return

    # Step 2: pick subject
    if st.session_state.subject is None:
        render_subject_picker()
        return

    # Step 3: create engine (once)
    if st.session_state.engine is None:
        st.session_state.engine = QuizEngine(
            st.session_state.mode,
            st.session_state.subject,
        )

    engine: QuizEngine = st.session_state.engine
    xp_info = compute_xp_and_badges(engine)

    # Global header + HUD
    render_header(st.session_state.mode)
    render_hud(engine, xp_info)

    # Router
    if page == "Solo Quiz":
        quiz_flow()
    elif page == "Live Session":
        live_session_page(engine, xp_info)
    elif page == "Revision Lab":
        revision_lab(engine)
    elif page == "Dashboard":
        render_dashboard(engine, xp_info)
    else:
        admin_ai_page(engine)


if __name__ == "__main__":
    main()
