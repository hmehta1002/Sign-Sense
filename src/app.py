import streamlit as st
import time
import re
import random

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
# USER PROFILE & ROLE
# ---------------------------------------------------------
def render_user_profile():
    st.sidebar.subheader("User Profile")
    role = st.sidebar.selectbox("Role", ["Student", "Teacher"])
    st.session_state["role"] = role


# ---------------------------------------------------------
# INLINE DEMO AVATAR (ALWAYS VISIBLE)
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
# DYSLEXIC: MEANING-FIRST DECOMPOSITION
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
    st.write("**Action:** Solve / Simplify")
    st.write(f"**Numbers:** {', '.join(numbers)}")
    st.write(f"**Operations:** {', '.join(ops)}")
    st.write("**Goal:** Find the correct final answer")


# ---------------------------------------------------------
# QUESTION-SPECIFIC REASONING FLOW (ISL + ADHD)
# ---------------------------------------------------------
def render_reasoning_flow(question_text):
    text = question_text.lower()

    # 1. Extract numbers in order
    numbers = re.findall(r"\b\d+\b", text)

    # 2. Detect operations in order of appearance
    operations = []

    word_ops = [
        ("divided by", "Division"),
        ("divide", "Division"),
        ("division", "Division"),
        ("multiplied by", "Multiplication"),
        ("multiply", "Multiplication"),
        ("multiplication", "Multiplication"),
        ("added to", "Addition"),
        ("add", "Addition"),
        ("addition", "Addition"),
        ("subtracted from", "Subtraction"),
        ("subtract", "Subtraction"),
        ("subtraction", "Subtraction"),
    ]

    symbol_ops = {
        "÷": "Division",
        "/": "Division",
        "×": "Multiplication",
        "*": "Multiplication",
        "+": "Addition",
        "-": "Subtraction",
    }

    # Find word-based operations in text order
    for phrase, op_name in word_ops:
        if phrase in text:
            operations.append(op_name)

    # Find symbol-based operations
    for char in question_text:
        if char in symbol_ops:
            operations.append(symbol_ops[char])

    # Remove duplicates while preserving order
    operations = list(dict.fromkeys(operations))

    # 3. Build operation steps with numbers
    steps = []
    for i in range(min(len(numbers) - 1, len(operations))):
        steps.append(f"{numbers[i]} {operations[i]} {numbers[i+1]}")

    if not steps:
        steps = ["Single-step reasoning"]

    # 4. Decide rule
    rule = "Left-to-right evaluation"
    if "Addition" in operations or "Subtraction" in operations:
        if "Multiplication" in operations or "Division" in operations:
            rule = "BODMAS / Operator precedence"

    # 5. Render
    st.markdown("### Reasoning Flow (Question-Specific)")

    cols = st.columns(4)

    with cols[0]:
        st.markdown(
            f"""
            <div style="border:1px solid #334155;
            border-radius:12px;padding:14px;
            text-align:center;background:#020617;">
            <b>Numbers</b><br>{', '.join(numbers)}
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[1]:
        st.markdown(
            f"""
            <div style="border:1px solid #334155;
            border-radius:12px;padding:14px;
            text-align:center;background:#020617;">
            <b>Operations</b><br>{'<br>'.join(steps)}
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[2]:
        st.markdown(
            f"""
            <div style="border:1px solid #334155;
            border-radius:12px;padding:14px;
            text-align:center;background:#020617;">
            <b>Rule Applied</b><br>{rule}
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[3]:
        st.markdown(
            f"""
            <div style="border:1px solid #334155;
            border-radius:12px;padding:14px;
            text-align:center;background:#020617;">
            <b>Outcome</b><br>Final Answer
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
        "Operation order selected",
        "Rule applied",
        "Answer derived"
    ]
    for s in steps:
        st.write(f"- {s}")


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
# SIDEBAR NAVIGATION (RESTORED)
# ---------------------------------------------------------
def sidebar_navigation():
    pages = {
        "Solo Quiz": "solo",
        "Live Session": "live",
        "Revision Lab": "revision",
        "Dashboard": "dashboard",
        "Admin / AI Quiz Builder": "admin_ai",
    }
    return pages[st.sidebar.radio("Navigation", list(pages.keys()))]


# ---------------------------------------------------------
# SOLO QUIZ PAGE (FULL)
# ---------------------------------------------------------
def solo_quiz_page():
    st.header("Solo Quiz")

    mode = st.selectbox(
        "Accessibility Mode",
        ["standard", "dyslexia", "adhd", "isl"]
    )

    subject_label = st.selectbox("Subject", ["Math", "English"])
    subject = subject_label.lower()

    if st.button("Start / Restart Quiz"):
        st.session_state.engine = QuizEngine(mode, subject)
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start / Restart Quiz to begin.")
        return

    q = engine.get_current_question()
    if q is None:
        st.success("Quiz complete.")
        return

    selected = render_question_UI(q, mode)

    if mode == "dyslexia":
        render_dyslexic_decomposition(q["question"])

    if mode in ["isl", "adhd"]:
        render_reasoning_flow(q["question"])
        render_cognitive_replay()

    if mode == "isl":
        render_demo_avatar()

    col1, col2 = st.columns(2)
    with col2:
        if st.button("Next"):
            if selected:
                engine.check_answer(selected)
            engine.next_question()
            st.experimental_rerun()


# ---------------------------------------------------------
# ROUTER (RESTORED)
# ---------------------------------------------------------
def route_page(page):
    role = st.session_state.get("role", "Student")

    if role == "Teacher":
        render_classroom_dashboard()
        return

    if page == "solo":
        solo_quiz_page()
    elif page == "dashboard":
        render_dashboard(st.session_state.get("engine"))
    elif page == "revision":
        render_revision_page(st.session_state.get("engine"))
    elif page == "live":
        engine = st.session_state.get("engine")
        if engine:
            from live.live_sync import live_session_page
            live_session_page(engine, {})
        else:
            st.warning("Start a quiz first.")
    elif page == "admin_ai":
        ai_quiz_builder()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="SignSense", layout="wide")
    apply_theme()

    render_user_profile()

    if st.sidebar.button("Reset App"):
        reset_app()

    page = sidebar_navigation()
    route_page(page)


if __name__ == "__main__":
    main()
