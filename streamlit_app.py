import streamlit as st
import pandas as pd 
import numpy as np 


st.title("Project 5 Omloopsplanning ")
df = (pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
#of gewoon met normale df 
df
st.table(df)

dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))

st.dataframe(dataframe.style.highlight_max(axis=0))
# dit werkt dus voor correlatie


dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))
st.table(dataframe)
# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

import streamlit as st

left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button('Press me!')


import time

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'

import streamlit as st

# als je hier een loop van maakt voor je drie functie.
# Zo kan je Status I maken in een list met de correcte namen, 
# En het algemeen maken door de termen good en improve gebruiken 
Bus ="good"
Omloop = 'good'
Rit = "good"
status = ['Bus', 'Omloop', 'Rit']
for i in len(status):
    if i == "good":
        # Display a success indicator with custom styling
        st.markdown('<div style="color: green;">✅️ Status is good</div>', unsafe_allow_html=True)
    elif i == "improve":
        # Display an improvement indicator with custom styling
        st.markdown('<div style="color: orange;">🔶 Status can be improved</div>', unsafe_allow_html=True)
    else:
        # Display a failure indicator with custom styling
        st.markdown('<div style="color: red;">❌ Status is wrong</div>', unsafe_allow_html=True)
