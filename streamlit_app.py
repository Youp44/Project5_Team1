import streamlit as st
import pandas as pd 
import numpy as np 


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
