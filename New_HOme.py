import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def run():
    st.title("Analyze Bus Planning and Time Table")
    st.write("Welcome to the Home Page!")

    if 'df_planning' not in st.session_state:
        st.warning("Please upload both 'Bus Planning' and 'Time Table' in to the sidebar to continue.")
        return

    df_planning = st.session_state.df_planning
    df_afstand = st.session_state.df_afstanden
    df_tijden = st.session_state.df_tijden

    df_planning.rename(columns={'omloop nummer': 'omloopnummer'}, inplace=True)
    df_planning.rename(columns={'Unnamed: 0': 'index'}, inplace=True)

    def bereken_absolute_tijd(df):
        # Combineer tijd met datum voor julian date berekening
        df['starttijd'] = pd.to_datetime(df['starttijd datum'])
        df['eindtijd'] = pd.to_datetime(df['eindtijd datum'])

        # Zet om naar juliandate
        df['starttijd_jd'] = df['starttijd'].apply(lambda x: x.to_julian_date())
        df['eindtijd_jd'] = df['eindtijd'].apply(lambda x: x.to_julian_date())

        # Voeg kolommen in minuten toe (sinds begin van dataset)
        ref_start = df['starttijd_jd'].min()
        df['starttijd_min'] = (df['starttijd_jd'] - ref_start) * 24 * 60
        df['eindtijd_min'] = (df['eindtijd_jd'] - ref_start) * 24 * 60

        # Bereken reistijd correct
        df['reistijd_min'] = df['eindtijd_min'] - df['starttijd_min']

        # Sorteer correct op tijd en index
        df = df.sort_values(by=['starttijd_min', 'eindtijd_min', 'index']).reset_index(drop=True)
        return df

    df_planning = bereken_absolute_tijd(df_planning)
    df_planning = sorteer_planning_per_omloop(df_planning)

    verspringingen_df, waarschuwing = controleer_verspringende_locaties_per_omloop_met_datum(df_planning)

    if waarschuwing:
        st.warning("Bussen teleporteren onverwacht tussen locaties:")
        st.dataframe(verspringingen_df)
    else:
        st.success("Geen teleportaties gedetecteerd. Alle overgangen zijn logisch.")

    energieverbruik_per_km = st.number_input("Energy consumption per km (kWh)", min_value=0.1, value=2.5)
    max_verbruik = st.number_input("Maximal consumption per bus (kWh)", min_value=1.0, value=270.0)
    min_waarde_SOC = st.number_input("Minimal SOC-value", min_value=1.0, value=30.0)

    df_planning['starttijd'] = pd.to_datetime(df_planning['starttijd'], format='%H:%M:%S')
    df_planning['eindtijd'] = pd.to_datetime(df_planning['eindtijd'], format='%H:%M:%S')

    def controleer_soc_grenzen(df_planning, df_afstand, energieverbruik_per_km, MAX_waarde_SOC, min_waarde_SOC):
        soc_per_omloop = {}
        df_planning['SOC'] = 0
        overschrijdingen = []
        fouten = False
        warning = False

        for omloop in df_planning['omloopnummer'].unique():
            SOC = MAX_waarde_SOC
            soc_waarden = []

            for i, row in df_planning[df_planning['omloopnummer'] == omloop].iterrows():
                if row['activiteit'] == 'opladen':
                    SOC += abs(row['energieverbruik'])
                    SOC = min(SOC, MAX_waarde_SOC)
                else:
                    match = df_afstand[
                        (df_afstand['startlocatie'] == row['startlocatie']) &
                        (df_afstand['eindlocatie'] == row['eindlocatie']) &
                        ((df_afstand['buslijn'] == row['buslijn']) | df_afstand['buslijn'].isna())
                    ]
                    afstand_m = match.iloc[0]['afstand in meters'] if not match.empty else 0
                    afstand_km = afstand_m / 1000
                    SOC -= afstand_km * energieverbruik_per_km

                soc_waarden.append(SOC)
                df_planning.at[i, 'SOC'] = SOC

                if SOC < min_waarde_SOC:
                    if not warning:
                        st.error("SOC below minimum value!")
                        warning = True
                    fouten = True
                    overschrijdingen.append({'rij_index': i, 'omloopnummer': omloop, 'SOC': SOC})

            soc_per_omloop[omloop] = soc_waarden

        return pd.DataFrame(overschrijdingen), fouten, soc_per_omloop

    df_overschrijdingen, fouten, soc_per_omloop = controleer_soc_grenzen(
        df_planning, df_afstand, energieverbruik_per_km, max_verbruik, min_waarde_SOC
    )

    if fouten:
        with st.expander("Click for more information"):
            st.write("The following rows have errors or violations:")
            st.dataframe(df_overschrijdingen)
    else:
        st.success('Alles in orde! Geen SOC-overschrijdingen.')

    omloop_selectie = st.selectbox("Selecteer een omloopnummer om SOC te bekijken", list(soc_per_omloop.keys()))

    fig, ax = plt.subplots()
    ax.plot(range(len(soc_per_omloop[omloop_selectie])), soc_per_omloop[omloop_selectie], label=f'Theoretische SOC waarde - Omloop {omloop_selectie}', linestyle='-', marker='o')
    ax.axhline(y=min_waarde_SOC, color='r', linestyle='--', label=f'Minimale SOC ({int(min_waarde_SOC)})')
    ax.axhline(y=max_verbruik, color='r', linestyle='--', label=f'Maximale SOC ({int(max_verbruik)})')
    ax.set_xlabel("Index")
    ax.set_ylabel("SOC waarde (kWh)")
    ax.set_title(f"Theoretische SOC waarde voor Omloop {omloop_selectie}")
    ax.legend(loc="lower right")
    st.pyplot(fig)

    def controleer_oplaadtijd(df, min_oplaadtijd):
        warning = False
        korte_oplaadtijden = []

        for i, row in df.iterrows():
            if row['energieverbruik'] <= 0:
                oplaad_tijd = (row['eindtijd'] - row['starttijd']).total_seconds() / 60
                if oplaad_tijd <= min_oplaadtijd:
                    if not warning:
                        st.error(f'Charging time is less than {min_oplaadtijd} minutes!')
                        warning = True
                    korte_oplaadtijden.append({
                        'rij_index': i,
                        'starttijd': row['starttijd'].strftime('%H:%M:%S'),
                        'eindtijd': row['eindtijd'].strftime('%H:%M:%S'),
                        'energieverbruik': row['energieverbruik'],
                        'oplaadtijd': oplaad_tijd
                    })

        if not warning:
            st.success(f'Everything is fine! No charging times shorter than {min_oplaadtijd} minutes.')

        return pd.DataFrame(korte_oplaadtijden), warning

    min_oplaadtijd = st.number_input("Minimal charge time", min_value=0.1, value=15.0)
    df_korte_oplaadtijden, waarschuwing = controleer_oplaadtijd(df_planning, min_oplaadtijd)
    if not df_korte_oplaadtijden.empty:
        st.dataframe(df_korte_oplaadtijden)

    def check_dienst_ritten_reistijd(df_planning, df_afstand):
        dienst_ritten = df_planning[df_planning['activiteit'] == 'dienst rit']
        dienst_ritten['starttijd'] = pd.to_datetime(dienst_ritten['starttijd'])
        dienst_ritten['eindtijd'] = pd.to_datetime(dienst_ritten['eindtijd'])
        dienst_ritten['reistijd_min'] = (dienst_ritten['eindtijd'] - dienst_ritten['starttijd']).dt.total_seconds() / 60

        invalid_rides = []
        for _, row in dienst_ritten.iterrows():
            match = df_afstand[(df_afstand['startlocatie'] == row['startlocatie']) &
                               (df_afstand['eindlocatie'] == row['eindlocatie']) &
                               (df_afstand['buslijn'] == row['buslijn'])]
            if not match.empty:
                min_time, max_time = match.iloc[0]['min reistijd in min'], match.iloc[0]['max reistijd in min']
                if not (min_time <= row['reistijd_min'] <= max_time):
                    invalid_rides.append(row.to_dict())

        return pd.DataFrame(invalid_rides)

    invalid_rides_df = check_dienst_ritten_reistijd(df_planning, df_afstand)
    if not invalid_rides_df.empty:
        st.warning("De volgende dienst ritten vallen buiten de reistijdslimieten:")
        st.dataframe(invalid_rides_df)
    else:
        st.success("Alle dienst ritten vallen binnen de reistijdslimieten.")

    def eindtijd_groter_starttijd(df):
        waarschuwing = False
        tijd_controle = []
        for i, row in df.iterrows():
            if row['eindtijd_min'] < row['starttijd_min']:
                if not waarschuwing:
                    st.warning("Eindtijd ligt vóór starttijd (zonder middernacht)")
                    waarschuwing = True
                tijd_controle.append({
                    'omloopnummer': row['omloopnummer'],
                    'index_huidige_rij': row['index'],
                    'eindtijd': row['eindtijd_min'],
                    'starttijd': row['starttijd_min']
                })
        return pd.DataFrame(tijd_controle), waarschuwing

    tijd_controle, waarschuwing = eindtijd_groter_starttijd(df_planning)
    if not tijd_controle.empty:
        st.dataframe(tijd_controle)
    else:
        st.success("Everything is fine! No end time greater than start time")

    if not df_planning.empty:
        fig = px.timeline(
            df_planning,
            x_start='starttijd datum',
            x_end='eindtijd datum',
            y='omloopnummer',
            color='activiteit'
        )
        fig.update_yaxes(tickmode='linear', tick0=1, dtick=1, autorange='reversed')
        fig.update_xaxes(tickformat='%H:%M')
        fig.update_layout(title="Gantt Chart for Bus Line")
        st.plotly_chart(fig)
    else:
        st.write("No data available for bus line")

def sorteer_planning_per_omloop(df):
    df = df.copy()
    df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
    df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])
    df = df.sort_values(by=['omloopnummer', 'starttijd datum', 'eindtijd datum']).reset_index(drop=True)
    df['index'] = df.index
    return df

def controleer_verspringende_locaties_per_omloop_met_datum(df):
    df = df.copy()
    verspringingen = []
    waarschuwing = False

    df['startlocatie'] = df['startlocatie'].str.strip().str.lower()
    df['eindlocatie'] = df['eindlocatie'].str.strip().str.lower()

    for omloop in df['omloopnummer'].unique():
        df_omloop = df[df['omloopnummer'] == omloop].sort_values(by='index')
        vorige_rij = None

        for _, huidige_rij in df_omloop.iterrows():
            if vorige_rij is not None:
                mag_verspringen = (
                    pd.to_datetime(huidige_rij['starttijd datum']).date() >
                    pd.to_datetime(vorige_rij['starttijd datum']).date()
                )

                if (vorige_rij['eindlocatie'] != huidige_rij['startlocatie']) and not mag_verspringen:
                    verspringingen.append({
                        'omloopnummer': omloop,
                        'index_huidige_rij': huidige_rij['index'],
                        'vorige_eindlocatie': vorige_rij['eindlocatie'],
                        'huidige_startlocatie': huidige_rij['startlocatie'],
                        'starttijd_datum': huidige_rij['starttijd datum'],
                        'vorige_starttijd_datum': vorige_rij['starttijd datum']
                    })
                    waarschuwing = True
            vorige_rij = huidige_rij

    return pd.DataFrame(verspringingen), waarschuwing
