import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
    

def run():
    st.title('Improvement planning')


    improved_scheduling = pd.read_excel('omloopplanning_fixed9.xlsx')

    st.session_state.improved_scheduling = improved_scheduling
    
    def plot_gantt_chart(df, title):
        fig = px.timeline(
            df, 
            x_start='starttijd datum', 
            x_end='eindtijd datum', 
            y='omloop nummer', 
            color='activiteit'
        )
        fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_layout(title=dict(text=title, font=dict(size=30)))
        fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
        st.plotly_chart(fig)


    if not improved_scheduling.empty:
        plot_gantt_chart(improved_scheduling,'Improved')
    else:
        st.error("No data available for improved planning")



    def plot_gantt_chart(df, title):
        fig = px.timeline(
            df, 
            x_start='starttijd datum', 
            x_end='eindtijd datum', 
            y='omloop nummer', 
            color='activiteit'
        )
        fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_layout(title=dict(text=title, font=dict(size=30)))
        fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
        st.plotly_chart(fig)


    if 'df_planning' in st.session_state and not st.session_state.df_planning.empty:
        plot_gantt_chart(st.session_state.df_planning,'Orginal planning')
    else:
        st.error("No data available for orginal planning")
