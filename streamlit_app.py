import streamlit as st
import pandas as pd 
import numpy as np 

df = (pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
#of gewoon met normale df 
st.table(df)
st.title("Project 5 Omloopsplanning ")




