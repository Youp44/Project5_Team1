import streamlit as st
import pandas as pd

# Define expected sheet names
sheet_names = ['Dienstregeling', 'Afstandsmatrix']

# Hoofdcode
st.title("Project 5 - Omloopsplanning en Dienstregeling Analyse")

# Sidebar file uploads
st.sidebar.markdown("## Upload the required files")
uploaded_Omloopsplanning = st.sidebar.file_uploader("Upload 'Omloopsplanning'", type=["xlsx", "xls"])
uploaded_Dienstregeling = st.sidebar.file_uploader("Upload 'Dienstregeling'", type=["xlsx", "xls"])

# Check if both files are uploaded
if uploaded_Omloopsplanning and uploaded_Dienstregeling:
    try:
        # Load files into DataFrames
        df_planning = pd.read_excel(uploaded_Omloopsplanning)
        df_tijden = pd.read_excel(uploaded_Dienstregeling, sheet_name=sheet_names[0])
        df_afstanden = pd.read_excel(uploaded_Dienstregeling, sheet_name=sheet_names[1])

        # Display uploaded data previews
        st.subheader("Planning Data")
        st.dataframe(df_planning.head(10))  # Display a sample to avoid large load

        st.subheader("Tijden Data")
        st.dataframe(df_tijden.head(10))  # Display a sample to avoid large load

        # Input for energy consumption and max consumption
        energieverbruik_per_km = st.number_input("Energieverbruik per km (kWh)", min_value=0.1, value=2.5)
        max_verbruik = st.number_input("Maximaal verbruik per omloop (kWh)", min_value=1.0, value=364.5)

        # Koppel de afstanden aan de planning op basis van startlocatie, eindlocatie en buslijn
        def find_afstand(row, df_afstand):
            # Filteren op basis van startlocatie, eindlocatie en buslijn
            match = df_afstand[
                (df_afstand['startlocatie'] == row['startlocatie']) &
                (df_afstand['eindlocatie'] == row['eindlocatie']) &
                ((df_afstand['buslijn'] == row['buslijn']) | df_afstand['buslijn'].isna())
            ]
            
            # Als er een match is, haal de afstand in meters op, anders 0
            if not match.empty:
                return match.iloc[0]['afstand in meters']
            else:
                return 0

        # Controleer of df_planning en df_afstand niet leeg zijn
        if df_planning.empty:
            st.error("df_planning is leeg!")
        if df_afstanden.empty:
            st.error("df_afstand is leeg!")
        
        # Voeg de afstanden toe aan de planning DataFrame
        df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_afstanden), axis=1)

        # Zet meters om naar kilometers
        df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000

        # Voeg een kolom toe voor energieverbruik per rit (afstand_km * energieverbruik_per_km)
        df_planning['energieverbruik'] = df_planning['afstand_km'] * energieverbruik_per_km

        # Controleer per omloop het cumulatieve energieverbruik
        overschrijdingen = []  # Lijst om omloop nummer, tijd en totaal verbruik van overschrijding bij te houden

        for omloop_nummer, omloop_data in df_planning.groupby('omloop nummer'):
            cumulatief_verbruik = 0  # Reset cumulatief verbruik per omloop
            
            for index, row in omloop_data.iterrows():
                cumulatief_verbruik += row['energieverbruik']  # Voeg het energieverbruik van de huidige rit toe
                
                # Controleer of het cumulatieve energieverbruik boven de limiet komt
                if cumulatief_verbruik > max_verbruik:
                    overschrijdingen.append({
                        'omloop': omloop_nummer,       # Omloop nummer
                        'tijd': row['eindtijd'],       # Tijd van overschrijding
                        'totaal_verbruik': cumulatief_verbruik  # Huidig totaalverbruik
                    })
                    break  # Stop met verder controleren voor deze omloop als het verbruik al is overschreden
        # Bepaal de status op basis van het aantal overschrijdingen
        if len(overschrijdingen) > 0:
            Bus_status = 'Improvement'
        else:
            Bus_status = 'Good'
        
        # Status indicators
        status = {
            'Bus': Bus_status,
            'Omloop': "Good",  # Dit kan ook worden aangepast als nodig
            'Rit': "Good"      # Dit kan ook worden aangepast als nodig
        }
        
        for key, value in status.items():
            color = "green" if value == "Is good" else "orange" if value == "Can use improvement" else "Is bad"
            icon = "✅️" if value == "Good" else "🔶" if value == "Improvement" else "❌"
            st.markdown(f'<div style="color: {color};">{icon} {key} status {value}</div>', unsafe_allow_html=True)

        # Controleer of er overschrijdingen zijn
        if overschrijdingen:
            st.subheader("Overschrijdingen van energieverbruik")
            
            # Maak een DataFrame van overschrijdingen
            overschrijdingen_df = pd.DataFrame(overschrijdingen)
            overschrijdingen_df['tijd'] = pd.to_datetime(overschrijdingen_df['tijd'])
            
            # Voeg een tijd kolom toe in het juiste formaat
            overschrijdingen_df['tijd'] = overschrijdingen_df['tijd'].dt.time
            
            # Toon de tabel
            st.dataframe(overschrijdingen_df)

            # Toon een tekst voor elke overschrijding
            for oversch in overschrijdingen:
                tijd = oversch['tijd']  # Tijd van overschrijding
                st.write(f"Energieverbruik overschreden in omloop {oversch['omloop']} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
        else:
            st.success(f"Energieverbruik bleef onder de {max_verbruik} kWh voor alle omlopen.")
    
    except Exception as e:
        st.error("Er is een fout opgetreden bij het verwerken van de bestanden. Controleer of de bestanden correct zijn geformatteerd en probeer het opnieuw.")
else:
    st.write("Upload zowel 'Omloopsplanning' als 'Dienstregeling' om door te gaan.")

# Additional sections for error explanations and further outputs
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Uitleg fout')
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Verbeterde versie')
