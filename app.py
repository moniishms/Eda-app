import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib

st.set_page_config(layout="wide")

if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = pd.DataFrame()

if "history" not in st.session_state:
    st.session_state.history = []

if "selected_columns" not in st.session_state:
    st.session_state.selected_columns = []

if "merged_df" not in st.session_state:
    st.session_state.merged_df = pd.DataFrame()

if "csv_data" not in st.session_state:
    st.session_state.csv_data = b""

st.title("Excel File Upload and Viewer")

num = st.number_input(
    "Enter the number of files to upload",
    min_value=1,
    max_value=5,
    step=1
)

uploaded_files = []
data_frames = []

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

if uploaded_files and data_frames:

    merge_type = st.selectbox(
        "Select merge type",
        ["Row-wise", "Column-wise"]
    )

    if merge_type == "Row-wise":

        temp_merged_df = pd.concat(
            data_frames,
            ignore_index=True
        )

    else:

        row_counts = [len(df) for df in data_frames]

        if len(data_frames) > 1 and len(set(row_counts)) != 1:

            st.error(
                "All files must have same number of rows for column-wise merge."
            )

            st.stop()

        temp_merged_df = pd.concat(
            data_frames,
            axis=1
        )

        duplicate_cols = temp_merged_df.columns[
            temp_merged_df.columns.duplicated()
        ].tolist()

        if duplicate_cols:

            st.warning(
                f"Duplicate columns removed: {duplicate_cols}"
            )

        temp_merged_df = temp_merged_df.loc[
            :,
            ~temp_merged_df.columns.duplicated()
        ]

    temp_merged_df = temp_merged_df.replace(
        ["None", "none", "NaN", "nan", ""],
        pd.NA
    )

    st.session_state.merged_df = temp_merged_df.copy()

    merged_df = st.session_state.merged_df

    file_fingerprint = [
        (
            f.name,
            hashlib.md5(f.getvalue()).hexdigest()
        )
        for f in uploaded_files
    ]

    if st.session_state.get("file_fingerprint") != file_fingerprint:

        st.session_state.file_fingerprint = file_fingerprint

        st.session_state.cleaned_df = merged_df.copy()

        for col in st.session_state.cleaned_df.columns:

            try:

                st.session_state.cleaned_df[col] = pd.to_numeric(
                    st.session_state.cleaned_df[col]
                )

            except:

                pass

        st.session_state.history = []
        st.session_state.selected_columns = []

    st.write("Merged DataFrame:")
    st.dataframe(merged_df)

    st.write(
        f"Shape of merged DataFrame: {merged_df.shape}"
    )

    st.title("Data Cleaning Part")

    st.write("No of missing values in each column:")
    st.write(st.session_state.cleaned_df.isnull().sum())

    st.write("Data types of each column:")
    st.write(st.session_state.cleaned_df.dtypes)

    available_cols = merged_df.columns.tolist()

    with st.form("column_selection_form"):

        temp_selected_columns = st.multiselect(
            "Select columns to clean:",
            options=available_cols,
            default=st.session_state.selected_columns
        )

        submit_columns = st.form_submit_button(
            "Confirm Selected Columns"
        )

    if submit_columns:

        st.session_state.selected_columns = (
            temp_selected_columns
        )

    selected_columns = st.session_state.selected_columns

    if selected_columns:

        with st.form("cleaning_form"):

            apply_to_all = st.checkbox(
                "Apply same cleaning method to all selected columns"
            )

            cleaning_choices = {}

            if apply_to_all:

                cleaning_method = st.selectbox(
                    "Select cleaning method:",
                    [
                        "Mean",
                        "Median",
                        "Mode",
                        "Drop Rows",
                        "Drop Columns",
                        "Skip"
                    ]
                )

            else:

                for idx, col in enumerate(selected_columns):

                    current_missing = (
                        st.session_state.cleaned_df[col].isnull().sum()
                        if col in st.session_state.cleaned_df.columns
                        else merged_df[col].isnull().sum()
                    )

                    with st.expander(
                        f"{col} ({current_missing} missing values)"
                    ):

                        series_for_type = (
                            st.session_state.cleaned_df[col]
                            if col in st.session_state.cleaned_df.columns
                            else merged_df[col]
                        )

                        if pd.api.types.is_numeric_dtype(
                            series_for_type
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

                        cleaning_choices[col] = st.selectbox(
                            f"Cleaning method for {col}",
                            options,
                            key=f"{col}_{idx}"
                        )

            submit_cleaning = st.form_submit_button(
                "Apply Cleaning"
            )

        if submit_cleaning:

            st.session_state.history.append(
                st.session_state.cleaned_df.copy()
            )

            drop_rows = []
            drop_columns = []
            skipped_cols = []

            if apply_to_all:

                for col in selected_columns:

                    if col in st.session_state.cleaned_df.columns:

                        series = st.session_state.cleaned_df[col]

                    else:

                        st.session_state.cleaned_df[col] = merged_df[col]

                        series = st.session_state.cleaned_df[col]

                    if cleaning_method == "Skip":

                        pass

                    elif cleaning_method == "Mean":

                        if pd.api.types.is_numeric_dtype(series):

                            st.session_state.cleaned_df[col] = (
                                series.fillna(series.mean())
                            )

                        else:

                            skipped_cols.append(col)

                    elif cleaning_method == "Median":

                        if pd.api.types.is_numeric_dtype(series):

                            st.session_state.cleaned_df[col] = (
                                series.fillna(series.median())
                            )

                        else:

                            skipped_cols.append(col)

                    elif cleaning_method == "Mode":

                        mode_values = series.mode()

                        if len(mode_values) > 0:

                            st.session_state.cleaned_df[col] = (
                                series.fillna(mode_values[0])
                            )

                    elif cleaning_method == "Drop Rows":

                        drop_rows.append(col)

                    elif cleaning_method == "Drop Columns":

                        drop_columns.append(col)

            else:

                for col, option in cleaning_choices.items():

                    if col in st.session_state.cleaned_df.columns:

                        series = st.session_state.cleaned_df[col]

                    else:

                        st.session_state.cleaned_df[col] = merged_df[col]

                        series = st.session_state.cleaned_df[col]

                    if option == "Skip":

                        pass

                    elif option == "Mean":

                        if pd.api.types.is_numeric_dtype(series):

                            st.session_state.cleaned_df[col] = (
                                series.fillna(series.mean())
                            )

                    elif option == "Median":

                        if pd.api.types.is_numeric_dtype(series):

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

                        drop_rows.append(col)

                    elif option == "Drop Columns":

                        drop_columns.append(col)

            if drop_rows:

                st.session_state.cleaned_df = (
                    st.session_state.cleaned_df.dropna(
                        subset=drop_rows
                    )
                )

            if drop_columns:

                st.session_state.cleaned_df = (
                    st.session_state.cleaned_df.drop(
                        columns=drop_columns,
                        errors="ignore"
                    )
                )

            if skipped_cols:

                st.warning(
                    f"Skipped non-numeric columns: {skipped_cols}"
                )

            st.success("Cleaning applied!")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("Undo Last Action"):

            if st.session_state.history:

                st.session_state.cleaned_df = (
                    st.session_state.history.pop()
                )

                st.success("Undo successful!")

            else:

                st.warning("Nothing to undo.")

    with col2:

        if st.button("Reset Cleaned Data"):

            current_selected_columns = (
                st.session_state.selected_columns
            )

            st.session_state.cleaned_df = merged_df.copy()

            st.session_state.history = []

            st.session_state.selected_columns = (
                current_selected_columns
            )

            st.success("Cleaned data reset!")

    st.write("Cleaned DataFrame:")
    st.dataframe(st.session_state.cleaned_df)

    st.session_state.csv_data = (
        st.session_state.cleaned_df
        .to_csv(index=False, na_rep="")
        .encode("utf-8")
    )

    if st.session_state.csv_data:

        st.download_button(
            label="Download Cleaned Data",
            data=st.session_state.csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    # =========================
    # EDA SECTION
    # =========================

    if not st.session_state.cleaned_df.empty:

        st.title("EDA Visualization")

        numeric_cols = [
            col for col in
            st.session_state.cleaned_df
            .select_dtypes(include=["number"])
            .columns
            if "id" not in col.lower()
        ]

        # =========================
        # Dataset Information
        # =========================

        st.subheader("Dataset Information")

        st.write(
            f"Rows: {st.session_state.cleaned_df.shape[0]}"
        )

        st.write(
            f"Columns: {st.session_state.cleaned_df.shape[1]}"
        )

        st.write(
            f"Duplicate Rows: "
            f"{st.session_state.cleaned_df.duplicated().sum()}"
        )

        # =========================
        # Summary Statistics
        # =========================

        st.subheader("Summary Statistics")

        try:

            st.dataframe(
                st.session_state.cleaned_df
                .describe(include="all")
                .T
            )

        except Exception as e:

            st.warning(
                f"Could not generate summary statistics: {e}"
            )


        # =========================
        # Correlation Heatmap
        # =========================

        if len(numeric_cols) > 1:

            st.subheader("Correlation Heatmap")

            corr_matrix = (
                st.session_state.cleaned_df[numeric_cols]
                .corr()
            )

            fig, ax = plt.subplots(figsize=(12, 8))

            sns.heatmap(
                corr_matrix,
                annot=True,
                fmt=".2f",
                cmap="coolwarm",
                linewidths=0.5,
                annot_kws={"size": 8},
                ax=ax
            )

            plt.xticks(rotation=45, ha="right")
            plt.yticks(rotation=0)

            st.pyplot(fig)
            plt.close(fig)

        else:

            st.info(
                "Need at least 2 numeric columns for correlation heatmap."
            )

        # =========================
        # Distribution + Boxplot
        # =========================

        if numeric_cols:

            with st.form("visualization_form"):

                dist_col = st.selectbox(
                    "Select column for distribution plot",
                    numeric_cols,
                    key="distribution_col"
                )

                box_col = st.selectbox(
                    "Select column for box plot",
                    numeric_cols,
                    key="boxplot_col"
                )

                visualize = st.form_submit_button(
                    "Generate Visualizations"
                )

            if visualize:

                # =========================
                # Distribution Plot
                # =========================

                st.subheader("Distribution Plot")

                unique_values = (
                    st.session_state.cleaned_df[dist_col]
                    .nunique()
                )

                fig, ax = plt.subplots(figsize=(8, 5))

                if unique_values <= 10:

                    sns.countplot(
                        x=st.session_state.cleaned_df[dist_col],
                        ax=ax
                    )

                else:

                    sns.histplot(
                        st.session_state.cleaned_df[dist_col].dropna(),
                        kde=True,
                        ax=ax
                    )

                st.pyplot(fig)
                plt.close(fig)

                skewness = (
                    st.session_state.cleaned_df[dist_col]
                    .skew()
                )

                if abs(skewness) < 0.5:

                    skew_type = "Approximately Normal"

                elif skewness > 0:

                    skew_type = "Right Skewed"

                else:

                    skew_type = "Left Skewed"

                st.write(
                    f"Skewness Value: {round(skewness, 2)}"
                )

                st.write(
                    f"Distribution Type: {skew_type}"
                )

                # =========================
                # Box Plot
                # =========================

                st.subheader(
                    "Box Plot for Outlier Detection"
                )

                if (
                    st.session_state.cleaned_df[box_col]
                    .dropna()
                    .empty
                ):

                    st.warning(
                        f"{box_col} has no valid data to plot."
                    )

                else:

                    fig, ax = plt.subplots(figsize=(8, 5))

                    sns.boxplot(
                        x=st.session_state.cleaned_df[box_col],
                        ax=ax
                    )

                    st.pyplot(fig)
                    plt.close(fig)

                    Q1 = (
                        st.session_state.cleaned_df[box_col]
                        .quantile(0.25)
                    )

                    Q3 = (
                        st.session_state.cleaned_df[box_col]
                        .quantile(0.75)
                    )

                    IQR = Q3 - Q1

                    lower_bound = (
                        Q1 - 1.5 * IQR
                    )

                    upper_bound = (
                        Q3 + 1.5 * IQR
                    )

                    outliers = st.session_state.cleaned_df[
                        (
                            st.session_state.cleaned_df[box_col]
                            < lower_bound
                        )
                        |
                        (
                            st.session_state.cleaned_df[box_col]
                            > upper_bound
                        )
                    ]

                    st.write(
                        f"Number of outliers: {len(outliers)}"
                    )

        else:

            st.warning(
                "No numeric columns available for visualization."
            )