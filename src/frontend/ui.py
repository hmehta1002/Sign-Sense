import streamlit as st
from typing import Optional

# ----------------- CONSTANTS -----------------

DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"
AVATAR_NEUTRAL = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"
AVATAR_THINKING = "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"
AVATAR_HAPPY = "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"


# ----------------- GLOBAL THEME -----------------

def _apply_neon_theme():
    st.markdown("""
    <style>

    /* EVERYTHING WHITE */
    * {
        color: #ffffff !important;
    }

    /* Background */
    .stApp {
        background: radial-gradient(circle at top left, #4c1d95 0%, #000814 60%, #000000 100%) !important;
    }

    /* Max Width */
    .main > div {
        max-width: 950px;
        margin: auto;
        padding-top: 1.2rem;
    }

    /* Header */
    .hero-card {
        padding: 20px;
        border-radius: 20px;
        background: rgba(255,255,255,0.08);
        border: 2px solid rgba(0,255,255,0.4);
        box-shadow: 0 0 25px rgba(0,255,255,0.4);
    }
    .neon-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f5ff, #bc13fe, #ff0080);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 0.2em;
    }

    /* Radio Button Cards */
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 14px;
        padding: 12px;
        font-size: 18px;
        border: 2px solid rgba(0,255,255,0.25);
        transition: 0.25s;
        margin-bottom: 10px;
        width: 250px;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #00eaff !important;
        box-shadow: 0 0 15px rgba(0,255,255,0.4);
        transform: translateX(4px);
    }

    /* Selected radio button glow */
    div[role="radiogroup"] > label:has(input:checked) {
        border-color: #ff00ff !important;
        box-shadow: 0 0 22px rgba(255,0,255,0.8);
    }

    /* Question Box */
    .question-card {
        background: rgba(255,255,255,0.08);
        padding: 18px;
        border-radius: 16px;
        border: 2px solid rgba(0,255,255,0.35);
        box-shadow: 0 0 24px rgba(0,255,255,0.4);
        margin-top: 15px;
    }
    .question-text {
        font-size: 1.6rem;
        font-weight: 700;
        text-shadow: 0px 0px 10px rgba(0,255,255,0.7);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00eaff, #8b5cf6);
        border-radius: 10px;
        color: black !important;
        font-size: 16px;
        font-weight: 700;
        width: 260px;
        border: none;
        padding: 12px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(0,255,255,0.9);
    }

    /* Deaf/ISL Avatar */
    .avatar-3d-box {
        width: 260px;
        height: 260px;
        background: rgba(255,255,255,0.08);
        margin: auto;
        border-radius: 16px;
        border: 2px solid rgba(0,255,255,0.4);
        box-shadow: 0 0 30px rgba(0,255,255,0.6);
        margin-bottom: 14px;
    }

    /* Avatar mood bubble */
    .avatar {
        width: 90px;
        height: 90px;
        display: block;
        margin: auto;
        margin-top: 10px;
        border-radius: 50%;
        border: 2px solid #00eaff;
        box-shadow: 0 0 22px rgba(0,255,255,0.6);
    }
    
    </style>
    """, unsafe_allow_html=True)


# ----------------- MODE TEXT -----------------

def _mode_description(mode: str) -> str:
    return {
        "Standard": "Balanced learning with full features.",
        "ADHD-Friendly": "Reduced distractions · calmer pacing.",
        "Dyslexia-Friendly": "Readable fonts · spacing overlays.",
        "Autism-Friendly": "Minimal changes · stable UX.",
        "Deaf/ISL Mode": "Sign Language avatars and visual-first learning.",
    }.get(mode, "")


# ----------------- HELPERS -----------------

def _choose_overlay(mode: str) -> Optional[str]:
    if mode != "Dyslexia-Friendly":
        return None
    overlay = st.selectbox("Overlay color:", ["None", "Blue", "Yellow", "Green"])
    colors = {
        "Blue": "#3b82f655",
        "Yellow": "#facc1555",
        "Green": "#22c55e55",
    }
    return colors.get(overlay, None)


def _avatar_for_state(score: int, history_len: int) -> str:
    if history_len == 0 or score == 0:
        return AVATAR_NEUTRAL
    avg = score / history_len
    return AVATAR_THINKING if avg < 1.2 else AVATAR_HAPPY


# ----------------- UI SCREENS -----------------

def render_header():
    _apply_neon_theme()
    col1, col2 = st.columns([2.3, 1.2])
    with col1:
        st.markdown(f"""
        <div class='hero-card'>
        <div class='neon-title'>SignSense</div>
        <div class='neon-subtitle'>Accessible. Adaptive. AI-Powered.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"<img src='{AVATAR_NEUTRAL}' class='avatar'>", unsafe_allow_html=True)


def render_mode_selection() -> str:
    st.subheader("Learning Mode")
    modes = ["Standard", "ADHD-Friendly", "Dyslexia-Friendly", "Autism-Friendly", "Deaf/ISL Mode"]
    mode = st.radio("Choose:", modes, index=0)
    st.info(_mode_description(mode))
    return mode


def render_subject_selection() -> str:
    st.subheader("Choose Subject")
    choice = st.radio("Subject:", ["Mathematics 🧮", "English ✍️"])
    return "math" if "Math" in choice else "english"


def render_question(question: dict, engine, mode: str):
    st.subheader("Question")

    overlay = _choose_overlay(mode)

    # Avatar mood
    st.markdown(f"<img src='{_avatar_for_state(engine.score, len(engine.history))}' class='avatar'>", unsafe_allow_html=True)

    if overlay:
        st.markdown(f"<div style='background:{overlay};border-radius:12px;padding:10px;'>", unsafe_allow_html=True)

    # Question Card
    st.markdown(f"""
    <div class='question-card'>
        <div class='question-text'>{question["question"]}</div>
    </div>
    """, unsafe_allow_html=True)

    if overlay:
        st.markdown("</div>", unsafe_allow_html=True)

    # Deaf Mode Assets
    if mode == "Deaf/ISL Mode":
        st.markdown("### 🧏 ISL Explanation")
        st.markdown("<div class='avatar-3d-box'></div>", unsafe_allow_html=True)

        if st.button("👋 Show Sign GIF"):
            if question.get("isl_gif"): st.image(question["isl_gif"])

        if st.button("🎬 Full Sign Video"):
            if question.get("isl_video"): st.video(question["isl_video"])

        if st.button("🔁 Repeat"):
            st.success("Replay coming in Final Sprint!")

    selected = st.radio("Answer:", question["options"])
    hint = st.checkbox("🧩 Show hint")
    return selected, hint


def render_results(engine):
    st.subheader("Performance Summary")
    avatar = _avatar_for_state(engine.score, len(engine.history))
    st.markdown(f"<img src='{avatar}' class='avatar'>", unsafe_allow_html=True)

    summary = engine.summary()
    st.write(f"Score: **{summary['percentage']}%**  ({summary['score']} pts)")
    st.write(f"Correct: **{summary['correct_answered']} / {summary['total_answered']}**")

    if st.button("🔁 Restart"):
        st.session_state.page = "home"
        st.session_state.engine = None
