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



    def controleer_soc_grenzen(df_planning, MAX_waarde_SOC=270, min_waarde_SOC=30):
        """
        LET OP ER MOET NOG SORT OP TIJD/INDEX WORDEN TOEGEVOEGD
        Controleert de SOC-waarden op overschrijdingen van de grenswaarden.
    
        Parameters:
        - df_planning (pd.DataFrame): De input DataFrame met de planning en energieverbruik.
        - MAX_waarde_SOC (float): De maximale SOC-waarde.
        - min_waarde_SOC (float): De minimale SOC-waarde.
        
        Returns:
        - df_overschrijdingen (pd.DataFrame): DataFrame met rijen waarin de SOC wordt overschreden.
        """
        SOC = MAX_waarde_SOC
        vorige_omloop = None
        warning = False
        fouten = False
        # Lijst om overschrijdingsgevallen op te slaan
        overschreidingen = []

        for i, row in df_planning.iterrows():
            # Reset SOC bij een nieuwe omloop
            if row['omloopnummer'] != vorige_omloop:
                SOC = MAX_waarde_SOC
                vorige_omloop = row['omloopnummer']

            # Energieverbruik eraf trekken
            SOC -= row['energieverbruik']

            # Controleer de grenzen
            if SOC < min_waarde_SOC or SOC > MAX_waarde_SOC:
                if not warning:
                    st.warning('Gaat niet goed: SOC overschrijdt de grenzen!')
                    warning = True
                fouten = True
                overschreidingen.append({
                    'rij_index': i,
                    'omloopnummer': row['omloopnummer'],
                    'energieverbruik': row['energieverbruik'],
                    'SOC': SOC
                })

            # Voeg SOC-waarde toe aan de DataFrame
            df_planning.loc[i, 'SOC'] = SOC

        # Maak een DataFrame met alleen overschrijdingsgevallen
        df_overschrijdingen = pd.DataFrame(overschreidingen)
    
        return df_overschrijdingen, fouten 
    df_overschrijdingen, fouten = controleer_soc_grenzen(df_planning)

# Toon de resultaten op basis van fouten
    if fouten:
        st.dataframe(df_overschrijdingen)  # Alleen tonen als er overschrijdingen zijn
    else:
        st.success('Alles in orde! Geen SOC-overschrijdingen.')

        """
        Dit deel moet nog aangepast worden voor wat en wanneer we willen checekn 
        """
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
                        st.warning(f'Gaat niet goed: Oplaadtijd is korter dan {min_oplaadtijd} minuten!')
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
            st.success(f'Alles in orde! Geen opladingen korter dan {min_oplaadtijd} minuten.')

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
                        st.warning("Bus verspringt van locatie!")
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
        st.success("Alles in orde! Geen verspringende locaties.")



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
        st.success('Alles in orde! Geen eindtijden groter dan starttijden')    
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

 