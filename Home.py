import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import plotly.express as px

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
        df_selected_omloop['cumulatief_energieverbruik'] = df_selected_omloop['energieverbruik'].cumsum()  # Zorg dat je deze kolom eerder definieert
        df_selected_omloop['cumulatief_verwacht_energieverbruik'] = df_selected_omloop['verwacht_energieverbruik'].cumsum()

        # Plotten van de resultaten
        plt.figure(figsize=(10, 4))

        # Cumulatieve energieverbruik plotten
        plt.plot(df_selected_omloop.index, df_selected_omloop['cumulatief_energieverbruik'], label='Cumulatief Energieverbruik (Werkelijk)', color='red', linewidth=2)

        # Cumulatieve verwacht energieverbruik plotten
        plt.plot(df_selected_omloop.index, df_selected_omloop['cumulatief_verwacht_energieverbruik'], label='Cumulatief Energieverbruik (Verwacht)', color='green', linewidth=2)

        # Titel en labels
        plt.title(f'Energieverbruik en Cumulatief voor Omloop Nummer {selected_omloop}')
        plt.xlabel('Index')
        plt.ylabel('Energieverbruik (kWh)')
        plt.grid(True)
        plt.legend()

        # Toon de plot in Streamlit
        st.pyplot(plt)

        # Zorg ervoor dat de eindtijd kolom correct wordt omgezet naar datetime
        df_planning['starttijd datum'] = pd.to_datetime(df_planning['starttijd datum'], errors='coerce')
        df_planning['eindtijd datum'] = pd.to_datetime(df_planning['eindtijd datum'], errors='coerce')

        fig = px.timeline(df_planning, x_start='starttijd datum', x_end='eindtijd datum', y='omloop nummer', color='activiteit')
        fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
        fig.update_layout(
            title=dict(text='Gantt chart', font=dict(size=30))
        )
        fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
        st.plotly_chart(fig)

        overschrijdigen = {}
# Loop door de unieke omloopnummers
        for omloop_nummer in df_planning['omloop nummer'].unique():
            # Filter de data voor het huidige omloopnummer
            df_omloop = df_planning[df_planning['omloop nummer'] == omloop_nummer]
    
            # Controleer of de filter niet leeg is voordat we de berekening uitvoeren
            if not df_omloop.empty:
                # Bereken verwacht energieverbruik
                df_omloop['verwacht_energieverbruik'] = df_omloop['afstand_km'] * energieverbruik_per_km
                cumulatief_verbruik = df_omloop['verwacht_energieverbruik'].cumsum()
        
                # Controleer op overschrijdingen, en alleen als cumulatief_verbruik geldig is
                if not cumulatief_verbruik.empty:
                    # Loop door de rijen en controleer per index
                    for idx, (index, row) in enumerate(df_omloop.iterrows()):
                        # Zorg dat idx niet buiten de lengte van cumulatief_verbruik ligt
                        if idx < len(cumulatief_verbruik) and cumulatief_verbruik.iloc[idx] > max_verbruik:
                            overschrijdigen[omloop_nummer] = {
                                'tijd': row['eindtijd datum'],     # Tijd van overschrijding
                                'totaal_verbruik': cumulatief_verbruik.iloc[idx]
                            }
                            break  # Stop de loop na de eerste overschrijding

        # Controleer of er overschrijdingen zijn en toon de resultaten
        if overschrijdigen:
            st.write("Lijst met eerste overschrijdingen van energieverbruik per omloop:")
            for omloop, oversch in overschrijdigen.items():
                tijd = oversch['tijd'].time() if pd.notna(oversch['tijd']) else "Onbekend"  # Controleer op NaT
                st.write(f"Energieverbruik overschreden in omloop {omloop} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
        else:
            st.write(f"Energieverbruik bleef onder de {max_verbruik} kWh voor alle omlopen.")

if __name__ == "__main__":
    run()
