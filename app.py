import streamlit as st
import pandas as pd

st.title("Excel File Upload and Viewer")
num=st.number_input("Enter the number of files to upload",min_value=1, max_value=5,step=1)

uploaded_files = []
data_frames=[]
for i in range(num):
    uploaded_file = st.file_uploader(f"Upload Excel file {i+1}", type=["xlsx","csv"], key=f"file_{i}")
    if uploaded_file is not None:
        uploaded_files.append(uploaded_file)

for files in uploaded_files:
    if files.name.endswith(".xlsx"):
        df = pd.read_excel(files)
    elif files.name.endswith(".csv"):
        df = pd.read_csv(files)
    data_frames.append(df)

if data_frames:
    merge_type = st.selectbox("Select merge type", ["Row-wise", "Column-wise"])
    if merge_type == "Row-wise":
        merged_df = pd.concat(data_frames, ignore_index=True)
    else:
        merged_df = pd.concat(data_frames, axis=1)
    st.write("Merged DataFrame:")
    st.dataframe(merged_df.head(15))
    