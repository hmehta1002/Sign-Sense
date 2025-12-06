import streamlit as st
from typing import Optional

# ------------- CONSTANTS -------------

DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"

AVATAR_NEUTRAL = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"
AVATAR_THINKING = "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"
AVATAR_HAPPY = "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"


# ------------- THEME & STYLE -------------

def _apply_neon_theme():
    """Global neon cyber theme (background, typography, cards)."""
    css = """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #4c1d95 0, #020617 45%, #000000 100%);
        color: #f9fafb;
    }

    /* Center main content area */
    .main > div {
        max-width: 980px;
        margin: 0 auto;
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }

    /* Neon header */
    .neon-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f97316, #e11d48, #6366f1, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .neon-subtitle {
        font-size: 0.95rem;
        color: #e5e7eb;
        opacity: 0.9;
        margin-top: 0.35rem;
    }

    .hero-card {
        border-radius: 20px;
        padding: 1.4rem 1.6rem;
        background: radial-gradient(circle at top left, rgba(251,113,133,0.35), rgba(15,23,42,0.96));
        border: 1px solid rgba(129,140,248,0.7);
        box-shadow: 0 0 28px rgba(129,140,248,0.45);
    }

    /* Avatar */
    .avatar {
        width: 96px;
        height: 96px;
        border-radius: 999px;
        border: 2px solid rgba(244,114,182,0.9);
        box-shadow: 0 0 26px rgba(244,114,182,0.7);
        object-fit: cover;
        margin: 0.3rem auto 0.4rem auto;
        display: block;
    }

    /* Mode card */
    .mode-card {
        border-radius: 16px;
        padding: 0.9rem 1rem;
        background: linear-gradient(145deg, rgba(24,24,48,0.95), rgba(30,64,175,0.9));
        border: 1px solid rgba(129,140,248,0.7);
        box-shadow: 0 0 18px rgba(59,130,246,0.4);
        margin-top: 0.4rem;
    }
    .mode-title {
        font-weight: 700;
        font-size: 1rem;
    }
    .mode-tag {
        display: inline-block;
        padding: 0.12rem 0.55rem;
        border-radius: 999px;
        font-size: 0.7rem;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.7);
        margin-left: 0.5rem;
    }
    .mode-desc {
        font-size: 0.8rem;
        color: #e5e7eb;
        margin-top: 0.35rem;
    }

    /* Question card */
    .question-card {
        margin-top: 0.8rem;
        border-radius: 18px;
        padding: 1.1rem 1.4rem;
        background: radial-gradient(circle at top left, rgba(59,130,246,0.35), rgba(15,23,42,0.96));
        border: 1px solid rgba(96,165,250,0.8);
        box-shadow: 0 0 20px rgba(59,130,246,0.45);
    }
    .question-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #bfdbfe;
    }
    .question-text {
        margin-top: 0.45rem;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Option styling (radio labels) */
    div[role="radiogroup"] > label {
        background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(30,64,175,0.9));
        border-radius: 12px;
        border: 1px solid rgba(148,163,246,0.7);
        padding: 0.45rem 0.75rem;
        margin-bottom: 0.4rem;
        transition: all 0.16s ease-out;
    }
    div[role="radiogroup"] > label:hover {
        border-color: rgba(251,113,133,0.9);
        box-shadow: 0 0 18px rgba(251,113,133,0.6);
        transform: translateY(-1px);
    }

    /* Result card */
    .result-card {
        border-radius: 18px;
        padding: 1.2rem 1.5rem;
        background: radial-gradient(circle at top left, rgba(74,222,128,0.25), rgba(6,78,59,0.95));
        border: 1px solid rgba(74,222,128,0.85);
        box-shadow: 0 0 24px rgba(34,197,94,0.55);
    }

    .metric-chip {
        display: inline-block;
        margin: 0.2rem 0.3rem 0 0;
        padding: 0.16rem 0.6rem;
        border-radius: 999px;
        font-size: 0.74rem;
        background: rgba(15,23,42,0.8);
        border: 1px solid rgba(148,163,184,0.7);
    }

    /* Dyslexia spacing class */
    .dyslexia-text {
        letter-spacing: 0.12em !important;
        word-spacing: 0.20em !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _mode_description(mode: str) -> str:
    if mode == "Standard":
        return "Balanced layout with normal pacing and visuals."
    if mode == "ADHD-Friendly":
        return "Reduced clutter, bigger tap targets, and calmer pacing (no visible timer)."
    if mode == "Dyslexia-Friendly":
        return "Extra spacing, optional overlays, and dyslexia-aware typography."
    if mode == "Autism-Friendly":
        return "Low-stimulation visuals, predictable navigation, and no surprise animations."
    if mode == "Deaf/ISL Mode":
        return "Indian Sign Language mode with signing avatar support and visual-first guidance."
    return ""


def _choose_overlay(mode: str) -> Optional[str]:
    if mode != "Dyslexia-Friendly":
        return None
    overlay = st.selectbox(
        "Reading comfort overlay (Dyslexia mode):",
        ["None", "Blue", "Yellow", "Green"],
    )
    mapping = {
        "Blue": "#1e293b77",
        "Yellow": "#facc1577",
        "Green": "#22c55e66",
    }
    return mapping.get(overlay, None)


def _avatar_for_state(score: int, history_len: int) -> str:
    if history_len == 0 or score == 0:
        return AVATAR_NEUTRAL
    avg = score / history_len
    if avg < 1.2:
        return AVATAR_THINKING
    return AVATAR_HAPPY


def _apply_dyslexia_font_if_needed(mode: str):
    if mode == "Dyslexia-Friendly":
        st.markdown(
            f'<link href="{DYSLEXIA_FONT_URL}" rel="stylesheet">',
            unsafe_allow_html=True,
        )


# ------------- PUBLIC UI FUNCTIONS (USED BY app.py) -------------


def render_header():
    """Top hero section."""
    _apply_neon_theme()

    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        st.markdown(
            "<div class='hero-card'>"
            "<div class='neon-title'>SignSense</div>"
            "<div class='neon-subtitle'>Neon cyber learning hub with ADHD, Dyslexia, Autism, and ISL support.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(f"<img src='{AVATAR_NEUTRAL}' class='avatar'>", unsafe_allow_html=True)


def render_mode_selection() -> str:
    """Mode selection screen."""
    st.subheader("Select Your Accessibility Mode")

    modes = [
        "Standard",
        "ADHD-Friendly",
        "Dyslexia-Friendly",
        "Autism-Friendly",
        "Deaf/ISL Mode",
    ]

    mode = st.radio(
        "Choose the mode that best matches your learning style:",
        modes,
        index=modes.index("Standard"),
    )

    st.markdown(
        "<div class='mode-card'>"
        f"<span class='mode-title'>{mode}</span>"
        "<span class='mode-tag'>Accessibility profile</span>"
        f"<div class='mode-desc'>{_mode_description(mode)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    return mode


def render_subject_selection() -> str:
    """Subject selection screen."""
    st.subheader("Choose Your Subject")

    subject_label = st.radio(
        "Pick one subject to begin:",
        ["Mathematics 🧮", "English ✍️"],
        index=0,
    )
    subject = "math" if subject_label.startswith("Mathematics") else "english"

    st.caption("You can restart from home if you want to switch subjects later.")
    return subject


def render_question(question: dict, engine, mode: str):
    """
    Show a single question with:
    - avatar
    - dyslexia overlay if needed
    - ISL GIF / video for Deaf mode
    """
    st.subheader("Active Question")

    overlay_color = _choose_overlay(mode)
    _apply_dyslexia_font_if_needed(mode)

    avatar_url = _avatar_for_state(engine.score, len(engine.history))
    st.markdown(f"<img src='{avatar_url}' class='avatar'>", unsafe_allow_html=True)

    if overlay_color:
        st.markdown(
            f"<div style='background:{overlay_color}; border-radius:18px; padding:0.5rem;'>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='question-card'>"
        f"<div class='question-label'>Difficulty · {question.get('difficulty', 'easy').capitalize()}</div>"
        f"<div class='question-text'>{question['question']}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if overlay_color:
        st.markdown("</div>", unsafe_allow_html=True)

    # Deaf/ISL Mode – show sign media if fields exist
    if mode == "Deaf/ISL Mode":
        st.info("ISL support: signing avatar explanation available for this question.")
        gif_path = question.get("isl_gif")
        video_path = question.get("isl_video")

        if gif_path:
            st.image(gif_path, caption="ISL: Question explanation (looped)")
        if video_path:
            if st.button("🎬 Watch full ISL explanation video"):
                st.video(video_path)

    selected = st.radio("Choose your answer:", question["options"])

    hint_requested = st.checkbox("🧩 Show a gentle hint", value=False)

    return selected, hint_requested


def render_results(engine):
    """Neon cyber results dashboard."""
    st.subheader("Session Summary")

    summary = engine.summary()
    avatar_url = _avatar_for_state(engine.score, len(engine.history))

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(
            f"**Mode:** {engine.mode}  ·  **Subject:** {engine.subject.capitalize()}",
        )
        st.write(
            f"**Weighted score:** {summary['score']}  "
            f"· Approx. performance: **{summary['percentage']:.1f}%**"
        )
        st.write(
            f"Questions answered: **{summary['total_answered']}**, "
            f"Correct: **{summary['correct_answered']}**"
        )

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("**Difficulty breakdown:**", unsafe_allow_html=True)

        for d in ["easy", "medium", "hard"]:
            count = summary["difficulty_counts"][d]
            acc = summary["accuracy_by_difficulty"][d]
            label = d.capitalize()
            if acc is None:
                text = f"{label}: {count} questions"
            else:
                text = f"{label}: {count} questions — {acc*100:.0f}% correct"
            st.markdown(
                f"<span class='metric-chip'>{text}</span>",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<img src='{avatar_url}' class='avatar'>", unsafe_allow_html=True)
        if summary["percentage"] >= 80:
            st.success("High mastery · strong readiness for advanced content.")
        elif summary["percentage"] >= 50:
            st.info("Developing mastery · with a bit more practice, scores can rise quickly.")
        else:
            st.warning("Emerging skills · this is a safe space to keep practising.")

    st.markdown("---")
    st.caption(
        "Roadmap: plug in an ML model in the AI module to drive adaptive difficulty and richer ISL content."
    )

    if st.button("🔁 Restart from Home"):
        st.session_state.page = "home"
        st.session_state.engine = None
        st.session_state.mode = "Standard"
        st.session_state.subject = None
