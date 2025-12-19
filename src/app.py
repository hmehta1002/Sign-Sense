import streamlit as st
import time
import re
import random

from frontend.ui import apply_theme, render_question_UI
from backend.logic import QuizEngine


# ---------------------------------------------------------
# RESET
# ---------------------------------------------------------
def reset_app():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()


# ---------------------------------------------------------
# USER PROFILE
# ---------------------------------------------------------
def render_user_profile():
    st.sidebar.subheader("User Profile")
    role = st.sidebar.selectbox("Role", ["Student", "Teacher"])
    st.session_state["role"] = role


# ---------------------------------------------------------
# INLINE AVATAR (DEMO SAFE)
# ---------------------------------------------------------
def render_demo_avatar():
    st.markdown(
        """
        <svg width="90" height="120" viewBox="0 0 110 140"
             xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="5" width="100" height="130" rx="18"
                fill="#0f172a" stroke="#334155" stroke-width="2"/>
          <circle cx="55" cy="45" r="18" fill="#cbd5e1"/>
          <rect x="25" y="70" width="60" height="40" rx="18"
                fill="#94a3b8"/>
        </svg>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# DYSLEXIC MEANING-FIRST DECOMPOSITION
# ---------------------------------------------------------
def render_dyslexic_decomposition(question_text):
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

    st.markdown("### Question Breakdown")
    st.write(f"**Action:** Simplify / Solve")
    st.write(f"**Numbers:** {', '.join(numbers)}")
    st.write(f"**Operations:** {', '.join(ops)}")
    st.write("**Goal:** Find the final answer")


# ---------------------------------------------------------
# REASONING FLOW (QUESTION SPECIFIC)
# ---------------------------------------------------------
def render_reasoning_flow(question_text):
    numbers = re.findall(r"\b\d+\b", question_text)
    st.markdown("### Reasoning Flow")

    cols = st.columns(4)
    labels = ["Numbers", "Operations", "Rule", "Outcome"]
    values = [
        ", ".join(numbers),
        "Detected from question",
        "Correct order applied",
        "Final Answer"
    ]

    for col, l, v in zip(cols, labels, values):
        with col:
            st.markdown(
                f"""
                <div style="border:1px solid #334155;
                border-radius:10px;padding:12px;
                text-align:center;background:#020617;">
                <b>{l}</b><br>{v}
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------------
# COGNITIVE REPLAY (ISL + ADHD)
# ---------------------------------------------------------
def render_cognitive_replay():
    st.markdown("### Cognitive Replay")
    steps = [
        "Numbers identified",
        "Operation order chosen",
        "Rule applied",
        "Answer derived"
    ]
    for s in steps:
        st.write(f"- {s}")
        time.sleep(0.2)


# ---------------------------------------------------------
# CLASSROOM (TEACHER INSIGHTS)
# ---------------------------------------------------------
def render_classroom_dashboard():
    st.header("Insight Classroom")

    if "class_code" not in st.session_state:
        st.session_state.class_code = f"CLS-{random.randint(100,999)}"

    st.success(f"Classroom Code: {st.session_state.class_code}")

    st.markdown("### Cognitive Heatmap (Simulated)")
    st.progress(0.8)
    st.write("Numbers understood: 80%")
    st.progress(0.45)
    st.write("Operation confusion: 45%")
    st.progress(0.2)
    st.write("Rule misunderstanding: 20%")

    st.markdown("**Most common breakdown:** Operation Order")


# ---------------------------------------------------------
# SOLO QUIZ
# ---------------------------------------------------------
def solo_quiz():
    st.header("Solo Quiz")

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl"]
    )

    if st.button("Start Quiz"):
        st.session_state.engine = QuizEngine(mode, "math")

    engine = st.session_state.get("engine")
    if not engine:
        return

    q = engine.get_current_question()
    if not q:
        st.success("Quiz complete")
        return

    render_question_UI(q, mode)

    if mode == "dyslexia":
        render_dyslexic_decomposition(q["question"])

    if mode in ["isl", "adhd"]:
        render_reasoning_flow(q["question"])
        render_cognitive_replay()

    if mode == "isl":
        render_demo_avatar()

    if st.button("Next"):
        engine.next_question()
        st.experimental_rerun()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    render_user_profile()

    if st.sidebar.button("Reset App"):
        reset_app()

    role = st.session_state.get("role", "Student")

    if role == "Teacher":
        render_classroom_dashboard()
    else:
        solo_quiz()


if __name__ == "__main__":
    main()
