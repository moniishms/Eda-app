import streamlit as st
import pandas as pd

st.title("Excel File Upload and Viewer")
st.write("Write the number of files u want to view")

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df)

    st.subheader("Dataset Info")
    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])


    