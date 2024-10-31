import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

def run():
    st.title("Analyse Omloopsplanning en Dienstregeling")
    st.write("Welcome to the Home Page!")

    # Controleer of de benodigde DataFrames zijn opgeslagen in de session_state
    if 'df_planning' not in st.session_state:
        st.error("Er zijn geen geüploade gegevens. Upload de bestanden in de sidebar.")
        return
    
    df_planning = st.session_state.df_planning
    df_afstand = st.session_state.df_afstanden

    # Input voor energieverbruik en maximale verbruik
    energieverbruik_per_km = st.number_input("Energieverbruik per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximaal verbruik per omloop (kWh)", min_value=1.0, value=364.5)

    # Functie om afstand te vinden
    def find_afstand(row, df_afstand):
        match = df_afstand[
            (df_afstand['startlocatie'] == row['startlocatie']) & 
            (df_afstand['eindlocatie'] == row['eindlocatie']) & 
            ((df_afstand['buslijn'] == row['buslijn']) | df_afstand['buslijn'].isna())
        ]
        if not match.empty:
            return match.iloc[0]['afstand in meters']
        else:
            return 0

    # Controleer of df_planning en df_afstanden niet leeg zijn
    if df_planning.empty:
        st.error("df_planning is leeg!")
        return
    if df_afstand.empty:
        st.error("df_afstand is leeg!")
        return

    # Voeg de afstanden toe aan de planning DataFrame
    df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_afstand), axis=1)
    df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000

    # Voeg een selectbox toe voor omloopnummer
    unique_omloop_nummers = df_planning['omloop nummer'].unique()
    selected_omloop = st.selectbox("Kies een omloop nummer", unique_omloop_nummers)

    # Filteren op het geselecteerde omloop nummer
    df_selected_omloop = df_planning[df_planning['omloop nummer'] == selected_omloop]

    if not df_selected_omloop.empty:
        # Bereken verwacht energieverbruik
        df_selected_omloop['verwacht_energieverbruik'] = df_selected_omloop['afstand_km'] * energieverbruik_per_km

        # Cumulatieve som berekenen voor werkelijke en verwacht energieverbruik
        df_selected_omloop['cumulatief_energieverbruik'] = df_selected_omloop['energieverbruik'].cumsum()
        df_selected_omloop['cumulatief_verwacht_energieverbruik'] = df_selected_omloop['verwacht_energieverbruik'].cumsum()

        # Plotten van de resultaten
        plt.figure(figsize=(12, 6))

        # Functie om de lijn te tekenen, waarbij kleuren veranderen bij overschrijden van max_verbruik
        def plot_with_threshold(x, y, label, color_below, color_above):
            over_threshold = y > max_verbruik
            plt.plot(x[~over_threshold], y[~over_threshold], label=label, color=color_below, linewidth=2)
            plt.plot(x[over_threshold], y[over_threshold], color=color_above, linewidth=2)

        # Cumulatieve werkelijke energieverbruik plotten met drempel
        plot_with_threshold(df_selected_omloop.index, df_selected_omloop['cumulatief_energieverbruik'], 
                            label='Cumulatief Energieverbruik (Werkelijk)', color_below='blue', color_above='red')

        # Cumulatieve verwachte energieverbruik plotten met drempel
        plot_with_threshold(df_selected_omloop.index, df_selected_omloop['cumulatief_verwacht_energieverbruik'], 
                            label='Cumulatief Energieverbruik (Verwacht)', color_below='green', color_above='red')

        # Toevoegen van een horizontale lijn op max_verbruik
        plt.axhline(y=max_verbruik, color='black', linestyle='--', linewidth=1, label=f'Verbruikslimiet ({max_verbruik})')

        # Titel en labels
        plt.title(f'Energieverbruik en Cumulatief voor Omloop Nummer {selected_omloop}')
        plt.xlabel('Index')
        plt.ylabel('Energieverbruik (kWh)')
        plt.grid(True)
        plt.legend()

        # Toon de plot in Streamlit
        st.pyplot(plt)

    # Gantt-diagram genereren
    df_planning['starttijd datum'] = pd.to_datetime(df_planning['starttijd datum'])
    df_planning['eindtijd datum'] = pd.to_datetime(df_planning['eindtijd datum'])
    fig = px.timeline(df_planning, x_start='starttijd datum', x_end='eindtijd datum', y='omloop nummer', color='activiteit')
    fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_layout(
        title=dict(text='Gantt Chart', font=dict(size=30))
    )
    fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
    st.plotly_chart(fig)

    # Bereken overschrijding en toon status
    overschrijding = df_selected_omloop['cumulatief_energieverbruik'].max() > max_verbruik
    status_kleur = "red" if overschrijding else "green"
    status_bericht = "Overschreden" if overschrijding else "Onder de limiet"
    st.markdown(f'<div style="color: {status_kleur}; font-size: 20px;">{status_bericht}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    run()
