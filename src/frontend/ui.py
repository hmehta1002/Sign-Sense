import streamlit as st

# ---------- Dyslexia Font Injection (if available) ----------
DYSLEXIA_FONT_URL = "https://fonts.cdnfonts.com/css/opendyslexic"

def apply_global_styles(mode, color_filter):
    base_css = f"""
    <style>
        body {{
            font-family: {'OpenDyslexic' if mode == 'Dyslexia-Friendly' else 'Arial'}, sans-serif;
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

        .option-button {{
            width: 100%;
            background-color: #ececec;
            border: none;
            padding: 14px;
            margin-top: 8px;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            transition: 0.2s;
        }}

        .option-button:hover {{
            background-color: #d7d7d7;
        }}

        .avatar {{
            width: 120px;
            margin: auto;
            display: block;
        }}

        .filter {{
            backdrop-filter: blur(2px) brightness(0.9);
            background-color: {color_filter};
            padding: 10px;
            border-radius: 10px;
        }}
    </style>
    """

    st.markdown(base_css, unsafe_allow_html=True)
    if mode == "Dyslexia-Friendly":
        st.markdown(f'<link href="{DYSLEXIA_FONT_URL}" rel="stylesheet">', unsafe_allow_html=True)


# ---------- AVATAR SYSTEM ----------

def get_avatar(score, index):
    if score == 0 and index == 0:
        return "https://cdn-icons-png.flaticon.com/512/4333/4333609.png"  # neutral
    if score / max(index,1) < 1.2:
        return "https://cdn-icons-png.flaticon.com/512/4333/4333622.png"  # thinking
    return "https://cdn-icons-png.flaticon.com/512/4333/4333625.png"      # happy


# ---------- UI COMPONENTS ----------

def render_header():
    st.title("SignSense")
    st.caption("Adaptive, Accessible Learning Platform")


def render_mode_selection():
    return st.radio(
        "Select learning accessibility mode:",
        ["Standard", "ADHD-Friendly", "Dyslexia-Friendly", "Autism-Friendly"]
    )


def render_subject_selection():
    return st.radio("Choose subject:", ["math", "english"])


def render_question(question, mode, score, index):
    color_filter = None
    if mode == "Dyslexia-Friendly":
        overlay = st.selectbox(
            "Reading Assistance Tint:",
            ["None", "Blue Overlay", "Yellow Overlay", "Green Overlay"]
        )
        color_filter = {"Blue Overlay": "#d7eaff", "Yellow Overlay": "#fff9c4", "Green Overlay": "#dbffda"}.get(overlay, None)

    apply_global_styles(mode, color_filter)

    # Avatar display
    avatar_url = get_avatar(score, index)
    st.markdown(f'<img src="{avatar_url}" class="avatar">', unsafe_allow_html=True)

    st.markdown(f"<div class='question-box'>{question['question']}</div>", unsafe_allow_html=True)

    return st.radio("Select an answer:", question["options"])


def render_results(engine):
    st.success("🎉 Quiz Completed!")
    st.write(f"Score: **{engine.score}**")
    st.write(f"Mode: **{engine.mode}**")
    st.write(f"Subject: **{engine.subject}**")

    avatar_url = get_avatar(engine.score, len(engine.questions))
    st.markdown(f'<img src="{avatar_url}" class="avatar">', unsafe_allow_html=True)

    if st.button("Restart"):
        st.session_state.page = "home"
