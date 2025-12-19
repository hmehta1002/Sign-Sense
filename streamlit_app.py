import streamlit as st
import time

# ==============================
# MOCK / SAFE IMPORTS
# (replace with your real ones if already present)
# ==============================
try:
    from backend.logic import QuizEngine
    from backend.cloud_store import (
        create_classroom,
        join_classroom,
        add_classroom_question,
        submit_classroom_answer,
        get_classroom_state,
    )
except Exception:
    # fallback so app never crashes
    class QuizEngine:
        def __init__(self, mode, subject):
            self.questions = [
                {"question": "48 ÷ 6 × 4", "options": ["8", "16", "32"], "answer": "32"}
            ]
            self.i = 0

        def get_current_question(self):
            return self.questions[self.i] if self.i < len(self.questions) else None

        def check_answer(self, x): pass
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


# ==============================
# COGNITIVE REPLAY STORAGE
# ==============================
if "cognitive_log" not in st.session_state:
    st.session_state.cognitive_log = {}


def log_cognitive(student, question, data):
    st.session_state.cognitive_log.setdefault(student, {}).setdefault(question, []).append(data)


# ==============================
# SOLO QUIZ
# ==============================
def solo_quiz():
    st.header("📘 Solo Quiz")

    mode = st.selectbox("Mode", ["standard", "isl", "adhd", "dyslexia"])
    subject = st.selectbox("Subject", ["Math", "English"])

    if st.button("Start / Restart"):
        st.session_state.engine = QuizEngine(mode, subject)
        st.session_state.q_start = time.time()
        st.session_state.option_changes = 0
        st.experimental_rerun()

    engine = st.session_state.get("engine")
    if not engine:
        st.info("Click Start to begin")
        return

    q = engine.get_current_question()
    if not q:
        st.success("Quiz completed")
        return

    st.subheader(q["question"])
    choice = st.radio("Choose", q["options"], key="opt")

    if st.button("Next"):
        spent = int(time.time() - st.session_state.q_start)
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
        st.session_state.q_start = time.time()
        st.experimental_rerun()


# ==============================
# STUDENT CLASSROOM
# ==============================
def student_classroom():
    st.header("🎓 Student Classroom")

    name = st.text_input("Your name")
    code = st.text_input("Class code")

    if st.button("Join"):
        if join_classroom(code, name):
            st.session_state.student = name
            st.session_state.joined = code
            st.success("Joined classroom")

    if "joined" in st.session_state:
        room = get_classroom_state(st.session_state.joined)
        for i, q in enumerate(room.get("questions", [])):
            st.write(f"Q{i+1}: {q}")
            ans = st.text_input("Answer", key=f"a{i}")
            if st.button("Submit", key=f"s{i}"):
                submit_classroom_answer(st.session_state.joined, st.session_state.student, i, ans)
                st.success("Submitted")


# ==============================
# TEACHER CLASSROOM + COGNITIVE REPLAY
# ==============================
def teacher_classroom():
    st.header("🧑‍🏫 Insight Classroom")

    if "class_code" not in st.session_state:
        if st.button("Create Classroom"):
            st.session_state.class_code = create_classroom()
    else:
        st.success(f"Class Code: {st.session_state.class_code}")

        q = st.text_input("Add question")
        if st.button("Add"):
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
        st.warning("Run a quiz attempt to generate replay data.")
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


# ==============================
# MAIN
# ==============================
def main():
    st.set_page_config("AI Quiz Portal", layout="wide")

    page = st.sidebar.radio(
        "Navigate",
        ["Solo Quiz", "Student Classroom", "Teacher Classroom"]
    )

    if page == "Solo Quiz":
        solo_quiz()
    elif page == "Student Classroom":
        student_classroom()
    else:
        teacher_classroom()


if __name__ == "__main__":
    main()
