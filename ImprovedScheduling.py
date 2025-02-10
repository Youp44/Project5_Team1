import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def plot_gantt_chart(df, title):
    fig = px.timeline(
        df, 
        x_start='starttijd datum', 
        x_end='eindtijd datum', 
        y='omloop nummer', 
        color='activiteit'
    )
    fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
    fig.update_layout(title=dict(text=title, font=dict(size=30)))
    fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
    st.plotly_chart(fig)

def run():
    st.title("Analyze Bus Planning and Time Table")
    st.write("Welcome to the Home Page!")

    # Check if the necessary DataFrames are stored in session_state
    if 'df_planning' not in st.session_state or 'df_afstanden' not in st.session_state:
        st.error("There is no uploaded data. Upload the files in the sidebar.")
        return
    
    df_planning = st.session_state.df_planning
    df_afstand = st.session_state.df_afstanden

    # Input for maximum energy consumption
    max_verbruik = st.number_input("Maximal consumption per bus (kWh)", min_value=1.0, value=270.0)
    
    # Check if df_planning and df_afstanden are not empty
    if df_planning.empty:
        st.error("df_planning is empty!")
        return
    if df_afstand.empty:
        st.error("df_afstand is empty!")
        return

    # Add a selectbox for loop number
    unique_omloop_nummers = df_planning['omloop nummer'].unique()
    selected_omloop = st.selectbox("Choose a bus number", unique_omloop_nummers)

    # Filter on the selected loop number
    df_selected_omloop = df_planning[df_planning['omloop nummer'] == selected_omloop]

    if not df_selected_omloop.empty:
        # Bereken cumulatief energieverbruik
        df_selected_omloop['cumulatief_energieverbruik'] = df_selected_omloop['energieverbruik'].cumsum()

        # Maximale verbruiksdrempel
        max_verbruik_line = max_verbruik

        # Maak een nieuwe lijst voor de aangepaste cumulatieve energieverbruik
        aangepaste_cumulatief = []
        cumulatieve_lading = 0  # Houdt de cumulatieve waarde na reset

        # Loop door de cumulatieve waarden
        for i in range(len(df_selected_omloop)):
            cumulatieve_lading += df_selected_omloop['energieverbruik'].iloc[i]

            if cumulatieve_lading > max_verbruik_line:
                cumulatieve_lading = max_verbruik_line  # Beperk tot max_verbruik_line
            
            aangepaste_cumulatief.append(cumulatieve_lading)

            if cumulatieve_lading == max_verbruik_line:
                cumulatieve_lading = 0  # Begin opnieuw met opladen

        # Zet de aangepaste cumulatieve waarden terug in de DataFrame
        df_aangepast = pd.DataFrame({
            'index': range(len(aangepaste_cumulatief)),
            'cumulatief_energieverbruik': aangepaste_cumulatief
        })

        # Plot de resultaten
        fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
        ax.plot(df_aangepast['index'], df_aangepast['cumulatief_energieverbruik'], color='green', linewidth=2)
        ax.axhline(y=max_verbruik_line, color='purple', linestyle='--', label='Max Consumption (kWh)')
        ax.set_title(f'Energy Consumption and Cumulative for Bus Number {selected_omloop}')
        ax.set_xlabel('Index')
        ax.set_ylabel('Energy Consumption (kWh)')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
    
    # Gantt Chart for existing schedule
    plot_gantt_chart(df_planning, 'Gantt Chart for Bus Line')

    # Load improved schedule for comparison
    try:
        improved_schedule = pd.read_excel('/mnt/data/omloopplanning (2).xlsx')
        st.write("### Improved Bus Planning")
        st.dataframe(improved_schedule.head(10))
    
        # Gantt Chart for improved schedule
        plot_gantt_chart(improved_schedule, 'Gantt Chart for Improved Bus Line')
    except Exception as e:
        st.error(f"Failed to load improved schedule: {e}")

if __name__ == "__main__":
    run()
