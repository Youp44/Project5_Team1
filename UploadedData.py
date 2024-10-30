import streamlit as st

def run():
    st.title("Geupload Data")

    # Check if 'df_planning' exists in session state
    if 'df_planning' in st.session_state:
        st.subheader("Planning Data")
        st.dataframe(st.session_state.df_planning.head(10))  # Access the DataFrame from session state

    # Check if 'df_tijden' exists in session state
    if 'df_tijden' in st.session_state:
        st.subheader("Tijden Data")
        st.dataframe(st.session_state.df_tijden.head(10))  # Access the DataFrame from session state

    # Check if 'df_afstanden' exists in session state
    if 'df_afstanden' in st.session_state:
        st.subheader("Afstand Data")
        st.dataframe(st.session_state.df_afstanden.head(10))  # Access the DataFrame from session state
