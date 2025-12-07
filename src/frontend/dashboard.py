import streamlit as st
import pandas as pd
import plotly.express as px

def render_dashboard(engine):
    st.title("📊 Performance Dashboard")

    if not engine.history:
        st.warning("Complete a quiz first to see analytics.")
        return

    df = pd.DataFrame(engine.history)

    st.metric("🏆 Total Score", engine.score)
    st.metric("🔥 Best Streak", engine.best_streak)

    # Accuracy Pie Chart
    fig1 = px.pie(
        df,
        names=df.correct.map({True: "Correct", False: "Wrong"}),
        title="Answer Accuracy"
    )
    st.plotly_chart(fig1, use_container_width=True)
