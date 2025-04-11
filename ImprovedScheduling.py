import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def run():
    st.title('Improvement planning')

    # Load improved scheduling file
    improved_scheduling = pd.read_excel('verbeterde_omloop_planning.xlsx')

    # Controleer en hernoem kolommen als nodig
    if 'Unnamed: 0' in improved_scheduling.columns:
        improved_scheduling.rename(columns={'Unnamed: 0': 'index'}, inplace=True)
    if 'omloopnummer' in improved_scheduling.columns:
        improved_scheduling.rename(columns={'omloopnummer': 'omloop nummer'}, inplace=True)

    st.session_state.improved_scheduling = improved_scheduling

    # Gantt chart functie
    def plot_gantt_chart(df, title):
        fig = px.timeline(
            df,
            x_start='starttijd datum',
            x_end='eindtijd datum',
            y='omloop nummer',
            color='activiteit'
        )
        fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed',
                         showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_layout(title=dict(text=title, font=dict(size=30)))
        fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
        st.plotly_chart(fig)

    # Toon verbeterde planning
    if not improved_scheduling.empty:
        plot_gantt_chart(improved_scheduling, 'Improved')
    else:
        st.error("No data available for improved planning")

    # Toon originele planning als beschikbaar
    if 'df_planning' in st.session_state and not st.session_state.df_planning.empty:
        df_original = pd.read_excel('omloopplanning.xlsx')

        # Zorg dat kolomnaam juist is voor Gantt-plot
        if 'omloopnummer' in df_original.columns:
            df_original.rename(columns={'omloopnummer': 'omloop nummer'}, inplace=True)
        if 'Unnamed: 0' in df_original.columns:
            df_original.rename(columns={'Unnamed: 0': 'index'}, inplace=True)

        plot_gantt_chart(df_original, 'Original planning')

        # === Materiaalritten analyse (original) ===
        materiaalritten_orig = df_original[df_original['activiteit'] == 'materiaal rit']
        aantal_orig = len(materiaalritten_orig)
        if aantal_orig > 0:
            materiaalritten_orig = materiaalritten_orig.copy()
            materiaalritten_orig['starttijd datum'] = pd.to_datetime(materiaalritten_orig['starttijd datum'])
            materiaalritten_orig['eindtijd datum'] = pd.to_datetime(materiaalritten_orig['eindtijd datum'])
            materiaalritten_orig['rit_duur'] = materiaalritten_orig['eindtijd datum'] - materiaalritten_orig['starttijd datum']
            totaal_orig = materiaalritten_orig['rit_duur'].sum().total_seconds() / 3600
        else:
            totaal_orig = 0.0

        # === Materiaalritten analyse (improved) ===
        materiaalritten_impr = improved_scheduling[improved_scheduling['activiteit'] == 'materiaal rit']
        aantal_impr = len(materiaalritten_impr)
        if aantal_impr > 0:
            materiaalritten_impr = materiaalritten_impr.copy()
            materiaalritten_impr['starttijd datum'] = pd.to_datetime(materiaalritten_impr['starttijd datum'])
            materiaalritten_impr['eindtijd datum'] = pd.to_datetime(materiaalritten_impr['eindtijd datum'])
            materiaalritten_impr['rit_duur'] = materiaalritten_impr['eindtijd datum'] - materiaalritten_impr['starttijd datum']
            totaal_impr = materiaalritten_impr['rit_duur'].sum().total_seconds() / 3600
        else:
            totaal_impr = 0.0

        # Toon in één overzicht
        with st.expander("Repositioning Trips comparison (Original vs Improved)"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original planning")
                st.metric("Number of Repositioning Trips", aantal_orig)
                st.metric("Total time (in hours)", f"{totaal_orig:.2f}")
            with col2:
                st.subheader("Improved planning")
                st.metric("Number of Repositioning Trips", aantal_impr)
                st.metric("Total time (in hours)", f"{totaal_impr:.2f}")
    else:
        st.error("No data available for original planning")

    # Analyse tekst
    st.markdown("""
    ### Analysis

    The improved planning shows a more efficient use of resources compared to the original planning.  
    Notably, there are fewer material transfer rides, which results in a more compact and time-efficient schedule and it's cost efficient.  
    This suggests that the improved planning not only optimizes vehicle usage but also contributes to a shorter overall operational timeline and a lower overall cost.
    """)
