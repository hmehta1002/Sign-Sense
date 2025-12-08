import streamlit as st
import pandas as pd


def render_dashboard(engine):
    if not engine or not engine.history:
        st.warning("No quiz data yet. Complete a quiz first.")
        return

    st.header("📊 Performance Dashboard")

    df = pd.DataFrame(engine.history)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Score", engine.score)
    col2.metric("Best Streak", engine.best_streak)
    col3.metric("Questions Attempted", len(df))

    st.subheader("Correct vs Incorrect")
    counts = df["correct"].value_counts()
    chart_df = counts.rename(index={True: "Correct", False: "Incorrect"})
    st.bar_chart(chart_df)

    if "time_taken" in df.columns:
        st.subheader("Time Taken per Question (seconds)")
        st.line_chart(df["time_taken"])
