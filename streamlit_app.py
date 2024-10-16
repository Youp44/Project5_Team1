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
    
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Uitleg fout')
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('# Verbeterde versie')

image_url = https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.cleanpng.com%2Fpng-transdev-business-transport-super-advice-veolia-ra-5486609%2F&psig=AOvVaw079_y6WUOs7jHob1Vi1Kt0&ust=1729174366653000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCPjBpNGKk4kDFQAAAAAdAAAAABAE

st.image(image_url)