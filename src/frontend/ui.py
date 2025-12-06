import streamlit as st

DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"

AVATAR_NEUTRAL = "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"
AVATAR_THINKING = "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"
AVATAR_HAPPY = "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"


def _apply_global_styles(mode: str, overlay_color: str | None):
    base_css = f"""
    <style>
        body {{
            font-family: {'OpenDyslexic' if mode == 'Dyslexia-Friendly' else 'system-ui'}, sans-serif;
            color: #222;
        }}
        .question-box {{
            background-color: #ffffff;
            padding: 18px;
            border-radius: 10px;
            margin-top: 10px;
            font-size: 20px;
            line-height: 1.4;
            {"letter-spacing: 0.12em; word-spacing: 0.15em;" if mode == "Dyslexia-Friendly" else ""}
        }}
        .avatar {{
            width: 110px;
            margin: 0 auto 8px auto;
            display: block;
        }}
        .filter-wrapper {{
            padding: 10px;
            border-radius: 10px;
            background-color: %s;
        }}
    </style>
    """ % (overlay_color if overlay_color else "transparent")

    st.markdown(base_css, unsafe_allow_html=True)
    if mode == "Dyslexia-Friendly":
        st.markdown(
            f'<link href="{DYSLEXIA_FONT_URL}" rel="stylesheet">',
            unsafe_allow_html=True,
        )


def _mode_description(mode: str) -> str:
    if mode == "Standard":
        return "Balanced layout with normal pacing and visuals."
    if mode == "ADHD-Friendly":
        return "Larger tap targets, minimal clutter, and no visible timer."
    if mode == "Dyslexia-Friendly":
        return "Adjusted spacing, optional color overlays, and dyslexia-aware formatting."
    if mode == "Autism-Friendly":
        return "Low-stimulation visuals, predictable navigation, no flashing or timers."
    return ""


def render_header():
    st.title("SignSense")
    st.caption("Neurodiversity-aware adaptive quiz platform with assistive and gamified features.")


def render_mode_selection() -> str:
    st.subheader("Select Learning Mode")
    mode = st.radio(
        "Choose the mode that best matches your learning style:",
        ["Standard", "ADHD-Friendly", "Dyslexia-Friendly", "Autism-Friendly"],
    )
    st.info(_mode_description(mode))
    return mode


def render_subject_selection() -> str:
    st.subheader("Choose Subject")
    subject_label = st.radio("Select a quiz:", ["Mathematics", "English"])
    return "math" if subject_label == "Mathematics" else "english"


def _choose_overlay(mode: str) -> str | None:
    if mode != "Dyslexia-Friendly":
        return None
    overlay = st.selectbox(
        "Reading comfort overlay (for dyslexia support):",
        ["None", "Blue", "Yellow", "Green"],
    )
    mapping = {
        "Blue": "#d7eaff",
        "Yellow": "#fff9c4",
        "Green": "#dbffda",
    }
    return mapping.get(overlay, None)


def _avatar_for_state(score: int, history_len: int) -> str:
    if history_len == 0 or score == 0:
        return AVATAR_NEUTRAL
    avg = score / history_len
    if avg < 1.2:
        return AVATAR_THINKING
    return AVATAR_HAPPY


def render_question(question: dict, engine, mode: str):
    st.subheader("Question")

    overlay_color = _choose_overlay(mode)
    _apply_global_styles(mode, overlay_color)

    avatar_url = _avatar_for_state(engine.score, len(engine.history))
    st.markdown(f"<img src='{avatar_url}' class='avatar'>", unsafe_allow_html=True)

    if overlay_color:
        st.markdown("<div class='filter-wrapper'>", unsafe_allow_html=True)

    st.markdown(f"<div class='question-box'>{question['question']}</div>", unsafe_allow_html=True)

    selected = st.radio("Select your answer:", question["options"])

    if overlay_color:
        st.markdown("</div>", unsafe_allow_html=True)

    hint_requested = st.checkbox("I want a small hint", value=False)
    return selected, hint_requested


def render_results(engine):
    st.subheader("Quiz Summary")

    summary = engine.summary()
    st.write(f"Total questions answered: **{summary['total_answered']}**")
    st.write(f"Weighted score: **{summary['score']}**")
    st.write(f"Approximate performance: **{summary['percentage']:.1f}%**")

    easy = summary["difficulty_counts"]["easy"]
    med = summary["difficulty_counts"]["medium"]
    hard = summary["difficulty_counts"]["hard"]

    st.markdown("**Difficulty distribution:**")
    st.write(f"- Easy questions seen: {easy}")
    st.write(f"- Medium questions seen: {med}")
    st.write(f"- Hard questions seen: {hard}")

    st.markdown("---")
    if summary["percentage"] >= 80:
        st.success("Performance band: High. Strong understanding demonstrated. Your avatar is proud of you! ⭐")
    elif summary["percentage"] >= 50:
        st.info("Performance band: Moderate. You are making good progress. A few more tries will push you higher.")
    else:
        st.warning("Performance band: Emerging. This is a safe space to practice. Let's treat this as a warm-up round.")

    if st.button("Restart from home"):
        st.session_state.page = "home"
        st.session_state.engine = None
        st.session_state.mode = "Standard"
        st.session_state.subject = None
