import streamlit as st


def render_revision_page(engine):
    st.title("🔁 Revision Lab")

    if not engine or not engine.history:
        st.info("No completed quiz history to revise yet.")
        return

    st.write("Review the questions you got wrong:")

    wrong = [h for h in engine.history if not h["correct"]]
    if not wrong:
        st.success("You answered everything correctly, nothing to revise! 🎉")
        return

    for rec in wrong:
        st.markdown(
            f"**Q:** {rec['question']}  \n"
            f"**Your answer:** {rec['selected']}  \n"
            f"**Correct answer:** {rec['correct_answer']}"
        )
