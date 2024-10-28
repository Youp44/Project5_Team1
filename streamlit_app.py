import streamlit as st
import pandas as pd
import io

# Define expected sheet names
sheet_names = ['Dienstregeling', 'Afstandsmatrix']

# Hoofdcode
st.title("Project 5 - Omloopsplanning en Dienstregeling Analyse")

# Sidebar file uploads
st.sidebar.markdown("## Upload the required files")
uploaded_Omloopsplanning = st.sidebar.file_uploader("Upload 'Omloopsplanning'", type=["xlsx", "xls"])
uploaded_Dienstregeling = st.sidebar.file_uploader("Upload 'Dienstregeling'", type=["xlsx", "xls"])

# Energy checking function
def controleer_energieverbruik_overschrijding(df_planning, df_tijden, energieverbruik_per_km=2.5, max_verbruik=364.5):
    def find_afstand(row, df_tijden):
        match = df_tijden[
            (df_tijden['startlocatie'] == row['startlocatie']) &
            (df_tijden['eindlocatie'] == row['eindlocatie']) &
            ((df_tijden['buslijn'] == row['buslijn']) | df_tijden['buslijn'].isna())
        ]
        return match.iloc[0]['afstand in meters'] if not match.empty else 0

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

        # Button to check energy consumption
        if st.button("Controleer energieverbruik"):
            overschrijdingen = controleer_energieverbruik_overschrijding(df_planning, df_tijden, energieverbruik_per_km, max_verbruik)
            if overschrijdingen:
                st.subheader("Overschrijdingen")
                for oversch in overschrijdingen:
                    tijd = oversch['tijd']
                    st.write(f"Energieverbruik overschreden in omloop {oversch['omloop']} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
            else:
                st.success(f"Energieverbruik bleef onder de {max_verbruik} kWh voor alle omlopen.")
    except Exception as e:
        st.error("An error occurred while processing the files. Please ensure the files are correctly formatted and try again.")
        st.experimental_rerun()  # Refresh the app if an error occurs
else:
    st.write("Upload both 'Omloopsplanning' and 'Dienstregeling' to proceed.")

# Status indicators
status = {
    'Bus': "good",
    'Omloop': "good",
    'Rit': "good"
}
for key, value in status.items():
    color = "green" if value == "good" else "orange" if value == "improve" else "red"
    icon = "✅️" if value == "good" else "🔶" if value == "improve" else "❌"
    st.markdown(f'<div style="color: {color};">{icon} {key} status is {value}</div>', unsafe_allow_html=True)

# Additional sections for error explanations and further outputs
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Uitleg fout')
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Verbeterde versie')
