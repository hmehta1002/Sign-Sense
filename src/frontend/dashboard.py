import streamlit as st
import pandas as pd
import plotly.express as px


def render_dashboard(engine):
    st.title("📊 Performance Dashboard")

    if not engine.history:
        st.warning("No data available. Take a quiz first.")
        return

    df = pd.DataFrame(engine.history)

    st.metric("Total Score", engine.score)
    st.metric("Best Streak", engine.best_streak)

    fig = px.pie(df, names=df.correct.map({True: "Correct", False: "Wrong"}), title="Accuracy")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(df, x="question", y="time_taken", title="⏱ Time per Question")
    st.plotly_chart(fig2, use_container_width=True)
