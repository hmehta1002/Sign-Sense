import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(engine):
    st.title("📊 Performance Dashboard")

    if not engine.history:
        st.warning("Take a quiz first.")
        return

    df = pd.DataFrame(engine.history)

    st.metric("Score", engine.score)
    st.metric("Best Streak", engine.best_streak)

    pie = px.pie(df, names=df.correct.map({True: "Correct", False: "Wrong"}), title="Answer Accuracy")
    st.plotly_chart(pie, use_container_width=True)

    bar = px.bar(df, x="question", y="time_taken", title="Time per Question")
    st.plotly_chart(bar, use_container_width=True)
