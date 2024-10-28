import streamlit as st
import pandas as pd
import io

sheet_names = ['Dienstregeling', 'Afstandsmatrix']

# Hoofdcode
st.title("Project 5 - Omloopsplanning en Dienstregeling Analyse")

# Sidebar voor Omloopsplanning
st.sidebar.markdown("## Upload the 'Omloopsplanning'")
uploaded_Omloopsplanning = st.sidebar.file_uploader("Omloopsplanning", type=["xlsx", "xls"])

# Sidebar voor Dienstregeling
st.sidebar.markdown("## Upload the 'Dienstregeling'")
uploaded_Dienstregeling = st.sidebar.file_uploader("Dienstregeling", type=["xlsx", "xls"])

def controleer_energieverbruik_overschrijding(df_planning, df_tijden, energieverbruik_per_km=2.5, max_verbruik=364.5):
    def find_afstand(row, df_tijden):
        match = df_tijden[
            (df_tijden['startlocatie'] == row['startlocatie']) &
            (df_tijden['eindlocatie'] == row['eindlocatie']) &
            ((df_tijden['buslijn'] == row['buslijn']) | df_tijden['buslijn'].isna())
        ]
        if not match.empty:
            return match.iloc[0]['afstand in meters']
        else:
            return 0

    df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_tijden), axis=1)
    df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000
    df_planning['energieverbruik'] = df_planning['afstand_km'] * energieverbruik_per_km

    overschrijdingen = []

    for omloop_nummer, omloop_data in df_planning.groupby('omloop nummer'):
        cumulatief_verbruik = 0
        
        for index, row in omloop_data.iterrows():
            cumulatief_verbruik += row['energieverbruik']
            
            if cumulatief_verbruik > max_verbruik:
                overschrijdingen.append({
                    'omloop': omloop_nummer,
                    'tijd': row['eindtijd'],
                    'totaal_verbruik': cumulatief_verbruik
                })
                break

    return overschrijdingen

# Controleer of beide bestanden zijn geüpload
if uploaded_Omloopsplanning is not None and uploaded_Dienstregeling is not None:
    df_planning = pd.read_excel(io.BytesIO(uploaded_Omloopsplanning.read()))
    df_tijden = pd.read_excel(io.BytesIO(uploaded_Dienstregeling.read()), sheet_name=sheet_names[0])
    df_afstanden = pd.read_excel(io.BytesIO(uploaded_Dienstregeling.read()), sheet_name=sheet_names[1])

    # Toon de inhoud van beide bestanden (optioneel voor gebruikers)
    st.subheader("Planning Data Preview")
    st.dataframe(df_planning.head(10))

    st.subheader("Tijden Data Preview")
    st.dataframe(df_tijden.head(10))

    # Voeg invoeropties voor energieverbruik per km en max verbruik toe
    energieverbruik_per_km = st.number_input("Energieverbruik per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximaal verbruik per omloop (kWh)", min_value=1.0, value=364.5)

    # Knop om de berekening uit te voeren
    if st.button("Controleer energieverbruik"):
        overschrijdingen = controleer_energieverbruik_overschrijding(df_planning, df_tijden, energieverbruik_per_km, max_verbruik)

        # Resultaten tonen
        if overschrijdingen:
            st.subheader("Overschrijdingen")
            for oversch in overschrijdingen:
                tijd = oversch['tijd']
                st.write(f"Energieverbruik overschreden in omloop {oversch['omloop']} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
        else:
            st.success(f"Energieverbruik bleef onder de {max_verbruik} kWh voor alle omlopen.")

else:
    st.write("Upload both 'Omloopsplanning' and 'Dienstregeling' to proceed.")

# Statusweergave
status = {
    'Bus': "good",
    'Omloop': "good",
    'Rit': "good"
}
for key, value in status.items():
    color = "green" if value == "good" else "orange" if value == "improve" else "red"
    icon = "✅️" if value == "good" else "🔶" if value == "improve" else "❌"
    st.markdown(f'<div style="color: {color};">{icon} {key} status is {value}</div>', unsafe_allow_html=True)

# Additional feedback sections for error explanations
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Uitleg fout')
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Verbeterde versie')


# heb foto geprobeerd te uplaoden dit is echt poep


