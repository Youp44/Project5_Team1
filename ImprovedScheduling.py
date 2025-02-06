import streamlit as st
import pandas as pd 
import plotly.express as px

def run():
    st.title("Improved Bus Planning")
    
    improved_schedule = pd.read_excel('')
    st.dataframe(improved_schedule.head(10))
    
    fig = px.timeline(
        improved_schedule, 
    x_start='starttijd datum', 
    x_end='eindtijd datum', 
    y='omloopnummer', 
    color='activiteit'
    )
    fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_layout(
    title=dict(text=f'Gantt Chart for Bus Line ', font=dict(size=30))
    )
    fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
    
    # Toon de plot in Streamlit
    st.plotly_chart(fig)