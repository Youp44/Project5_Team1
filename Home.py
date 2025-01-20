import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def run():
    st.title("Analyze Bus Planning and Time Table")
    st.write("Welcome to the Home Page!")

    # Check if the necessary DataFrames are stored in session_state
    if 'df_planning' not in st.session_state:
        st.error("There is no uploaded data. Upload the files in the sidebar.")
        return
    
    df_planning = st.session_state.df_planning
    df_afstand = st.session_state.df_afstanden

    # Input for energy consumption and maximum consumption
    energieverbruik_per_km = st.number_input("Energy consumption per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximal consumption per bus (kWh)", min_value=1.0, value=270.0)

    # Function to find distance
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

    # Check if df_planning and df_afstanden are not empty
    if df_planning.empty:
        st.error("df_planning is empty!")
        return
    if df_afstand.empty:
        st.error("df_afstand is empty!")
        return

    # Add distances to the planning DataFrame
    df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_afstand), axis=1)
    df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000

    # Add a selectbox for loop number
    unique_omloop_nummers = df_planning['omloop nummer'].unique()
    selected_omloop = st.selectbox("Choose a bus number", unique_omloop_nummers)

    # Filter on the selected loop number
    df_selected_omloop = df_planning[df_planning['omloop nummer'] == selected_omloop]

         # Stel voor dat 'df_selected_omloop' al berekeningen heeft voor cumulatief energieverbruik
        # Controleer of df_selected_omloop niet leeg is
        # Controleer of df_selected_omloop niet leeg is
    if not df_selected_omloop.empty:
    # Bereken verwacht energieverbruik
        df_selected_omloop['verwacht_energieverbruik'] = df_selected_omloop['afstand_km'] * energieverbruik_per_km

    # Bereken cumulatief energieverbruik voor actueel en verwacht
        df_selected_omloop['cumulatief_energieverbruik'] = df_selected_omloop['energieverbruik'].cumsum()
        df_selected_omloop['cumulatief_verwacht_energieverbruik'] = df_selected_omloop['verwacht_energieverbruik'].cumsum()

    # Maximale verbruiksdrempel
        max_verbruik_line = max_verbruik

    # Maak een nieuwe lijst voor de aangepaste cumulatieve verwachte energieverbruik
        aangepaste_cumulatief = []
        cumulatieve_lading = 0  # Houdt de cumulatieve waarde na reset

    # Loop door de cumulatieve waarden
        for i in range(len(df_selected_omloop)):
        # Voeg de verwachte energieverbruik toe aan cumulatieve lading
            cumulatieve_lading += df_selected_omloop['verwacht_energieverbruik'].iloc[i]

        # Controleer of de cumulatieve verwachte energieverbruik boven de maximale verbruiksdrempel komt
            if cumulatieve_lading > max_verbruik_line:
            # Zet de waarde op de drempel om het opladen te simuleren
                cumulatieve_lading = max_verbruik_line  # Beperk tot max_verbruik_line

        # Voeg de aangepaste cumulatieve waarde toe
            aangepaste_cumulatief.append(cumulatieve_lading)

        # Reset de cumulatieve lading naar 0 als we de drempel overschrijden
            if cumulatieve_lading == max_verbruik_line:
                cumulatieve_lading = 0  # Begin opnieuw met opladen

    # Zet de aangepaste cumulatieve waarden terug in de DataFrame
        df_aangepast = pd.DataFrame({
            'index': range(len(aangepaste_cumulatief)),
            'cumulatief_verwacht_energieverbruik': aangepaste_cumulatief
        })

    # Plot de resultaten
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

    # Plot de cumulatieve verwachte energieverbruik
        ax.plot(df_aangepast['index'], df_aangepast['cumulatief_verwacht_energieverbruik'], color='green', linewidth=2)

    # Voeg een horizontale lijn toe voor de maximale drempel
        ax.axhline(y=max_verbruik_line, color='purple', linestyle='--', label='Max Consumption (kWh)')

    # Titel en labels
        ax.set_title(f'Energy Consumption and Cumulative for Bus Number {selected_omloop}')
        ax.set_xlabel('Index')
        ax.set_ylabel('Energy Consumption (kWh)')
        ax.grid(True)
        ax.legend()

    # Toon de plot in Streamlit
        st.pyplot(fig)
    
    
        overschrijdigen = {}
        # Loop through the unique loop numbers
        for omloop_nummer in df_planning['omloop nummer'].unique():
            # Filter the data for the current loop number
            df_omloop = df_planning[df_planning['omloop nummer'] == omloop_nummer]
    
            # Check if the filter is not empty before performing the calculation
            if not df_omloop.empty:
                # Calculate expected energy consumption
                df_omloop['verwacht_energieverbruik'] = df_omloop['afstand_km'] * energieverbruik_per_km
                cumulatief_verbruik = df_omloop['verwacht_energieverbruik'].cumsum()
        
                # Check for exceedances, only if cumulative consumption is valid
                if not cumulatief_verbruik.empty:
                    # Loop through the rows and check for each index
                    for idx, (index, row) in enumerate(df_omloop.iterrows()):
                        # Ensure idx does not exceed the length of cumulative consumption
                        if idx < len(cumulatief_verbruik) and cumulatief_verbruik.iloc[idx] > max_verbruik:
                            overschrijdigen[omloop_nummer] = {
                                'tijd': row['eindtijd datum'],     # Time of exceedance
                                'totaal_verbruik': cumulatief_verbruik.iloc[idx]
                            }
                            break  # Stop the loop after the first exceedance



# Maak een lege lijst om gegevens in de DataFrame-vorm te verzamelen
        data = []

        # Loop door elke overschrijding en voeg de gegevens toe aan de lijst
        for omloop, oversch in overschrijdigen.items():
            tijd = oversch['tijd'].time() if pd.notna(oversch['tijd']) else "Unknown"  # Controleer op NaT
            data.append({
                'Omloop nummer': omloop,
                'Time': tijd,
                'Overschrijding': oversch['totaal_verbruik']
            })

    # Zet de gegevens om in een DataFrame
        df_overschrijding = pd.DataFrame(data)

# Controleer of er overschrijdingen zijn en toon de resultaten
        if not df_overschrijding.empty:
            st.write("List of first energy exceedances on time per bus:")
            st.dataframe(df_overschrijding, height=200)  # Maakt de DataFrame scrollbaar
        else:
            st.write(f"Energy consumption stayed under the threshold for all buses.")



        # Ensure the end time column is correctly converted to datetime
        df_planning['starttijd datum'] = pd.to_datetime(df_planning['starttijd datum'], errors='coerce')
        df_planning['eindtijd datum'] = pd.to_datetime(df_planning['eindtijd datum'], errors='coerce')

 

        
            # Controleer of de gefilterde data niet leeg is
        if not df_planning.empty:
            # Maak de Gantt Chart
            fig = px.timeline(
                df_planning, 
                x_start='starttijd datum', 
                x_end='eindtijd datum', 
                y='omloop nummer', 
                color='activiteit'
            )
            fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
            fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
            fig.update_layout(
                title=dict(text=f'Gantt Chart for Bus Line ', font=dict(size=30))
            )
            fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
    
            # Toon de plot in Streamlit
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for bus line ")
if __name__ == "__main__":
    run()

#SOC waarden 
# Veiligheidsmarge
# Oplaadtijden
# Consistenties
# Bussen niet teleporteren/ opsplittsen 
# accucapiciteit van 300KWu
# State of health (SOH) 85-95%
#oplaad tempo 450Kw opgeladen tot 90% Minstens 15 minuten achter elkaar opladen
# Gemiddelde verbruik ligt tussen 0.7 en 2.5 als die stil staat op 0.01
# 10% van de accucapiciteit als veiligheidsmarge

# Plan van aanpak. 
# Variable creeren SOC die de waarde aanhoud van de accu. We kunnen dan de rest van de waardes invoeren
# En de meegegeven parameters hanteren. Tijdens onze planning wordt deze variable dan bij gehouden. Wordt dit overschreden geeft dit een melding. 
# Voor zowel de onder of bovengrens hierbij is dan te zien wanneer dit gebeurd en wordt dit rood. Dit is onderdeel een van de omloop checker. 

# Deel 2 
# We moeten ook voldoen aan alle parameters die we net hebben opgenoemd ik denk dat het goed is als we hier ook een def van moeten maken. Zo kunnen we 
# De waardes van ook zowel de oplaadtijden controleren. Wat hier nog meer in moet komen te staan is later te benaderen. 

# Deel 3
# Zorgen dat de bus op dezelfde omloop blijft rijden en niet teleporteert van locatie naar locatie
# Hoe we dit moeten doen weet ik nog niet zeker. Mis is het handig om te checken of de rit tijden voldoen.
# Het omloop nummer mee te geven en te kijken of die bus ook logische route hanteert door dit te plotten per bus omloop?

 
