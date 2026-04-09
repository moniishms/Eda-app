import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    st.dataframe(merged_df)
    st.write(f"Shape of merged DataFrame: {merged_df.shape}")
    st.title("Data cleaning Part")
    st.write("No of missing values in each column:")
    st.write(merged_df.isnull().sum())
    st.write("Data types of each column:")
    st.write(merged_df.dtypes)
    missing_columns=merged_df.columns[merged_df.isnull().any()]
    if len(missing_columns) > 0:
        st.write("Columns with missing values:")
        for col in missing_columns:
            st.write(f"{col}: {merged_df[col].isnull().sum()} missing values")
            if merged_df[col].dtype in ['float64', 'int64']:
                options = ["Mean", "Median", "Mode", "Drop Rows","Skip"]
            else:
                options = ["Mode", "Drop Rows","Skip"]
            option = st.selectbox(f"Cleaning for {col}",options,key=col)
            if option == "Mean":
                merged_df[col]=merged_df[col].fillna(merged_df[col].mean())  
            elif option == "Median":
                merged_df[col]=merged_df[col].fillna(merged_df[col].median())  
            elif option == "Mode":
                merged_df[col]=merged_df[col].fillna(merged_df[col].mode()[0])  
            elif option == "Drop Rows":
                merged_df = merged_df.drop(columns=[col]) 
    else:
        st.write("No columns with missing values.")
    st.write("Cleaned DataFrame:")
    st.dataframe(merged_df)
    csv = merged_df.to_csv(index=False).encode('utf-8')
    st.download_button(
    label="Download Cleaned Data",
    data=csv,
    file_name="cleaned_data.csv",
    mime="text/csv")
    st.title("EDA visualization:")
    col=st.selectbox("Select the column for your visualization",merged_df.columns)
    if merged_df[col].dtype in ["float64","int64"]:
        fig, ax=plt.subplots()
        sns.histplot(merged_df[col],kde=True,ax=ax)
        st.pyplot(fig)
    else:
        fig, ax=plt.subplots()
        sns.countplot(x=merged_df[col],ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    st.write("### Correlation Heatmap")
    numeric_df = merged_df.select_dtypes(include=['float64', 'int64'])
    if not numeric_df.empty:
        fig, ax = plt.subplots()
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.write("No numeric columns available") 