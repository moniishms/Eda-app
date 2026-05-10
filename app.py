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
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
    if "cleaned_df" not in st.session_state:
        st.session_state.cleaned_df = merged_df.copy()
    st.write("Merged DataFrame:")
    st.dataframe(merged_df)
    st.write(f"Shape of merged DataFrame: {merged_df.shape}")
    st.title("Data cleaning Part")
    st.write("No of missing values in each column:")
    st.write(merged_df.isnull().sum())
    st.write("Data types of each column:")
    st.write(merged_df.dtypes)
    st.write("Columns available for cleaning:")
    st.write(f"Total columns: {len(merged_df.columns)}")
    
    # Select columns to clean - only from columns that exist in cleaned_df
    available_cols = [col for col in merged_df.columns if col in st.session_state.cleaned_df.columns]
    selected_columns = st.multiselect(
        "Select columns to clean (or select all):",
        options=available_cols,
        default=available_cols
    )
    
    if selected_columns:
        # Option to apply same method to all selected columns
        apply_to_all = st.checkbox("Apply same cleaning method to all selected columns")
        
        if apply_to_all:
            cleaning_method = st.selectbox("Select cleaning method for all selected columns:", 
                                          ["Mean", "Median", "Mode", "Drop Rows", "Skip"])
            
            if st.button("Apply cleaning"):
                for col in selected_columns:
                    if col not in st.session_state.cleaned_df.columns:
                        continue
                    
                    if cleaning_method == "Skip":
                        pass
                    elif cleaning_method == "Mean":
                        if st.session_state.cleaned_df[col].dtype in ['float64', 'int64']:
                            st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(st.session_state.cleaned_df[col].mean())
                    elif cleaning_method == "Median":
                        if st.session_state.cleaned_df[col].dtype in ['float64', 'int64']:
                            st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(st.session_state.cleaned_df[col].median())
                    elif cleaning_method == "Mode":
                        mode_values = st.session_state.cleaned_df[col].mode()
                        if len(mode_values) > 0:
                            st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(mode_values[0])
                    elif cleaning_method == "Drop Rows":
                        st.session_state.cleaned_df = st.session_state.cleaned_df.dropna(subset=[col])
                st.success("Cleaning applied!")
        else:
            # Individual column cleaning
            st.write("Or clean columns individually:")
            for idx, col in enumerate(selected_columns):
                with st.expander(f"{col} ({st.session_state.cleaned_df[col].isnull().sum()} missing values)"):
                    if st.session_state.cleaned_df[col].dtype in ['float64', 'int64']:
                        options = ["Mean", "Median", "Mode", "Drop Rows", "Skip"]
                    else:
                        options = ["Mode", "Drop Rows", "Skip"]

                    option = st.selectbox(f"Cleaning method for {col}", options, key=f"{idx}_{col}")

                    if col not in st.session_state.cleaned_df.columns:
                        st.warning(f"Column {col} no longer exists. Skipping.")
                    elif option == "Skip":
                        pass
                    elif option == "Mean":
                        st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(st.session_state.cleaned_df[col].mean())
                    elif option == "Median":
                        st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(st.session_state.cleaned_df[col].median())
                    elif option == "Mode":
                        mode_values = st.session_state.cleaned_df[col].mode()
                        if len(mode_values) > 0:
                            st.session_state.cleaned_df[col] = st.session_state.cleaned_df[col].fillna(mode_values[0])
                        else:
                            st.warning(f"No mode found for {col}. Skipping.")
                    elif option == "Drop Rows":
                        st.session_state.cleaned_df = st.session_state.cleaned_df.dropna(subset=[col])
    st.write("Cleaned DataFrame:")
    st.dataframe(st.session_state.cleaned_df)
    csv = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
    st.download_button(
    label="Download Cleaned Data",
    data=csv,
    file_name="cleaned_data.csv",
    mime="text/csv")