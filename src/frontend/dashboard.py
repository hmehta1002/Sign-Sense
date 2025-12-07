import streamlit as st
import pandas as pd

def render_dashboard(engine):
    if not engine.history:
        st.warning("Take a quiz first.")
        return

    df = pd.DataFrame(engine.history)
    
    st.subheader("📊 Performance Overview")
    st.metric("Score", engine.score)
    st.metric("Best Streak", engine.best_streak)

    st.bar_chart(df['correct'].value_counts())
    st.line_chart(df['time_taken'])
