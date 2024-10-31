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

    if not df_selected_omloop.empty:
        # Calculate expected energy consumption
        df_selected_omloop['verwacht_energieverbruik'] = df_selected_omloop['afstand_km'] * energieverbruik_per_km

        # Calculate cumulative sum for actual and expected energy consumption
        df_selected_omloop['cumulatief_energieverbruik'] = df_selected_omloop['energieverbruik'].cumsum()
        df_selected_omloop['cumulatief_verwacht_energieverbruik'] = df_selected_omloop['verwacht_energieverbruik'].cumsum()

        # Determine the maximum consumption line
        max_verbruik_line = max_verbruik

        # Determine line colors based on consumption
        kleur_actual = 'red' if df_selected_omloop['cumulatief_energieverbruik'].max() > max_verbruik_line else 'green'
        kleur_verwacht = 'red' if df_selected_omloop['cumulatief_verwacht_energieverbruik'].max() > max_verbruik_line else 'blue'

        # Plot the results
        plt.figure(figsize=(12, 6),dpi=100)

        # Plot cumulative actual energy consumption
        plt.plot(df_selected_omloop.index, df_selected_omloop['cumulatief_energieverbruik'], 
            label='Cumulative Energie Consumption (Actual)', 
            color=kleur_actual, linewidth=2)

        # Plot cumulative expected energy consumption
        plt.plot(df_selected_omloop.index, df_selected_omloop['cumulatief_verwacht_energieverbruik'], 
            label='Cumulative Energie Consumption (Expected)', 
            color=kleur_verwacht, linewidth=2)

        # Add a horizontal line for max consumption
        plt.axhline(y=max_verbruik_line, color='purple', linestyle='--', label='Max Consumption (kWh)')

        # Title and labels
        plt.title(f'Energy Consumption and Cumulative for Bus Number {selected_omloop}')
        plt.xlabel('Index')
        plt.ylabel('Energy Consumption (kWh)')
        plt.grid(True)
        plt.legend()

        # Show the plot in Streamlit
        st.pyplot(plt)

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

        # Voeg een selectievak toe voor lijnkeuze
        lijn_keuze = st.selectbox("Choose a bus line", options=[400, 401, '400 & 401'])

        # Filter de gegevens op de geselecteerde lijn en genereer de Gantt-diagram als op de knop wordt geklikt
        if lijn_keuze == '400 & 401':
        # Filter het dataframe voor beide lijnen 400 en 401
            df_filtered = df_planning[df_planning['buslijn'].isin([400, 401])]
        else:
            # Filter voor de geselecteerde lijn (400 of 401)
            df_filtered = df_planning[df_planning['buslijn'] == lijn_keuze]

    
            # Controleer of de gefilterde data niet leeg is
        if not df_filtered.empty:
            # Maak de Gantt Chart
            fig = px.timeline(
                df_filtered, 
                x_start='starttijd datum', 
                x_end='eindtijd datum', 
                y='omloop nummer', 
                color='activiteit'
            )
            fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed', showgrid=True, gridcolor='lightgray', gridwidth=1)
            fig.update_xaxes(tickformat='%H:%M', showgrid=True, gridcolor='lightgray', gridwidth=1)
            fig.update_layout(
                title=dict(text=f'Gantt Chart for Bus Line {lijn_keuze}', font=dict(size=30))
            )
            fig.update_layout(legend=dict(yanchor='bottom', y=0.01, xanchor='right', x=0.999))
    
            # Toon de plot in Streamlit
            st.plotly_chart(fig)
        else:
            st.write(f"No data available for bus line {lijn_keuze}")
if __name__ == "__main__":
    run()
