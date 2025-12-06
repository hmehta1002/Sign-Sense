import streamlit as st

from typing import Optional

# ---------- CONSTANTS ----------

DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"

AVATAR_NEUTRAL = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"
AVATAR_THINKING = "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"
AVATAR_HAPPY = "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"


# ---------- THEME & STYLE ----------

def _apply_neon_theme():
    """Inject global neon cyberpunk-style CSS for the whole app."""
    css = """
    <style>
        /* App background */
        .stApp {
            background: radial-gradient(circle at top left, #301E67 0, #130828 35%, #050109 100%);
            color: #f8f9ff;
        }

        /* Center main block and give it a max width */
        .main > div {
            max-width: 980px;
            margin: 0 auto;
            padding-top: 1.4rem;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1b1438 0, #050318 100%);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        section[data-testid="stSidebar"] .css-1d391kg {
            padding-top: 1.2rem;
        }

        /* Neon title */
        .neon-title {
            font-size: 2.4rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ff6bd5, #54ffe5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.08em;
        }

        .neon-subtitle {
            font-size: 0.98rem;
            color: #d8d9ff;
            opacity: 0.9;
        }

        /* Hero card */
        .hero-card {
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            background: radial-gradient(circle at top left, rgba(138,87,255,0.35), rgba(8,9,37,0.9));
            border: 1px solid rgba(137, 96, 255, 0.7);
            box-shadow: 0 0 24px rgba(116, 76, 255, 0.35);
        }

        /* Mode cards */
        .mode-card {
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.6rem;
            background: linear-gradient(145deg, rgba(20,15,55,0.95), rgba(39,20,89,0.9));
            border: 1px solid rgba(123, 97, 255, 0.6);
            cursor: pointer;
            transition: all 0.18s ease-out;
        }
        .mode-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 18px rgba(123, 97, 255, 0.7);
        }
        .mode-title {
            font-weight: 700;
            font-size: 0.98rem;
        }
        .mode-tag {
            display: inline-block;
            padding: 0.08rem 0.5rem;
            border-radius: 999px;
            font-size: 0.66rem;
            background: rgba(255,255,255,0.08);
            margin-left: 0.35rem;
        }
        .mode-desc {
            font-size: 0.8rem;
            color: #d5d6ff;
            margin-top: 0.25rem;
        }

        /* Question container */
        .question-card {
            margin-top: 0.8rem;
            border-radius: 18px;
            padding: 1.2rem 1.4rem;
            background: radial-gradient(circle at top left, rgba(98,83,238,0.3), rgba(9,7,30,0.9));
            border: 1px solid rgba(129, 140, 248, 0.7);
            box-shadow: 0 0 18px rgba(88, 28, 135, 0.45);
        }
        .question-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #a5b4fc;
        }
        .question-text {
            margin-top: 0.4rem;
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* Options styling */
        div[role="radiogroup"] > label {
            background: linear-gradient(135deg, rgba(24,20,68,0.98), rgba(55,0,88,0.9));
            border-radius: 12px;
            margin-bottom: 0.35rem;
            padding: 0.45rem 0.75rem;
            border: 1px solid rgba(148, 163, 255, 0.4);
            transition: all 0.15s ease-out;
        }
        div[role="radiogroup"] > label:hover {
            border-color: rgba(244,114,182,0.8);
            box-shadow: 0 0 16px rgba(244,114,182,0.4);
        }

        /* Avatar */
        .avatar {
            width: 96px;
            height: 96px;
            border-radius: 50%;
            border: 2px solid rgba(244,114,182,0.8);
            box-shadow: 0 0 22px rgba(244,114,182,0.75);
            margin: 0.4rem auto 0.6rem auto;
            display: block;
            object-fit: cover;
        }

        /* Result badges */
        .result-card {
            border-radius: 18px;
            padding: 1.3rem 1.4rem;
            background: radial-gradient(circle at top left, rgba(52,211,153,0.15), rgba(9,16,32,0.96));
            border: 1px solid rgba(52,211,153,0.7);
            box-shadow: 0 0 22px rgba(16,185,129,0.55);
        }

        .metric-chip {
            display: inline-block;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            padding: 0.16rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            background: rgba(15,23,42,0.8);
            border: 1px solid rgba(148,163,184,0.7);
        }

        /* Dyslexia spacing */
        .dyslexia-text {
            letter-spacing: 0.12em !important;
            word-spacing: 0.18em !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def _apply_dyslexia_font_if_needed(mode: str):
    if mode == "Dyslexia-Friendly":
        st.markdown(
            f'<link href="{DYSLEXIA_FONT_URL}" rel="stylesheet">',
            unsafe_allow_html=True,
        )


# ---------- MODE HELPERS ----------

def _mode_description(mode: str) -> str:
    if mode == "Standard":
        return "Balanced layout, visible pacing, and default visuals."
    if mode == "ADHD-Friendly":
        return "Reduced clutter, larger tap targets, and calmer pacing (no timer)."
    if mode == "Dyslexia-Friendly":
        return "Adjusted spacing, optional color overlays, and dyslexia-aware text."
    if mode == "Autism-Friendly":
        return "Low-stimulation visuals, predictable flow, and no surprise animations."
    if mode == "Deaf/ISL Mode":
        return "Indian Sign Language mode with signing avatar support and visual-first prompts."
    return ""


def _choose_overlay(mode: str) -> Optional[str]:
    if mode != "Dyslexia-Friendly":
        return None
    overlay = st.selectbox(
        "Reading comfort overlay (for Dyslexia mode):",
        ["None", "Blue", "Yellow", "Green"],
    )
    mapping = {
        "Blue": "#1e293b55",
        "Yellow": "#facc1555",
        "Green": "#22c55e40",
    }
    return mapping.get(overlay, None)


def _avatar_for_state(score: int, history_len: int) -> str:
    if history_len == 0 or score == 0:
        return AVATAR_NEUTRAL
    avg = score / history_len
    if avg < 1.2:
        return AVATAR_THINKING
    return AVATAR_HAPPY


# ---------- PUBLIC UI FUNCTIONS (USED BY app.py) ----------

def render_header():
    """Top hero header with neon style."""
    _apply_neon_theme()

    col1, col2 = st.columns([2.5, 1.5])
    with col1:
        st.markdown(
            "<div class='hero-card'>"
            "<div class='neon-title'>SignSense</div>"
            "<div class='neon-subtitle'>Neurodiversity-aware, ISL-ready adaptive quiz space.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<img src='{AVATAR_NEUTRAL}' class='avatar'>",
            unsafe_allow_html=True,
        )


def render_mode_selection() -> str:
    """Mode selection with cyber cards."""
    st.subheader("Choose Your Learning Environment")

    modes = [
        "Standard",
        "ADHD-Friendly",
        "Dyslexia-Friendly",
        "Autism-Friendly",
        "Deaf/ISL Mode",
    ]

    # Use radio for state, but the CSS makes it feel card-like
    mode = st.radio(
        "Select a mode (you can always change later):",
        modes,
        label_visibility="collapsed"
    )

    st.markdown(
        f"<div class='mode-card'>"
        f"<span class='mode-title'>{mode}</span>"
        f"<span class='mode-tag'>Accessibility profile</span>"
        f"<div class='mode-desc'>{_mode_description(mode)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    return mode


def render_subject_selection() -> str:
    """Subject selection (Math / English) with neon style."""
    st.subheader("Select a Subject")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Mathematics 🧮")
        math_selected = st.radio(
            "Math_radio",
            ["Math"],
            label_visibility="collapsed",
            key="math_subject_radio",
        )
    with col2:
        st.markdown("#### English ✍️")
        eng_selected = st.radio(
            "Eng_radio",
            ["English"],
            label_visibility="collapsed",
            key="eng_subject_radio",
        )

    # Simple toggle: if user clicked Math radio last, choose math; else english.
    # To avoid confusion, just show a combined radio below:
    subject_label = st.radio(
        "Final subject selection:",
        ["Mathematics", "English"],
        index=0,
    )
    subject = "math" if subject_label == "Mathematics" else "english"

    st.caption("You can switch subjects anytime by restarting from the home screen.")
    return subject


def render_question(question: dict, engine, mode: str):
    """Show one question with avatar, overlays, and optional ISL media."""
    st.subheader("Active Question")

    # Dyslexia overlays
    overlay_color = _choose_overlay(mode)
    _apply_dyslexia_font_if_needed(mode)

    # Avatar state
    avatar_url = _avatar_for_state(engine.score, len(engine.history))
    st.markdown(f"<img src='{avatar_url}' class='avatar'>", unsafe_allow_html=True)

    # Wrap question in card + overlay if needed
    if overlay_color:
        st.markdown(
            f"<div style='background:{overlay_color}; border-radius:18px; padding:0.4rem;'>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='question-card'>"
        f"<div class='question-label'>Difficulty: {question.get('difficulty','easy').capitalize()}</div>"
        f"<div class='question-text'>{question['question']}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if overlay_color:
        st.markdown("</div>", unsafe_allow_html=True)

    # ISL media for Deaf mode
    if mode == "Deaf/ISL Mode":
        st.info("Indian Sign Language (ISL) support is enabled for this session.")
        gif_path = question.get("isl_gif")
        video_path = question.get("isl_video")

        if gif_path:
            st.image(gif_path, caption="ISL: Question explanation (looped)")
        if video_path:
            if st.button("🎬 Watch full ISL explanation video"):
                st.video(video_path)

    # Options
    selected = st.radio("Choose your answer:", question["options"])

    # Hints – same for now, but could be mode-specific later
    hint_requested = st.checkbox("🧩 Show a gentle hint", value=False)

    return selected, hint_requested


def render_results(engine):
    """Neon-style result dashboard."""
    st.subheader("Session Summary")

    summary = engine.summary()
    avatar_url = _avatar_for_state(engine.score, len(engine.history))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(
            f"**Mode:** {engine.mode}  |  **Subject:** {engine.subject.capitalize()}"
        )
        st.write(
            f"**Weighted score:** {summary['score']}  "
            f"— Approx. performance: **{summary['percentage']:.1f}%**"
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
            st.markdown(f"<span class='metric-chip'>{text}</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<img src='{avatar_url}' class='avatar'>", unsafe_allow_html=True)
        if summary["percentage"] >= 80:
            st.success("High mastery ✔\n\nGreat job — this learner is ready for advanced content.")
        elif summary["percentage"] >= 50:
            st.info("Developing mastery 🌱\n\nWith a bit more practice, scores can improve quickly.")
        else:
            st.warning("Emerging skills ✨\n\nThis mode can be used for repeated safe practice.")

    st.markdown("---")
    st.caption(
        "Roadmap: plug-in ML model for adaptive difficulty & richer ISL content library in the AI module."
    )

    if st.button("🔁 Restart from Home"):
        st.session_state.page = "home"
        st.session_state.engine = None
        st.session_state.mode = "Standard"
        st.session_state.subject = None
