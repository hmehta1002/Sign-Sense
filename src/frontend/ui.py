import streamlit as st
from dataclasses import dataclass


@dataclass
class ModeConfig:
    name: str
    timer_visible: bool
    description: str
    emphasis_text: str
    large_buttons: bool
    dyslexia_font: bool
    low_stimulation: bool


MODE_CONFIGS = {
    "Standard": ModeConfig(
        name="Standard",
        timer_visible=True,
        description="Balanced layout with standard pacing and default visuals.",
        emphasis_text="Recommended for most learners.",
        large_buttons=False,
        dyslexia_font=False,
        low_stimulation=False,
    ),
    "ADHD-Friendly": ModeConfig(
        name="ADHD-Friendly",
        timer_visible=False,
        description="Reduced clutter, larger buttons, and no visible timer.",
        emphasis_text="Designed to lower pressure and support attention.",
        large_buttons=True,
        dyslexia_font=False,
        low_stimulation=False,
    ),
    "Dyslexia-Friendly": ModeConfig(
        name="Dyslexia-Friendly",
        timer_visible=True,
        description="Simplified text, clearer spacing, and dyslexia-friendly formatting.",
        emphasis_text="Designed to support reading comfort and clarity.",
        large_buttons=False,
        dyslexia_font=True,
        low_stimulation=False,
    ),
    "Autism-Friendly": ModeConfig(
        name="Autism-Friendly",
        timer_visible=False,
        description="Low-stimulation layout with predictable navigation and no timer.",
        emphasis_text="Designed to reduce sensory load and anxiety.",
        large_buttons=False,
        dyslexia_font=False,
        low_stimulation=True,
    ),
}


def apply_base_styles():
    """Base styling for the whole app."""
    st.markdown(
        """
        <style>
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            .main > div {
                padding-top: 1.5rem;
                padding-bottom: 1.5rem;
            }
            .question-card {
                padding: 1.25rem 1.5rem;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                background-color: #ffffff;
                margin-bottom: 1.5rem;
            }
            .mode-banner {
                padding: 0.75rem 1rem;
                border-radius: 10px;
                background-color: #f3f4ff;
                border: 1px solid #d4d8ff;
                margin-bottom: 0.75rem;
                font-size: 0.9rem;
            }
            .mode-emphasis {
                font-weight: 600;
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_mode_styles(mode_cfg: ModeConfig):
    """Mode-specific CSS."""
    css_parts = []

    if mode_cfg.large_buttons:
        css_parts.append(
            """
            button[kind="primary"], button[kind="secondary"] {
                font-size: 1.1rem !important;
                padding: 0.9rem 1.1rem !important;
            }
            """
        )

    if mode_cfg.dyslexia_font:
        # This assumes future addition of a dyslexia font; for now, we just tune spacing.
        css_parts.append(
            """
            body, input, textarea, select, button {
                letter-spacing: 0.05em !important;
                word-spacing: 0.12em !important;
            }
            """
        )

    if mode_cfg.low_stimulation:
        css_parts.append(
            """
            .reportview-container, .main, body {
                background-color: #f6f7f8 !important;
            }
            """
        )

    if css_parts:
        st.markdown(
            "<style>" + "\n".join(css_parts) + "</style>",
            unsafe_allow_html=True,
        )


def render_header():
    st.title("SignSense")
    st.caption("Adaptive Quiz Platform for Inclusive Learning")


def render_mode_selection(initial_mode: str | None = None) -> str:
    st.subheader("Select Your Learning Mode")

    if initial_mode is None:
        initial_mode = "Standard"

    mode = st.radio(
        "Choose the option that best matches how you learn:",
        list(MODE_CONFIGS.keys()),
        index=list(MODE_CONFIGS.keys()).index(initial_mode),
    )

    cfg = MODE_CONFIGS[mode]
    st.markdown(
        f"""
        <div class="mode-banner">
            <div><strong>{cfg.name} Mode</strong></div>
            <div>{cfg.description}</div>
            <div class="mode-emphasis">{cfg.emphasis_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    timer_text = (
        "Timer: visible"
        if cfg.timer_visible
        else "Timer: not shown to the learner"
    )
    st.write(f"*{timer_text}*")

    return mode


def render_subject_selection(selected_subject: str | None = None) -> str:
    st.subheader("Choose a subject")

    label = "Mathematics" if selected_subject == "math" else (
        "English" if selected_subject == "english" else "Mathematics"
    )

    subject_label = st.radio("Select a quiz:", ["Mathematics", "English"],
                             index=["Mathematics", "English"].index(label))
    subject = "math" if subject_label == "Mathematics" else "english"

    return subject


def render_question(
    question: dict,
    index: int,
    total: int,
    mode_cfg: ModeConfig,
):
    st.markdown(
        f"<div class='question-card'>"
        f"<div style='font-size:0.9rem;color:#555;'>Question {index + 1} of {total}</div>"
        f"<div style='margin-top:0.25rem;font-size:0.9rem;color:#777;'>"
        f"Difficulty: {question.get('difficulty', 'easy').capitalize()}</div>"
        f"<div style='margin-top:0.75rem;font-size:1.05rem;font-weight:500;'>"
        f"{question['question']}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    key = f"answer_{index}"
    selected = st.radio("Choose your answer:", question["options"], key=key)
    submit = st.button("Submit", key=f"submit_{index}")

    return selected, submit


def render_result_view(score: int, total_questions: int, max_possible: int):
    st.subheader("Quiz Complete")

    st.write(f"Total questions answered: {total_questions}")
    st.write(f"Weighted score: {score} (max possible approx. {max_possible})")

    if total_questions > 0 and max_possible > 0:
        percentage = (score / max_possible) * 100
        st.write(f"Approximate performance: {percentage:.1f}%")

        if percentage >= 80:
            st.success("Performance band: High. Strong understanding demonstrated.")
        elif percentage >= 50:
            st.info("Performance band: Moderate. Good progress with room for improvement.")
        else:
            st.warning("Performance band: Emerging. Additional practice is recommended.")
    else:
        st.info("No questions were answered in this session.")

    st.markdown("---")
    st.write("You may retry the same quiz, or select a different mode or subject.")

