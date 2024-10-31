import streamlit as st
import pandas as pd

# Set the title of the app as the first command
st.set_page_config(page_title="Multi-Page App", page_icon=":guardsman:", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("Select a page below")

# Define the pages
pages = {
    'Home': 'V',
    'Improved Scheduling': 'ImprovedScheduling',
    'Uploaded Data': 'UploadedData'
}

# Create a radio button for page selection
selection = st.sidebar.radio('Go to', list(pages.keys()))

# Import and run the selected page
if selection == "Home":
    from Home import run  # Ensure Home.py has a run() function
    run()
elif selection == "Improved Scheduling":
    from ImprovedScheduling import run  # Ensure ImprovedScheduling.py has a run() function
    run()
elif selection == "Uploaded Data":
    from UploadedData import run  # Ensure UploadedData.py has a run() function
    run()

uploaded_Omloopsplanning = st.sidebar.file_uploader("Upload 'Omloopsplanning'", type=["xlsx", "xls"])
uploaded_Dienstregeling = st.sidebar.file_uploader("Upload 'Dienstregeling'", type=["xlsx", "xls"])

if uploaded_Omloopsplanning is not None and uploaded_Dienstregeling is not None:
    try:
        # Load files into DataFrames
        df_planning = pd.read_excel(uploaded_Omloopsplanning)
        df_tijden = pd.read_excel(uploaded_Dienstregeling, sheet_name='Dienstregeling')
        df_afstanden = pd.read_excel(uploaded_Dienstregeling, sheet_name='Afstandsmatrix')

        # Store DataFrames in session state
        st.session_state.df_planning = df_planning
        st.session_state.df_tijden = df_tijden
        st.session_state.df_afstanden = df_afstanden
        
        st.success("Bestanden succesvol geüpload!")

    except Exception as e:
        st.error("Er is een fout opgetreden bij het verwerken van de bestanden: " + str(e))
else:
    st.warning("Upload zowel 'Omloopsplanning' als 'Dienstregeling' om door te gaan.")