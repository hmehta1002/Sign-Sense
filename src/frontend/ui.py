import streamlit as st
from typing import Optional

# ----------------- CONSTANTS -----------------

DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"

AVATAR_NEUTRAL = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"
AVATAR_THINKING = "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"
AVATAR_HAPPY = "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"


# ----------------- GLOBAL THEME -----------------

def _apply_neon_theme():
    css = """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #4c1d95 0%, #000814 60%, #000000 100%);
        color: white;
    }

    .main > div {
        max-width: 950px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 1rem;
    }

    /* Title */
    .neon-title {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f5ff, #bc13fe, #ff0080);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        letter-spacing: 0.15em;
    }

    /* Neon subtitle */
    .neon-subtitle {
        font-size: 1rem;
        opacity: 0.8;
    }

    /* Header card */
    .hero-card {
        padding: 20px;
        border-radius: 20px;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0,255,255,0.35);
        box-shadow: 0 0 25px rgba(0,255,255,0.4);
    }

    .avatar {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        margin-top: 10px;
        border: 2px solid #00eaff;
        box-shadow: 0px 0px 20px rgba(0,255,255,0.6);
    }

    /* Radio Buttons (Options) */
    div[role="radiogroup"] > label {
        background: rgba(15,23,42,0.7);
        border-radius: 14px;
        padding: 12px;
        font-size: 18px;
        border: 2px solid rgba(0,255,255,0.3);
        transition: 0.25s;
        cursor: pointer;
    }

    div[role="radiogroup"] > label:hover {
        border-color: #00eaff;
        box-shadow: 0 0 15px rgba(0,255,255,0.4);
        transform: scale(1.02);
    }

    /* Question Card */
    .question-card {
        margin-top: 20px;
        padding: 18px;
        border-radius: 18px;
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(12px);
        border: 2px solid rgba(0,255,255,0.4);
        box-shadow: 0 0 22px rgba(0,255,255,0.5);
    }

    .question-text {
        font-size: 1.5rem;
        font-weight: 600;
        text-shadow: 0px 0px 8px rgba(0,255,255,0.7);
    }

    /* Submit Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00eaff, #6a00ff);
        border-radius: 10px;
        color: black;
        font-weight: bold;
        border: none;
        font-size: 18px;
        padding: 12px;
        transition: 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 20px rgba(0,255,255,0.8);
    }

    /* 3D Avatar Deaf Mode Container */
    .avatar-3d-box {
        width: 250px;
        height: 250px;
        border-radius: 18px;
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(12px);
        margin: auto;
        border: 2px solid rgba(0,255,255,0.4);
        box-shadow: 0 0 22px rgba(0,255,255,0.6);
        margin-bottom: 20px;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ----------------- MODE TEXT -----------------

def _mode_description(mode: str) -> str:
    if mode == "Standard":
        return "Default balanced mode."
    if mode == "ADHD-Friendly":
        return "Simplified UI, reduced distractions."
    if mode == "Dyslexia-Friendly":
        return "Dyslexia font + spacing adjustments."
    if mode == "Autism-Friendly":
        return "Low-stimulation predictable layout."
    if mode == "Deaf/ISL Mode":
        return "Indian Sign Language support with animated signing avatar."
    return ""


# ----------------- HELPERS -----------------

def _choose_overlay(mode: str) -> Optional[str]:
    if mode != "Dyslexia-Friendly":
        return None

    overlay = st.selectbox("Choose overlay color for readability:", ["None", "Blue", "Yellow", "Green"])
    mapping = {
        "Blue": "#60a5fa55",
        "Yellow": "#facc1555",
        "Green": "#22c55e55",
    }
    return mapping.get(overlay, None)


def _avatar_for_state(score: int, history_len: int) -> str:
    if history_len == 0 or score == 0:
        return AVATAR_NEUTRAL
    avg = score / history_len
    if avg < 1.2:
        return AVATAR_THINKING
    return AVATAR_HAPPY


# ----------------- UI COMPONENTS -----------------

def render_header():
    _apply_neon_theme()

    col1, col2 = st.columns([2.5, 1.2])
    with col1:
        st.markdown(
            f"""
            <div class='hero-card'>
                <div class='neon-title'>SignSense</div>
                <div class='neon-subtitle'>Adaptive AI learning for neurodiverse and Deaf learners.</div>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(f"<img src='{AVATAR_NEUTRAL}' class='avatar'>", unsafe_allow_html=True)


def render_mode_selection() -> str:
    st.subheader("Select Learning Mode:")

    modes = ["Standard", "ADHD-Friendly", "Dyslexia-Friendly", "Autism-Friendly", "Deaf/ISL Mode"]

    mode = st.radio("Choose mode:", modes, index=0)

    st.info(_mode_description(mode))
    return mode


def render_subject_selection() -> str:
    st.subheader("Choose Subject")
    choice = st.radio("Subject:", ["Mathematics 🧮", "English ✍️"])
    return "math" if "Math" in choice else "english"


def render_question(question: dict, engine, mode: str):
    st.subheader("Question:")

    overlay = _choose_overlay(mode)

    avatar = _avatar_for_state(engine.score, len(engine.history))
    st.markdown(f"<img src='{avatar}' class='avatar'>", unsafe_allow_html=True)

    # WRAP QUESTION
    if overlay:
        st.markdown(f"<div style='background:{overlay};padding:10px;border-radius:12px;'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='question-card'>
            <div class='question-text'>{question["question"]}</div>
        </div>
        """, unsafe_allow_html=True
    )

    if overlay:
        st.markdown("</div>", unsafe_allow_html=True)

    # 🧏 Deaf/ISL Mode UI
    if mode == "Deaf/ISL Mode":
        st.markdown("<h4>🧏 ISL Explanation Mode</h4>", unsafe_allow_html=True)
        st.markdown("<div class='avatar-3d-box'></div>", unsafe_allow_html=True)

        if st.button("👋 Show Sign (GIF)"):
            st.image(question.get("isl_gif"))

        if st.button("🎬 Full Video Explanation"):
            if question.get("isl_video"):
                st.video(question["isl_video"])

        if st.button("🔁 Replay"):
            st.success("Replay feature will loop signing animations.")

    selected = st.radio("Choose your answer:", question["options"])
    hint = st.checkbox("🧩 Show hint")

    return selected, hint


def render_results(engine):
    summary = engine.summary()
    avatar = _avatar_for_state(engine.score, len(engine.history))

    st.subheader("Results Summary")
    st.markdown(f"<img src='{avatar}' class='avatar'>", unsafe_allow_html=True)

    st.write(f"Score: **{summary['percentage']}%** ({summary['score']} points)")
    st.write(f"Correct answers: **{summary['correct_answered']} / {summary['total_answered']}**")

    if st.button("🔁 Restart"):
        st.session_state.page = "home"
        st.session_state.engine = None
