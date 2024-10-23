import streamlit as st
import pandas as pd 
import streamlit as st


# Plaats de functie hier
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

# Rest van de Streamlit code blijft hetzelfde

# Titel van de applicatie
st.title("Project 5 - Omloopsplanning en Dienstregeling Analyse")

# Sidebar voor Omloopsplanning
st.sidebar.markdown("## Upload the 'Omloopsplanning'")
uploaded_Omloopsplanning = st.sidebar.file_uploader("Omloopsplanning", type=["xlsx", "xls"])

# Sidebar voor Dienstregeling
st.sidebar.markdown("## Upload the 'Dienstregeling'")
uploaded_Dienstregeling = st.sidebar.file_uploader("Dienstregeling", type=["xlsx", "xls"])

# Check if both files are uploaded
if uploaded_Omloopsplanning and uploaded_Dienstregeling:
    # Lees de bestanden in als DataFrames
    df_planning = pd.read_excel(uploaded_Omloopsplanning)
    df_tijden = pd.read_excel(uploaded_Dienstregeling)

    # Toon de inhoud van beide bestanden
    st.subheader("Planning Data")
    st.write(df_planning)

    st.subheader("Tijden Data")
    st.write(df_tijden)

    # Voeg invoeropties voor energieverbruik per km en max verbruik toe
    energieverbruik_per_km = st.number_input("Energieverbruik per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximaal verbruik per omloop (kWh)", min_value=1.0, value=364.5)

    # Knop om de berekening uit te voeren
    if st.button("Controleer energieverbruik"):
        # Functie om overschrijdingen te controleren (verondersteld dat de functie reeds gedefinieerd is)
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
    # Als geen van beide bestanden zijn geüpload, toon een bericht
    st.write("Upload both 'Omloopsplanning' and 'Dienstregeling' to proceed.")

# Optioneel: toon de shape van de DataFrames als bestanden zijn geüpload
if uploaded_Omloopsplanning is not None:
    st.write("Shape of the 'Omloopsplanning' DataFrame:", df_planning.shape)

if uploaded_Dienstregeling is not None:
    st.write("Shape of the 'Dienstregeling' DataFrame:", df_tijden.shape)
# als je hier een loop van maakt voor je drie functie.
# Zo kan je Status I maken in een list met de correcte namen, 
# En het algemeen maken door de termen good en improve gebruiken 
Bus ="good"
Omloop = 'good'
Rit = "good"
status = {
    'Bus': Bus,
    'Omloop': Omloop,
    'Rit': Rit
}
for key, value in status.items():
    if value == "good":
        # Display a success indicator with custom styling
        st.markdown(f'<div style="color: green;">✅️ {key} status is good</div>', unsafe_allow_html=True)
    elif value == "improve":
        # Display an improvement indicator with custom styling
        st.markdown(f'<div style="color: orange;">🔶 {key} status can be improved</div>', unsafe_allow_html=True)
    else:
        # Display a failure indicator with custom styling
        st.markdown(f'<div style="color: red;">❌ {key} status is wrong</div>', unsafe_allow_html=True)


# Omloopsplanning, maar kunnen we wel groot genoege bestanden uploaden?
st.sidebar.markdown("## Upload the 'Omloopsplanning'")

uploaded_Omloopsplanning = st.sidebar.file_uploader("Omloopsplanning",type=["xlsx", "xls"])

# Check if a file is uploaded
if uploaded_Omloopsplanning is not None:
    # Load the file into a DataFrame
    df = pd.read_excel(uploaded_Omloopsplanning)

    # Display the contents of the Excel file in the main app
    st.write("Here's a preview of your Excel file:")
    st.dataframe(df)

    # Optionally, show the shape of the DataFrame
    st.write(f"Shape of the DataFrame: {df.shape}")
else: 
    st.write("You didn't upload an 'Omloopsplanning'")


#Dienstregeling

st.sidebar.markdown("## Upload the 'Dienstregeling'")

uploaded_Dienstregeling = st.sidebar.file_uploader("Dienstregeling",type=["xlsx", "xls"])



# Check if a file is uploaded
if uploaded_Dienstregeling is not None:
    # Load the file into a DataFrame
    df = pd.read_excel(uploaded_Dienstregeling)

    # Display the contents of the Excel file in the main app
    st.write("Here's a preview of your Dienstregeling file:")
    st.dataframe(df)

    # Optionally, show the shape of the DataFrame
    st.write(f"Shape of the DataFrame: {df.shape}")
else: 
    st.write("You didn't upload an 'Dienstregeling'")
    
# en kunnen we alle delen niet in van die blokken plaats 
# word bijv bovenste blok groen als alles voldoet


st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Uitleg fout')
# hier onder dan ff de uitleg van waar de fout zit met een drop down df wss per bolletje 
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Verbeterde versie')
#output excel file, dit is voor later

# heb foto geprobeerd te uplaoden dit is echt poep


