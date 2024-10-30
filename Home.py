import streamlit as st
import pandas as pd

def run():
    st.title("Analyse Omloopsplanning en Dienstregeling")
    st.write("Welcome to the Home Page!")

    # Controleer of de benodigde DataFrames zijn opgeslagen in de session_state
    if 'df_planning' not in st.session_state:
        st.error("Er zijn geen geüploade gegevens. Upload de bestanden in de sidebar.")
        return
    
    df_planning = st.session_state.df_planning
    df_afstanden = st.session_state.df_afstanden

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
    if df_afstanden.empty:
        st.error("df_afstand is leeg!")
        return

    # Voeg de afstanden toe aan de planning DataFrame
    df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_afstanden), axis=1)

    # Zet meters om naar kilometers
    df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000

    # Voeg een kolom toe voor energieverbruik per rit
    df_planning['energieverbruik'] = df_planning['afstand_km'] * energieverbruik_per_km

    # Controleer per omloop het cumulatieve energieverbruik
    overschrijdingen = []

    for omloop_nummer, omloop_data in df_planning.groupby('omloop nummer'):
        cumulatief_verbruik = 0

        for index, row in omloop_data.iterrows():
            cumulatief_verbruik += row['energieverbruik']

            # Controleer of het cumulatieve energieverbruik boven de limiet komt
            if cumulatief_verbruik > max_verbruik:
                overschrijdingen.append({
                    'omloop': omloop_nummer,
                    'tijd': row['eindtijd'],
                    'totaal_verbruik': cumulatief_verbruik
                })
                break

    # Bepaal de status op basis van het aantal overschrijdingen
    Bus_status = 'Good' if len(overschrijdingen) == 0 else 'Improvement'

    status = {
        'Bus': Bus_status,
        'Omloop': "Good",  # Dit kan ook worden aangepast als nodig
        'Rit': "Good"      # Dit kan ook worden aangepast als nodig
    }
        
    # Status updates bovenaan
    for key, value in status.items():
        color = "green" if value == "Good" else "orange" if value == "Improvement" else "red"
        icon = "✅️" if value == "Good" else "🔶" if value == "Improvement" else "❌"
        st.markdown(f'<div style="color: {color}; font-size: 20px;">{icon} {key} status: {value}</div>', unsafe_allow_html=True)

    if overschrijdingen:
        st.subheader("Overschrijdingen van energieverbruik")

        # Maak een DataFrame van overschrijdingen
        overschrijdingen_df = pd.DataFrame(overschrijdingen)
        overschrijdingen_df['tijd'] = pd.to_datetime(overschrijdingen_df['tijd']).dt.time
        
        # Toon de tabel
        st.dataframe(overschrijdingen_df)

        # Toon een tekst voor elke overschrijding
        for oversch in overschrijdingen:
            tijd = oversch['tijd']
            st.write(f"Energieverbruik overschreden in omloop {oversch['omloop']} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
    else:
        st.success(f"Energieverbruik bleef onder de {max_verbruik} kWh voor alle omlopen.")
