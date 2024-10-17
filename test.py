import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Sidebar layout for uploading files
st.sidebar.title("Streamlit")

# File Uploads for Omloopplanning and Dienstregeling
df_planning = st.sidebar.file_uploader("Upload Omloopplanning", type=["xlsx"])
df_dienstregeling = st.sidebar.file_uploader("Upload Dienstregeling", type=["xlsx"])

# Display statuses and issues
st.title("Mogelijke Verbeteringspunten")
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

# Section for Error Explanation
st.markdown("### Uitleg fout")
st.write("")
st.write("")

# Section for Improved Version
st.markdown("### Verbeterde versie")
st.write("")

# If files are uploaded, process and display the merged data
if df_planning and df_dienstregeling:
    df_planning = pd.read_excel(df_planning)
    df_tijden = pd.read_excel(df_dienstregeling)
    
    # Convert start and end times to datetime format
    df_planning['starttijd'] = pd.to_datetime(df_planning['starttijd'], format='%H:%M:%S')
    df_planning['eindtijd'] = pd.to_datetime(df_planning['eindtijd'], format='%H:%M:%S')
    
    # Merge and calculate time differences
    df_merged = pd.merge(df_planning, df_tijden, on='buslijn')
    df_merged['verschil_in_min'] = (df_merged['eindtijd'] - df_merged['starttijd']).dt.total_seconds() / 60
    
    # Check if times are within the min and max travel times
    df_merged['correct'] = (df_merged['verschil_in_min'] >= df_merged['min_reistijd_in_min']) & \
                           (df_merged['verschil_in_min'] <= df_merged['max_reistijd_in_min'])
    
    # Filter for incorrect entries
    df_fouten = df_merged[df_merged['correct'] == False]
    
    # Output incorrect rows
    st.write("Fouten in Omloopplanning:")
    st.dataframe(df_fouten)

# Bus Schedule Plot
def plot_bus_schedule(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    route_labels = {}
    
    for bus in df['omloop nummer'].unique():
        bus_df = df[df['omloop nummer'] == bus]
        for _, row in bus_df.iterrows():
            reistijd = row['eindtijd'] - row['starttijd']
            if row['Route'] not in route_labels:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black', label=row['Route'])
                route_labels[row['Route']] = True
            else:
                ax.barh(bus, reistijd, left=row['starttijd'], color=row['Kleur'], edgecolor='black')
    
    ax.set_xlabel('Tijd (uren)')
    ax.set_ylabel('Busomloop')
    ax.set_title('Schema van busomlopen en routes over tijd')
    ax.set_yticks(df['omloop nummer'].unique())
    ax.set_xlim([df['starttijd'].min(), df['eindtijd'].max()])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xticks(pd.date_range(start=df['starttijd'].min(), end=df['eindtijd'].max(), freq='2H'))
    ax.legend(title="Route", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

if df_planning is not None:
    # Prepare the data for plotting
    df_planning['Route'] = df_planning['startlocatie'] + "-" + df_planning["eindlocatie"]
    route_kleuren = {
        'ehvgar-ehvbst': 'red', 'ehvapt-ehvbst': 'blue', 'ehvbst-ehvapt': 'green', 
        'ehvgar-ehvapt': 'purple', 'ehvgar-ehvgar': 'orange', 'ehvbst-ehvgar': 'cyan',
        'ehvbst-ehvbst': 'magenta', 'ehvapt-ehvapt': 'pink', 'ehvapt-ehvgar': 'brown'
    }
    df_planning['Kleur'] = df_planning['Route'].map(route_kleuren).fillna('gray')
    
    # Plot the schedule
    plot_bus_schedule(df_planning)
