import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# Plotting function
def plot_bus_schedule(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Houd bij welke routes al een label hebben om dubbele labels in de legenda te vermijden
    route_labels = {}
    
    # Itereer over de busomlopen
    for bus in df['omloop nummer'].unique():
        bus_df = df[df['omloop nummer'] == bus].sort_values(by='starttijd')  # Sorteer op starttijd
        prev_end_time = None  # Om de eindtijd van de vorige rit op te slaan
        
        for _, row in bus_df.iterrows():
            # Bereken de reistijd van de bus op de route
            reistijd = row['eindtijd'] - row['starttijd']
            
            # Voeg een idle balk toe als de huidige starttijd later is dan de vorige eindtijd
            if prev_end_time is not None and row['starttijd'] > prev_end_time:
                idle_time = row['starttijd'] - prev_end_time
                ax.barh(bus, idle_time, left=prev_end_time, color='lightgray', edgecolor='black', label='Idle')
            
            # Voeg een balk toe voor de reistijd van de bus op de route
            if row['Route'] not in route_labels:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black', label=row['Route'])
                route_labels[row['Route']] = True
            else:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black')
            
            # Update de eindtijd voor de volgende iteratie
            prev_end_time = row['eindtijd']
    
    # Labels en opmaak
    ax.set_xlabel('Tijd (uren)')
    ax.set_ylabel('Busomloop')
    ax.set_title('Schema van busomlopen met idle-periodes en routes over tijd')
    ax.set_yticks(df['omloop nummer'].unique())
    ax.set_yticklabels(df['omloop nummer'].unique())
    
    # Stel de limieten van de x-as in op basis van de vroegste starttijd en laatste eindtijd
    start_lim = df['starttijd'].min()
    end_lim = df['eindtijd'].max()
    ax.set_xlim([start_lim, end_lim])
    
    # Gebruik een formatter om tijd in uren en minuten weer te geven
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Stel de ticks op de x-as in om om de twee uur te weergeven
    ticks = pd.date_range(start=start_lim, end=end_lim, freq='2H')
    ax.set_xticks(ticks)
    
    # Voeg labels toe aan de ticks
    ax.set_xticklabels([tick.strftime('%H:%M') for tick in ticks], rotation=45, ha='right')

    # Voeg een legenda toe met de routes en idle-periodes
    ax.legend(title="Status", bbox_to_anchor=(1.05, 1), loc='upper left')  # Plaats de legenda buiten de grafiek
    
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # Voeg een grid toe voor betere leesbaarheid
    plt.tight_layout()  # Zorg dat alles netjes in beeld past

    return fig  # Return the figure for Streamlit

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

        # Plot bus schedule
        if st.button("Plot bus schema"):
            df_planning['starttijd'] = pd.to_datetime(df_planning['starttijd'], format='%H:%M')
            df_planning['eindtijd'] = pd.to_datetime(df_planning['eindtijd'], format='%H:%M')
            fig = plot_bus_schedule(df_planning)
            st.pyplot(fig)  # Display the plot in Streamlit
    except Exception as e:
        st.error("An error occurred while processing the files. Please ensure the files are correctly formatted and try again.")
        st.write(f"Error details: {e}")  # Optionally show error details for debugging
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
