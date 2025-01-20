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

    # Stukje met 'boolean index maken om hierbij aan te geven of de planning voldoet'
    #st.success('Wow')
    #st.warning('Je bus omloop voldoet niet aan de omgangs eisen')


    def controleer_soc_grenzen(df_planning, MAX_waarde_SOC=770, min_waarde_SOC=30):
        """
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

 