import streamlit as st


def render_dashboard(engine):
    st.title("📊 Dashboard")

    if not engine:
        st.info("No quiz data yet. Finish a quiz first.")
        return

    st.subheader("Score")
    st.write(f"Total score: **{engine.score}**")
    st.write(f"Best streak: **{engine.best_streak}**")

    st.subheader("History")
    if not engine.history:
        st.info("No questions answered yet.")
    else:
        for rec in engine.history:
            st.markdown(
                f"- **Q:** {rec['question']}  \n"
                f"  **Your answer:** {rec['selected']}  \n"
                f"  **Correct:** {'✅' if rec['correct'] else '❌'}  \n"
                f"  **Points:** {rec['points']}"
            )
