import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Excel File Upload and Viewer")

num = st.number_input(
    "Enter the number of files to upload",
    min_value=1,
    max_value=5,
    step=1
)

uploaded_files = []
data_frames = []
available_cols = []

for i in range(num):

    uploaded_file = st.file_uploader(
        f"Upload Excel file {i+1}",
        type=["xlsx", "csv"],
        key=f"file_{i}"
    )

    if uploaded_file is not None:
        uploaded_files.append(uploaded_file)

for files in uploaded_files:

    try:

        if files.name.endswith(".xlsx"):
            df = pd.read_excel(files)

        elif files.name.endswith(".csv"):
            df = pd.read_csv(files)

        data_frames.append(df)

    except Exception as e:

        st.error(f"Error reading {files.name}: {e}")

if data_frames:

    merge_type = st.selectbox(
        "Select merge type",
        ["Row-wise", "Column-wise"]
    )

    if merge_type == "Row-wise":

        merged_df = pd.concat(
            data_frames,
            ignore_index=True
        )

    else:

        row_counts = [len(df) for df in data_frames]

        if len(set(row_counts)) != 1:

            st.error(
                "All files must have same number of rows for column-wise merge."
            )

            st.stop()

        merged_df = pd.concat(
            data_frames,
            axis=1
        )

        duplicate_cols = merged_df.columns[
            merged_df.columns.duplicated()
        ].tolist()

        if duplicate_cols:

            st.warning(
                f"Duplicate columns removed: {duplicate_cols}"
            )

        merged_df = merged_df.loc[
            :,
            ~merged_df.columns.duplicated()
        ]

    file_fingerprint = [f.name for f in uploaded_files]

    if st.session_state.get("file_fingerprint") != file_fingerprint:

        st.session_state.file_fingerprint = file_fingerprint

        st.session_state.cleaned_df = merged_df.copy()

    st.write("Merged DataFrame:")
    st.dataframe(merged_df)

    st.write(
        f"Shape of merged DataFrame: {merged_df.shape}"
    )

    st.title("Data Cleaning Part")

    st.write("No of missing values in each column:")
    st.write(merged_df.isnull().sum())

    st.write("Data types of each column:")
    st.write(merged_df.dtypes)

    st.write(
        f"Total columns: {len(merged_df.columns)}"
    )

    available_cols = merged_df.columns.tolist()

    with st.form("cleaning_form"):

        selected_columns = st.multiselect(
            "Select columns to clean (or select all):",
            options=available_cols,
            default=available_cols
        )

        selected_columns = [
            col for col in selected_columns
            if col in st.session_state.cleaned_df.columns
        ]

        if selected_columns:

            apply_to_all = st.checkbox(
                "Apply same cleaning method to all selected columns"
            )

            if apply_to_all:

                cleaning_method = st.selectbox(
                    "Select cleaning method for all selected columns:",
                    [
                        "Mean",
                        "Median",
                        "Mode",
                        "Drop Rows",
                        "Drop Columns",
                        "Skip"
                    ]
                )

                apply_all = st.form_submit_button("Apply cleaning")

                if apply_all:

                    drop_cols = []

                    for col in selected_columns:

                        if cleaning_method == "Skip":
                            pass

                        elif cleaning_method == "Mean":

                            if pd.api.types.is_numeric_dtype(
                                st.session_state.cleaned_df[col]
                            ):

                                st.session_state.cleaned_df[col] = (
                                    st.session_state.cleaned_df[col]
                                    .fillna(
                                        st.session_state.cleaned_df[col]
                                        .mean()
                                    )
                                )

                            else:

                                st.warning(
                                    f"{col} is not numeric. Skipping."
                                )

                        elif cleaning_method == "Median":

                            if pd.api.types.is_numeric_dtype(
                                st.session_state.cleaned_df[col]
                            ):

                                st.session_state.cleaned_df[col] = (
                                    st.session_state.cleaned_df[col]
                                    .fillna(
                                        st.session_state.cleaned_df[col]
                                        .median()
                                    )
                                )

                            else:

                                st.warning(
                                    f"{col} is not numeric. Skipping."
                                )

                        elif cleaning_method == "Mode":

                            mode_values = (
                                st.session_state.cleaned_df[col]
                                .mode()
                            )

                            if len(mode_values) > 0:

                                st.session_state.cleaned_df[col] = (
                                    st.session_state.cleaned_df[col]
                                    .fillna(mode_values[0])
                                )

                        elif cleaning_method == "Drop Rows":

                            drop_cols.append(col)

                        elif cleaning_method == "Drop Columns":

                            st.session_state.cleaned_df = (
                                st.session_state.cleaned_df.drop(
                                    columns=[col]
                                )
                            )

                    if drop_cols:

                        st.session_state.cleaned_df = (
                            st.session_state.cleaned_df.dropna(
                                subset=drop_cols
                            )
                        )

                    st.success("Cleaning applied!")

            else:

                st.write("Or clean columns individually:")

                cleaning_choices = {}

                for idx, col in enumerate(selected_columns):

                    with st.expander(
                        f"{col} "
                        f"({st.session_state.cleaned_df[col].isnull().sum()} "
                        f"missing values)"
                    ):

                        if pd.api.types.is_numeric_dtype(
                            st.session_state.cleaned_df[col]
                        ):

                            options = [
                                "Mean",
                                "Median",
                                "Mode",
                                "Drop Rows",
                                "Drop Columns",
                                "Skip"
                            ]

                        else:

                            options = [
                                "Mode",
                                "Drop Rows",
                                "Drop Columns",
                                "Skip"
                            ]

                        option = st.selectbox(
                            f"Cleaning method for {col}",
                            options,
                            key=f"{idx}_{col}"
                        )

                        cleaning_choices[col] = option

                apply_individual = st.form_submit_button(
                    "Apply Individual Cleaning"
                )

                if apply_individual:

                    drop_rows_cols = []
                    drop_columns = []

                    for col, option in cleaning_choices.items():

                        series = st.session_state.cleaned_df[col]

                        if option == "Skip":
                            pass

                        elif option == "Mean":

                            st.session_state.cleaned_df[col] = (
                                series.fillna(series.mean())
                            )

                        elif option == "Median":

                            st.session_state.cleaned_df[col] = (
                                series.fillna(series.median())
                            )

                        elif option == "Mode":

                            mode_values = series.mode()

                            if len(mode_values) > 0:

                                st.session_state.cleaned_df[col] = (
                                    series.fillna(mode_values[0])
                                )

                        elif option == "Drop Rows":

                            drop_rows_cols.append(col)

                        elif option == "Drop Columns":

                            drop_columns.append(col)

                    if drop_rows_cols:

                        st.session_state.cleaned_df = (
                            st.session_state.cleaned_df.dropna(
                                subset=drop_rows_cols
                            )
                        )

                    if drop_columns:

                        st.session_state.cleaned_df = (
                            st.session_state.cleaned_df.drop(
                                columns=drop_columns
                            )
                        )

                    st.success("Individual cleaning applied!")

    if st.button("Reset Cleaned Data"):

        st.session_state.cleaned_df = merged_df.copy()

        st.success("Cleaned data reset!")

    st.write("Cleaned DataFrame:")
    st.dataframe(st.session_state.cleaned_df)

    csv = (
        st.session_state.cleaned_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download Cleaned Data",
        data=csv,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )