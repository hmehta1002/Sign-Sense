import streamlit as st
from streamlit_extras.let_it_rain import rain

try:
    from gtts import gTTS
    TTS_READY = True
except:
    TTS_READY = False


AVATAR = {
    "standard": "https://i.imgur.com/1X01Jmw.jpeg",
    "dyslexia": "https://i.imgur.com/dF982hU.jpeg",
    "adhd": "https://i.imgur.com/v4wO2oB.jpeg",
    "isl": "https://i.imgur.com/PMQdhmI.jpeg",
}


def apply_theme():
    st.markdown("""
    <style>
    body { background:#0b0f1f; }
    .question {
        padding:18px;
        background:rgba(255,255,255,0.06);
        border:1px solid #4dd2ff;
        border-radius:12px;
        margin-bottom:12px;
        font-size:18px;
        color:white;
    }
    label, div, p { color:white !important; }
    </style>
    """, unsafe_allow_html=True)


def render_header(mode):
    apply_theme()
    col1, col2 = st.columns([1,3])

    with col1:
        st.image(AVATAR[mode], caption=f"{mode.upper()} Mode")

    with col2:
        st.markdown(f"<h1 style='color:#4dd2ff'>SignSense</h1>", unsafe_allow_html=True)


def render_mode_picker():
    apply_theme()
    mode = st.radio("Choose Mode:", ["standard", "dyslexia", "adhd", "isl"])
    if st.button("Continue"):
        st.session_state.mode = mode


def render_subject_picker():
    apply_theme()
    subject = st.radio("Choose Subject:", ["math", "english"])
    if st.button("Start"):
        st.session_state.subject = subject


def _tts(txt, id):
    if not TTS_READY:
        st.warning("TTS unavailable here.")
        return
    speech = gTTS(txt)
    path = f"/tmp/{id}.mp3"
    speech.save(path)
    st.audio(path)


def render_question(q, mode, index, total):
    apply_theme()

    st.markdown(f"<div class='question'>({index}/{total}) {q['question']}</div>", unsafe_allow_html=True)

    if mode == "isl" and q.get("isl_video"):
        st.video(q["isl_video"])

    ans = st.radio("Select:", q["options"])

    if st.button("🔊 Speak Question"):
        _tts(q.get("tts_text", q["question"]), q["id"])

    if mode == "adhd":
        rain(emoji="⚡", font_size=20, falling_speed=2, animation_length=1)

    return ans


def render_results(engine):
    apply_theme()
    st.success("🎉 Quiz Finished!")
    st.write(f"Score: **{engine.score}**")
    rain(emoji="🎉", font_size=30, falling_speed=2, animation_length=4)
