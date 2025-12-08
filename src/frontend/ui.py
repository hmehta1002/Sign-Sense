import streamlit as st

try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except:
    TTS_AVAILABLE = False


def transform_dyslexia(text: str):
    spacing = "  ".join(text)
    return spacing


def animate(text):
    return f"<p style='animation:pulse 1.2s infinite;color:#00f2ff;font-size:22px;'>{text}</p>"


def render_header(mode):
    st.markdown(
        f"""
        <h1 style="text-align:center;
        background:linear-gradient(90deg,#f0f,#0ff);
        -webkit-background-clip:text;color:transparent;
        font-size:50px;">SignSense</h1>
        <p style='text-align:center;color:#aaa;'>Mode: <b>{mode}</b></p>
        """, unsafe_allow_html=True
    )


def render_mode_selection():
    st.subheader("Choose Learning Mode")
    return st.radio("",
        ["Standard","Dyslexia","ADHD Hybrid","ISL Mode"],
        horizontal=True
    )


def render_subject_selection():
    st.subheader("Choose Subject")
    return st.radio("",["Mathematics","English"],horizontal=True)


def render_question(q, mode, current_index, total, timer_value=None):
    st.markdown(f"### Question {current_index}/{total}")

    question_text = q["question"]

    if mode == "Dyslexia":
        question_text = transform_dyslexia(question_text)

    if mode == "ADHD Hybrid":
        st.markdown(animate(question_text), unsafe_allow_html=True)
    else:
        st.markdown(f"**{question_text}**")

    if mode == "ISL Mode":
        if q.get("isl_gif"):
            st.image(q["isl_gif"])
        if q.get("isl_video"):
            st.video(q["isl_video"])

    selected = st.radio("Answer:", q["options"])
    return selected


def render_results(engine):
    st.success("🎉 Quiz Completed!")
    st.metric("Final Score", engine.score)
    st.metric("Best Streak", engine.best_streak)
