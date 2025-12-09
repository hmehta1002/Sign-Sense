import random
import streamlit as st

st.set_page_config(page_title="SignSense", layout="wide")

from backend.logic import QuizEngine
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
        "mode": None,        # 'standard', 'dyslexia', 'adhd', 'isl'
        "subject": None,     # 'math' or 'english'
        "engine": None,      # QuizEngine instance
        "answered": False,   # whether current question has been answered
        "feedback": None,    # last question feedback dict
        "live_session": {
            "code": "",
            "status": "idle",       # 'idle', 'waiting', 'in_progress', 'finished'
            "players": [],          # list of {name, score}
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


# ---------- LIVE SESSION (SIMULATED HOST + LEADERBOARD) ----------

def live_session_page(engine: "QuizEngine | None", xp_info: dict):
    st.subheader("🌐 Live Session (Prototype Host View)")

    live = st.session_state.live_session

    col1, col2 = st.columns(2)
    with col1:
        code = st.text_input(
            "Session Code",
            value=live.get("code", ""),
            help="In production this would be shared with participants.",
        )
        live["code"] = code or "SIGN123"

        status = st.selectbox(
            "Session Status",
            options=["idle", "waiting", "in_progress", "finished"],
            index=["idle", "waiting", "in_progress", "finished"].index(
                live.get("status", "idle")
            ),
        )
        live["status"] = status

    with col2:
        st.write("**Host Controls (Prototype)**")
        st.write("• Share session code with learners.")
        st.write("• Start quiz when everyone has joined.")
        st.write("• Watch live leaderboard below.")

    st.markdown("---")
    st.write("### 👥 Players in this session (demo data)")

    # Demo players data (for prototype)
    if not live.get("players"):
        if st.button("➕ Add demo players"):
            live["players"] = [
                {"name": "Aditi", "score": 780},
                {"name": "Rohan", "score": 650},
                {"name": "Sara", "score": 540},
            ]

    # Manual add player
    with st.expander("Add player manually (prototype)", expanded=False):
        pname = st.text_input("Player name", key="add_player_name")
        pscore = st.number_input(
            "Score", min_value=0, max_value=2000, value=500, step=10
        )
        if st.button("Add to leaderboard"):
            if pname:
                live.setdefault("players", []).append(
                    {"name": pname, "score": int(pscore)}
                )

    players = sorted(live.get("players", []), key=lambda x: x["score"], reverse=True)

    if players:
        for i, p in enumerate(players, start=1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
            st.write(f"{medal} **{p['name']}** — {p['score']} pts")
    else:
        st.info("No players yet. Use demo button or add manually to simulate leaderboard.")

    st.markdown("---")
    st.caption(
        "This screen demonstrates the host + live leaderboard concept. "
        "In the final architecture this will be powered by WebSockets / PubSub and a real-time database."
    )


# ---------- ADMIN + AI QUIZ BUILDER (PROTOTYPE) ----------

def admin_ai_page(engine: "QuizEngine | None"):
    st.subheader("🧠 Admin & AI Quiz Builder (Prototype)")

    st.write(
        "This panel simulates AI-driven quiz creation. In the full build, an LLM will "
        "read PDFs / notes and auto-generate questions."
    )

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox("Target subject", ["math", "english"])
        topic = st.text_input("Topic / concept (e.g., fractions, tenses)")
        num_q = st.slider("Number of questions", 3, 15, 5)

    with col2:
        uploaded = st.file_uploader(
            "Optional: Upload a PDF / text file (prototype)",
            type=["pdf", "txt"],
            help="In the real system, we parse this and send it to an AI model.",
        )
        if uploaded is not None:
            st.info("📎 File received. In full version an AI model will read this.")

    if st.button("⚡ Generate quiz with AI (simulated)"):
        if engine is None:
            st.error("Run a quiz at least once so questions are loaded.")
            return

        # Create a temporary engine to ensure we have all questions for chosen subject
        temp_engine = QuizEngine(st.session_state.mode or "standard", subject)
        pool = temp_engine.questions

        if topic:
            filtered = [
                q
                for q in pool
                if topic.lower() in q["question"].lower()
                or any(topic.lower() in h.lower() for h in q.get("hints", []))
            ]
        else:
            filtered = pool

        if not filtered:
            filtered = pool

        k = min(num_q, len(filtered))
        new_quiz = random.sample(filtered, k=k)

        # Overwrite current engine with new AI-generated quiz
        st.session_state.engine = QuizEngine(st.session_state.mode, subject)
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


# ---------- SIDEBAR NAVIGATION ----------

def sidebar_nav():
    st.sidebar.title("⚡ SignSense")

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
