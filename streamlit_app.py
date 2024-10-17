import streamlit as st
import pandas as pd 
import numpy as np 

df_planning =pd.read_excel('omloopplanning.xlsx')
df = pd.read_excel('Connexxion data - 2024-2025.xlsx')
df_tijden = pd.read_excel('Connexxion data - 2024-2025 - kopie.xlsx')

st.title("Project 5 Omloopsplanning ")

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

st.markdown(
    """
    <div style="background-color: lightgreen; padding: 20px; border-radius: 10px;">
        <h3 style="color: white;">This is a light green block</h3>
        <p>This section is styled with a light green background and white text.</p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color: lightblue; padding: 20px; border-radius: 10px;">
        <h3 style="color: white;">This is a light blue block</h3>
        <p>This section is styled with a light blue background and white text.</p>
    </div>
    """, 
    unsafe_allow_html=True)
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

<<<<<<< HEAD

import pandas as pd

def calculate_energy_consumption(df_planning, df_tijden, energieverbruik_KWH=2.5, max_verbruik=364.5):
    # Koppel de afstanden aan de planning op basis van startlocatie, eindlocatie en buslijn (indien van toepassing)
    def find_afstand(row, df_tijden):
        # Filteren op basis van startlocatie, eindlocatie en eventueel buslijn
        match = df_tijden[
            (df_tijden['startlocatie'] == row['startlocatie']) &
            (df_tijden['eindlocatie'] == row['eindlocatie']) &
            ((df_tijden['buslijn'] == row['buslijn']) | df_tijden['buslijn'].isna())
        ]
        
        # Als er een match is, haal de afstand in meters op, anders 0
        return match.iloc[0]['afstand in meters'] if not match.empty else 0

    # Voeg de afstanden toe aan de planning DataFrame
    df_planning['afstand_meters'] = df_planning.apply(lambda row: find_afstand(row, df_tijden), axis=1)
    df_planning['afstand_km'] = df_planning['afstand_meters'] / 1000

    # Groepeer de afstanden per omloop nummer en bereken de totale kilometers per omloop
    totaal_km_per_omloop = df_planning.groupby('omloop nummer')['afstand_km'].sum()

    # Stel een cumulatieve variabele voor energieverbruik in
    cumulatief_verbruik = 0
    overschrijdingen = []  # Lijst om omloop nummer en tijd van overschrijding bij te houden

    # Ga door elke rij in de planning
    for index, row in df_planning.iterrows():
        # Als de activiteit geen 'opladen' is, tel energieverbruik erbij op
        if row['activiteit'] != 'opladen':
            cumulatief_verbruik += row['energieverbruik']
        # Als de activiteit 'opladen' is, trek energieverbruik af (opladen is negatief)
        else:
            cumulatief_verbruik += row['energieverbruik']  # energieverbruik bij opladen is al negatief
        
        # Controleer of het cumulatieve energieverbruik boven de 364.5 kWh komt
        if cumulatief_verbruik > max_verbruik:
            overschrijdingen.append({
                'omloop': row['omloop nummer'],  # Omloop nummer
                'tijd': row['eindtijd'],         # Tijd van overschrijding
                'totaal_verbruik': cumulatief_verbruik  # Huidig totaalverbruik
            })

    # Print overschrijdingen
    if overschrijdingen:
        for oversch in overschrijdingen:
            tijd = oversch['tijd'].time()  # Haal alleen de tijd op
            print(f"Energieverbruik overschreden in omloop {oversch['omloop']} om {tijd}, totaal verbruik: {oversch['totaal_verbruik']} kWh")
    else:
        print(f"Energieverbruik bleef onder de {max_verbruik} kWh, eindverbruik: {cumulatief_verbruik} kWh")

    # Maximaal energieverbruik per omloop berekenen
    max_b_per_omloop = {}

    for omloop_nummer in df_planning['omloop nummer'].unique():
        # Filteren op huidige omloop nummer
        df_omloop = df_planning[df_planning['omloop nummer'] == omloop_nummer]
        
        # Sorteren op 'starttijd'
        df_omloop = df_omloop.sort_values(by='starttijd')
        
        # Lijst van energieverbruik per omloop nummer
        energieverbruik = df_omloop['energieverbruik'].tolist()
         
        k = []
        max_b = 0
        for i in energieverbruik:
            k.append(i)
            b = sum(k)
            
            # Update max_b als de nieuwe som van 'b' groter is
            if b > max_b:
                max_b = b
            
            # Breek als b >= 364.5, maar we willen nog steeds max_b opslaan
            if b >= max_verbruik:
                print(f"{b} overschrijding voor omloop nummer {omloop_nummer}")
                break

        # Opslaan van het maximale b voor de huidige omloop nummer
        max_b_per_omloop[omloop_nummer] = max_b

    # Het resultaat: Dictionary met maximale b per omloop nummer
    sorted_dict = pd.DataFrame(sorted(max_b_per_omloop.items()), columns=['Omloop Nummer', 'Max B'])

    # Bereken totaal energieverbruik per omloop zonder laden
    totaal_energieverbruik_per_omloop_zonderladen = totaal_km_per_omloop * energieverbruik_KWH
    
    return sorted_dict, totaal_energieverbruik_per_omloop_zonderladen

# Voorbeeld van hoe je de functie aanroept
# df_planning, df_tijden zijn verondersteld te zijn gedefinieerd en gevuld met gegevens.
#sorted_max_b_per_omloop, totaal_energieverbruik = 
st.table(calculate_energy_consumption(df_planning, df_tijden))
# Print de resultaten
#print("Maximaal energieverbruik per omloop:")
#print(sorted_max_b_per_omloop)

#print("Totaal energieverbruik per omloop zonder laden:")
#print(totaal_energieverbruik)
=======
def plot_bus_schedule(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Houd bij welke routes al een label hebben om dubbele labels in de legenda te vermijden
    route_labels = {}
    
    # Itereer over de busomlopen
    for bus in df['omloop nummer'].unique():
        bus_df = df[df['omloop nummer'] == bus]
        for _, row in bus_df.iterrows():
            # Bereken de reistijd van de bus op de route
            reistijd = row['eindtijd'] - row['starttijd']
            
            # Voeg een balk toe voor de reistijd van de bus op de route
            if row['Route'] not in route_labels:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black', label=row['Route'])
                route_labels[row['Route']] = True
            else:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black')
    
    # Labels en opmaak
    ax.set_xlabel('Tijd (uren)')
    ax.set_ylabel('Busomloop')
    ax.set_title('Schema van busomlopen en routes over tijd')
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

    # Voeg een legenda toe met de routes
    ax.legend(title="Route", bbox_to_anchor=(1.05, 1), loc='upper left')  # Plaats de legenda buiten de grafiek
    
    plt.grid(axis='x', linestyle='--', alpha=0.7)  # Voeg een grid toe voor betere leesbaarheid
    plt.tight_layout()  # Zorg dat alles netjes in beeld past
    plt.show()


df_planning['starttijd'] = pd.to_datetime(df_planning['starttijd'], format='%H:%M')
df_planning['eindtijd'] = pd.to_datetime(df_planning['eindtijd'], format='%H:%M')

# Plot het resultaat
plot_bus_schedule(df_planning)
>>>>>>> 9b4d8d6caac32e1ca593603e26fb838363e2fe23
st.markdown('# Miauw snuiven kan toch gewoon op een zaterdag ')