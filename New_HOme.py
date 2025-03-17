import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def run():
    st.title("Analyze Bus Planning and Time Table")
    st.write("Welcome to the Home Page!")

    # Check if the necessary DataFrames are stored in session_state
    if 'df_planning' not in st.session_state:
        st.warning("Please upload both 'Bus Planning' and 'Time Table' in to the sidebar to continue.")

        return
    
    df_planning = st.session_state.df_planning
    df_afstand = st.session_state.df_afstanden
    df_tijden = st.session_state.df_tijden
    df_planning.rename(columns={'omloop nummer': 'omloopnummer'}, inplace=True)
    df_planning.rename(columns={'Unnamed: 0': 'index'}, inplace=True)
    # Stukje met 'boolean index maken om hierbij aan te geven of de planning voldoet'
    #st.success('Wow')
    #st.warning('Je bus omloop voldoet niet aan de omgangs eisen')


# Voeg een kolom toe met "absolute tijd" in minuten sinds middernacht
    def bereken_absolute_tijd(df):
        # Omzetten naar datetime.time als dat nog niet gebeurd is
        df['starttijd'] = pd.to_datetime(df['starttijd'], format='%H:%M:%S').dt.time
        df['eindtijd'] = pd.to_datetime(df['eindtijd'], format='%H:%M:%S').dt.time

        def tijd_naar_minuten(tijd):
            return tijd.hour * 60 + tijd.minute

        df['starttijd_min'] = df['starttijd'].apply(tijd_naar_minuten)
        df['eindtijd_min'] = df['eindtijd'].apply(tijd_naar_minuten)

        # Voeg 24 uur toe aan eindtijd als deze vóór starttijd ligt (over middernacht)
        df['eindtijd_min'] = df.apply(
            lambda row: row['eindtijd_min'] + 1440 if row['eindtijd_min'] < row['starttijd_min'] else row['eindtijd_min'],
            axis=1
        )

        # Sorteer op starttijd_min en eindtijd_min
        df = df.sort_values(by=['starttijd_min', 'eindtijd_min', 'index']).reset_index(drop=True)
        return df

    # Bereken absolute tijd en sorteer
    df_planning = bereken_absolute_tijd(df_planning)



    def controleer_soc_grenzen(df_planning, df_afstand, energieverbruik_per_km=2.5, MAX_waarde_SOC=270, min_waarde_SOC=30):
        """
        Controleert de SOC-waarden op basis van theoretisch energieverbruik berekend met afstand.

        Parameters:
        - df_planning (pd.DataFrame): De input DataFrame met de planning.
        - df_afstand (pd.DataFrame): DataFrame met afstanden tussen locaties.
        - energieverbruik_per_km (float): Verbruik in kWh per km.
        - MAX_waarde_SOC (float): Maximale SOC-waarde.
        - min_waarde_SOC (float): Minimale SOC-waarde.
    
        Returns:
        - df_overschrijdingen (pd.DataFrame): DataFrame met rijen waarin de SOC wordt overschreden.
        - soc_per_omloop (dict): Dictionary met SOC-waarden per omloopnummer.
        """
        soc_per_omloop = {}
        df_planning['SOC'] = 0  # Voeg een SOC-kolom toe
        overschrijdingen = []
        fouten = False
        warning = False
        
        for omloop in df_planning['omloopnummer'].unique():
            SOC = MAX_waarde_SOC
            soc_waarden = []
        
            for i, row in df_planning[df_planning['omloopnummer'] == omloop].iterrows():
                # Reset SOC als de minimale grens wordt bereikt
                if SOC < min_waarde_SOC:
                    SOC = MAX_waarde_SOC
            
                # Zoek afstand
                match = df_afstand[
                    (df_afstand['startlocatie'] == row['startlocatie']) & 
                    (df_afstand['eindlocatie'] == row['eindlocatie']) & 
                    ((df_afstand['buslijn'] == row['buslijn']) | df_afstand['buslijn'].isna())
                ]
                afstand_m = match.iloc[0]['afstand in meters'] if not match.empty else 0
                afstand_km = afstand_m / 1000  # Omzetten naar kilometers
            
                # Bereken energieverbruik
                energieverbruik = afstand_km * energieverbruik_per_km
            
                # Trek energieverbruik af van SOC
                SOC -= energieverbruik
            
                # Sla SOC-waarde op
                soc_waarden.append(SOC)
                df_planning.at[i, 'SOC'] = SOC
            
                # Controleer de SOC-grenzen
                if SOC < min_waarde_SOC:
                    if not warning:
                        st.error(f'There are intervals where a bus is below the minimum SOC value.')
                        warning = True
                    fouten = True
                    overschrijdingen.append({
                        'rij_index': i,
                        'omloopnummer': omloop,
                        'afstand_km': afstand_km,
                        'energieverbruik': energieverbruik,
                        'SOC': SOC
                    })
                    # Reset SOC na overschrijding
                    SOC = MAX_waarde_SOC
        
            # Sla SOC-waarden per omloop op
            soc_per_omloop[omloop] = soc_waarden
    
        df_overschrijdingen = pd.DataFrame(overschrijdingen)
    
        return df_overschrijdingen, fouten, soc_per_omloop

    # Interface met Streamlit
    energieverbruik_per_km = st.number_input("Energy consumption per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximal consumption per bus (kWh)", min_value=1.0, value=270.0)
    min_waarde_SOC = st.number_input("Minimal SOC-value", min_value=1.0, value=30.0)
    df_overschrijdingen, fouten, soc_per_omloop = controleer_soc_grenzen(df_planning, df_afstand, energieverbruik_per_km, max_verbruik)

    if fouten:
        with st.expander("Click for more information"):
            st.write("The following rows have errors or violations:")
            st.dataframe(df_overschrijdingen)
    else:
        st.success('Alles in orde! Geen SOC-overschrijdingen.')

    # Selectie van omloopnummer voor plot
    omloop_selectie = st.selectbox("Selecteer een omloopnummer om SOC te bekijken", list(soc_per_omloop.keys()))

    # Plot van SOC-waarden voor geselecteerde omloop
    fig, ax = plt.subplots()
    ax.plot(range(len(soc_per_omloop[omloop_selectie])), soc_per_omloop[omloop_selectie], label=f'Theoretische SOC waarde - Omloop {omloop_selectie}', linestyle='-', marker='o')
    ax.axhline(y=min_waarde_SOC, color='r', linestyle='--', label='Minimale SOC (30)')
    ax.set_xlabel("Index")
    ax.set_ylabel("SOC waarde (kWh)")
    ax.set_title(f"Theoretische SOC waarde voor Omloop {omloop_selectie}")
    ax.legend(loc="upper right")  # Legenda rechtsboven
    st.pyplot(fig)





    


    def controleer_oplaadtijd(df_planning, min_oplaadtijd=15):
        """
        Controleert de opladenstijd en geeft een waarschuwing als deze korter is dan de minimale tijd.
        
        Parameters:
        - df_planning (pd.DataFrame): De input DataFrame met de planning en energieverbruik.
        - min_oplaadtijd (int): De minimale vereiste opladenstijd in minuten.
    
        Returns:
        - df_korte_oplaadtijden (pd.DataFrame): DataFrame met rijen waar de oplaadtijd korter is dan de minimale tijd.
        - waarschuwing (bool): Geeft aan of er een waarschuwing is gegeven (True als er fouten zijn, anders False).
        """
        # Omzetten naar datetime als de tijden in stringformaat zijn
        df_planning['starttijd'] = pd.to_datetime(df_planning['starttijd'], format='%H:%M:%S')
        df_planning['eindtijd'] = pd.to_datetime(df_planning['eindtijd'], format='%H:%M:%S')

        warning = False  # Variabele om te controleren of de waarschuwing al is gegeven
        korte_oplaadtijden = []  # Lijst om kortere oplaadtijden op te slaan

        # Loop door de DataFrame om de opladenstijd te berekenen
        for i, row in df_planning.iterrows():
            if row['energieverbruik'] <= 0:
                # Bereken de oplaadtijd in minuten
                oplaad_tijd = (row['eindtijd'] - row['starttijd']).total_seconds() / 60  # Omzetten naar minuten
    
                # Controleer of de opladingstijd kleiner is dan de minimale oplaadtijd
                if oplaad_tijd <= min_oplaadtijd:
                    if not warning:
                        st.error(f'Error charing time is less than {min_oplaadtijd} minutes!')
                        warning = True  # Waarschuwing maar één keer tonen
                    korte_oplaadtijden.append({
                        'rij_index': i,
                        'starttijd': row['starttijd'].strftime('%H:%M:%S'),
                        'eindtijd': row['eindtijd'].strftime('%H:%M:%S'),
                        'energieverbruik': row['energieverbruik'],
                        'oplaadtijd': oplaad_tijd
                    })

        # Maak een DataFrame met alleen de kortere oplaadtijden
        df_korte_oplaadtijden = pd.DataFrame(korte_oplaadtijden)
    
        # Toon de succesmelding als er geen korte oplaadtijden zijn
        if not warning:
            st.success(f' Everything is fine! There are no charging time shorter than {min_oplaadtijd} minutes.')

        return df_korte_oplaadtijden, warning


    # Voorbeeld van het gebruik van de functie:
    df_korte_oplaadtijden, waarschuwing = controleer_oplaadtijd(df_planning)

    # Toon de DataFrame met korte oplaadtijden als er fouten zijn
    if not df_korte_oplaadtijden.empty:
        st.dataframe(df_korte_oplaadtijden)  # Alleen tonen als er korte oplaadtijden zijn
    
    

    def controleer_verspringende_locaties_per_omloop(df_planning):
        """
        Controleert of de eindlocatie van de vorige rij gelijk is aan de startlocatie van de huidige rij,
        per uniek omloopnummer en gesorteerd op de kolom 'index'.
        
        Parameters:
        - df_planning (pd.DataFrame): De input DataFrame met omloopnummers en locaties.
        
        Returns:
        - verspringingen (pd.DataFrame): DataFrame met rijen waarin de bus van locatie verspringt.
        - waarschuwing (bool): Geeft aan of er een waarschuwing is (True als er verspringingen zijn, anders False).
        """
        verspringingen = []  # Lijst om rijen met verspringingen op te slaan
        waarschuwing = False
    
        # Loop door unieke omloopnummers
        for omloop in df_planning['omloopnummer'].unique():
            # Filter de DataFrame op het huidige omloopnummer en sorteer op 'index'
            df_omloop = df_planning[df_planning['omloopnummer'] == omloop].sort_values(by='starttijd')
    
            # Loop door de gefilterde DataFrame en controleer locaties
            for i in range(1, len(df_omloop)):
                vorige_rij = df_omloop.iloc[i - 1]
                huidige_rij = df_omloop.iloc[i]
    
                # Controleer of de eindlocatie van de vorige rij gelijk is aan de startlocatie van de huidige rij
                if vorige_rij['eindlocatie'] != huidige_rij['startlocatie']:
                    if not waarschuwing:
                        st.warning("Bus jumps location!")
                        waarschuwing = True
                    verspringingen.append({
                        'omloopnummer': omloop,
                        'index_huidige_rij': huidige_rij['index'],
                        'vorige_eindlocatie': vorige_rij['eindlocatie'],
                        'huidige_startlocatie': huidige_rij['startlocatie']
                    })

        # Maak een DataFrame met alle verspringingen
        verspringingen_df = pd.DataFrame(verspringingen)

        return verspringingen_df, waarschuwing


    # Voorbeeld gebruik:
    verspringingen_df, waarschuwing = controleer_verspringende_locaties_per_omloop(df_planning)

    # Toon de resultaten
    if not verspringingen_df.empty:
        st.dataframe(verspringingen_df)  # Alleen tonen als er verspringingen zijn
    else:
        st.success('Everything is fine there are no busses jumping from location!')




    def check_missed_buses(df_tijden, df_planning):
        """
        Controleert of alle vertrektijden uit df_tijden aanwezig zijn in de geplande ritten van df_planning.
        Als een vertrektijd uit df_tijden ontbreekt in df_planning, wordt dit beschouwd als een gemiste rit.
    
        Parameters:
            df_tijden (pd.DataFrame): DataFrame met de verwachte dienstregeling (vertrektijden).
            df_planning (pd.DataFrame): DataFrame met de geplande ritten.

        Returns:
            pd.DataFrame: DataFrame met gemiste ritten.
        """
        if df_tijden.empty or df_planning.empty:
            return pd.DataFrame()  # Geen data beschikbaar, dus geen check nodig

        # We willen de buslijn, startlocatie, eindlocatie en vertrektijd controleren
        # Maak een lijst van de unieke ritten in df_tijden
        df_tijden_unique = df_tijden[['buslijn', 'startlocatie', 'eindlocatie', 'vertrektijd']].drop_duplicates()

        # Merge df_tijden met df_planning op buslijn, startlocatie en eindlocatie om te zien of de vertrektijd in de planning staat
        merged_df = df_tijden_unique.merge(
            df_planning, 
            on=['buslijn', 'startlocatie', 'eindlocatie'], 
            how='left', 
            suffixes=('_tijden', '_planning')
        )

        # Zoek naar rijen waar de vertrektijd niet overeenkomt, of de rit niet in de planning staat
        missed_buses = merged_df[merged_df['vertrektijd'].isna()]

        return missed_buses  # Retourneer de gemiste bussen

    # Voer de controle uit
    missed_stations_df = check_missed_buses(df_tijden, df_planning)

    # Controleer of er gemiste stations zijn en toon foutmelding
    if not missed_stations_df.empty:
        st.error("Busstation are missed! See the tabel below for more information.")
        st.dataframe(missed_stations_df)
    else:
        st.success("All the busses comply to the schedule!")


    def eindtijd_groter_startijd(df):
        waarschuwing = False 
        tijd_controle = []
        for i, row in df.iterrows(): 
            if row['eindtijd_min'] < row['starttijd_min']:
                if not waarschuwing:
                    st.warning("Eindtijd > Startijd")
                    waarschuwing = True
                tijd_controle.append({
                    'omloopnummer': row['omloopnummer'],
                    'index_huidige_rij': row['index'],
                    'eindtijd': row['eindtijd_min'],
                    'startijd': row['starttijd_min']
                    })   
        tijd_controle = pd.DataFrame(tijd_controle)
        
        return tijd_controle, waarschuwing
    
    tijd_controle, waarschuwing =eindtijd_groter_startijd(df_planning)  

    if not tijd_controle.empty:
        st.dataframe(tijd_controle)
    else:
        st.success('Everything is fine! No end time greater than starttime')    


                    # Controleer of de gefilterde data niet leeg is
        if not df_planning.empty:
            # Maak de Gantt Chart
            fig = px.timeline(
                df_planning, 
                x_start='starttijd datum', 
                x_end='eindtijd datum', 
                y='omloopnummer', 
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
# 15 minuten achter elkaar opladen bijhouden doormiddel van pdatetime had in de oude project al 
# Schema gemaakt met wanneer die die waarde benaderde en dat kun je dan invullen. 
# Hierdoor zal de rit er waarschijnlijk wel langer over doen en pas je de planning al aan wat lastig is 
# Dus moet een vorm vinden waardoor het alleen een checker is en het niet aan zou passen. 
# Trouwens de SOC telt nu al het opladen er bij dus zou alleen nog maar moeten checken of die 15 min oplaad

# Deel 3
# Zorgen dat de bus op dezelfde omloop blijft rijden en niet teleporteert van locatie naar locatie
# Hoe we dit moeten doen weet ik nog niet zeker. Mis is het handig om te checken of de rit tijden voldoen.
# Het omloop nummer mee te geven en te kijken of die bus ook logische route hanteert door dit te plotten per bus omloop?

 