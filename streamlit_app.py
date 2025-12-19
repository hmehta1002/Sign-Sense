import streamlit as st
import time

# ---------------------------------------------------------
# SAFE IMPORTS (fallbacks prevent crashes)
# ---------------------------------------------------------
try:
    from backend.logic import QuizEngine
    from backend.cloud_store import (
        create_classroom,
        join_classroom,
        add_classroom_question,
        submit_classroom_answer,
        get_classroom_state,
    )
    from frontend.dashboard import render_dashboard
    from revision.revision_ui import render_revision_page
    from ai.ai_builder import ai_quiz_builder
except Exception:
    # ---------- FALLBACKS ----------
    class QuizEngine:
        def __init__(self, mode, subject):
            self.mode = mode
            self.subject = subject
            self.i = 0
            self.questions = [
                {
                    "question": "48 ÷ 6 × 4",
                    "options": ["8", "16", "32"],
                    "answer": "32",
                },
                {
                    "question": "15 + 5 × 2",
                    "options": ["40", "25", "20"],
                    "answer": "25",
                },
            ]

        def get_current_question(self):
            return self.questions[self.i] if self.i < len(self.questions) else None

        def check_answer(self, _): pass
        def next_question(self): self.i += 1

    _CLASSROOM = {"questions": [], "students": {}}

    def create_classroom(): return "ABC123"
    def join_classroom(code, name):
        _CLASSROOM["students"][name] = {"status": "Joined"}
        return True
    def add_classroom_question(code, q):
        _CLASSROOM["questions"].append(q)
    def submit_classroom_answer(code, name, i, ans):
        _CLASSROOM["students"][name]["status"] = "Answered"
    def get_classroom_state(code):
        return _CLASSROOM

    def render_dashboard(engine):
        st.subheader("📊 Dashboard")
        st.write("Dashboard placeholder")

    def render_revision_page(engine):
        st.subheader("🔁 Revision Lab")
        st.write("Revision placeholder")

    def ai_quiz_builder():
        st.subheader("🤖 AI Quiz Builder")
        st.write("AI Builder placeholder")

# ---------------------------------------------------------
# SESSION INIT
# ---------------------------------------------------------
if "cognitive_log" not in st.session_state:
    st.session_state.cognitive_log = {}

# ---------------------------------------------------------
# COGNITIVE REPLAY LOGGER
# ---------------------------------------------------------
def log_cognitive(student, question, data):
    st.session_state.cognitive_log.setdefault(student, {}).setdefault(question, []).append(data)

# ---------------------------------------------------------
# SOLO QUIZ
# ---------------------------------------------------------
def solo_quiz():
    st.header("📘 Solo Quiz")

    mode = st.selectbox("Accessibility Mode", ["standard", "isl", "adhd", "dyslexia"])
    subject = st.selectbox("Subject", ["Math", "English"])

    if st.button("Start / Restart Quiz"):
        st.session_state.engine = QuizEngine(mode, subject)
        st.session_state.start_time = time.time()
        st.session_state.option_changes = 0
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start to begin.")
        return

    q = engine.get_current_question()
    if not q:
        st.success("Quiz completed 🎉")
        return

    st.subheader(q["question"])
    choice = st.radio("Choose an option", q["options"], key="opt")

    if st.button("Next"):
        spent = int(time.time() - st.session_state.start_time)
        log_cognitive(
            "Solo_User",
            q["question"],
            {
                "mode": mode,
                "time_spent": spent,
                "option_changes": st.session_state.option_changes,
                "hesitation": "Yes" if spent > 10 else "No",
            },
        )
        engine.check_answer(choice)
        engine.next_question()
        st.session_state.start_time = time.time()
        st.experimental_rerun()

# ---------------------------------------------------------
# STUDENT CLASSROOM
# ---------------------------------------------------------
def student_classroom():
    st.header("🎓 Student Classroom")

    name = st.text_input("Your Name")
    code = st.text_input("Classroom Code")

    if st.button("Join Classroom"):
        if join_classroom(code, name):
            st.session_state.student = name
            st.session_state.joined = code
            st.success("Joined classroom")
        else:
            st.error("Invalid code")

    if "joined" in st.session_state:
        room = get_classroom_state(st.session_state.joined)
        for i, q in enumerate(room.get("questions", [])):
            st.markdown(f"**Q{i+1}: {q}**")
            ans = st.text_input("Answer", key=f"a{i}")
            if st.button("Submit", key=f"s{i}"):
                submit_classroom_answer(st.session_state.joined, st.session_state.student, i, ans)
                st.success("Submitted")

# ---------------------------------------------------------
# TEACHER CLASSROOM + COGNITIVE REPLAY
# ---------------------------------------------------------
def teacher_classroom():
    st.header("🧑‍🏫 Insight Classroom")

    if "class_code" not in st.session_state:
        if st.button("Create Classroom"):
            st.session_state.class_code = create_classroom()
    else:
        st.success(f"Classroom Code: {st.session_state.class_code}")

        q = st.text_input("Add Question")
        if st.button("Add Question"):
            add_classroom_question(st.session_state.class_code, q)
            st.success("Added")

        room = get_classroom_state(st.session_state.class_code)
        st.subheader("Students")
        for s in room.get("students", {}):
            st.write(f"• {s}")

    st.divider()
    st.subheader("🧠 Cognitive Replay")

    log = st.session_state.cognitive_log
    if not log:
        st.warning("Run at least one quiz attempt to generate replay data.")
        return

    student = st.selectbox("Student", list(log.keys()))
    question = st.selectbox("Question", list(log[student].keys()))
    r = log[student][question][-1]

    st.markdown(f"""
**Question:** {question}  
Mode: **{r['mode']}**  
Time Spent: **{r['time_spent']} sec**  
Option Changes: **{r['option_changes']}**  
Hesitation: **{r['hesitation']}**
""")

    insight = "Stable reasoning"
    if r["hesitation"] == "Yes":
        insight = "Conceptual hesitation detected"
    st.info(f"Insight: {insight}")

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    st.set_page_config("AI Quiz Portal", layout="wide")

    page = st.sidebar.radio(
        "Navigation",
        [
            "📘 Solo Quiz",
            "🔁 Revision Lab",
            "📊 Dashboard",
            "🎓 Student Classroom",
            "🧑‍🏫 Teacher Classroom",
            "🤖 Admin / AI Quiz Builder",
        ],
    )

    if page == "📘 Solo Quiz":
        solo_quiz()
    elif page == "🔁 Revision Lab":
        engine = st.session_state.get("engine")
        if engine:
            render_revision_page(engine)
        else:
            st.info("Start a quiz first.")
    elif page == "📊 Dashboard":
        engine = st.session_state.get("engine")
        if engine:
            render_dashboard(engine)
        else:
            st.info("Complete a quiz first.")
    elif page == "🎓 Student Classroom":
        student_classroom()
    elif page == "🧑‍🏫 Teacher Classroom":
        teacher_classroom()
    elif page == "🤖 Admin / AI Quiz Builder":
        ai_quiz_builder()

if __name__ == "__main__":
    main()
