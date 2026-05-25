import streamlit as st
import pandas as pd
import numpy as np
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

    st.warning(
        "Use Row-wise merge for demo datasets. Column-wise merge is only recommended for datasets with matching row structures."
    )

    merge_type = st.selectbox(
        "Select merge type",
        ["Row-wise", "Column-wise"],
        index=0
    )

    if merge_type == "Row-wise":

        if len(data_frames) > 1:
            common_cols = set.intersection(
                *[set(df.columns) for df in data_frames]
            )
            union_cols = set.union(
                *[set(df.columns) for df in data_frames]
            )
            similarity = len(common_cols) / len(union_cols) if union_cols else 1.0

            if similarity < 0.8:
                st.warning(
                    "Row-wise merge may create NaN values because uploaded files have different columns."
                )

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
            [df.reset_index(drop=True) for df in data_frames],
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

    # Replace empty strings and string representations of null with pd.NA
    temp_merged_df = temp_merged_df.replace(
        ["None", "none", "NaN", "nan", ""],
        pd.NA
    )

    st.session_state.merged_df = temp_merged_df.copy()

    merged_df = st.session_state.merged_df


    file_fingerprint = [
        (
            f.name,
            hashlib.md5(f.getvalue()).hexdigest(),
            merge_type
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

        st.session_state.history = [st.session_state.cleaned_df.copy()]
        st.session_state.selected_columns = []

    st.write("Merged DataFrame:")
    st.dataframe(merged_df)

    st.write(
        f"Shape of merged DataFrame: {merged_df.shape}"
    )

    # Detailed missing values analysis at merge level
    st.write("**Missing Values in Merged Data (by column):**")
    merge_missing_df = pd.DataFrame({
        "Column": merged_df.columns,
        "Missing Values": merged_df.isnull().sum().values,
        "Missing %": (merged_df.isnull().sum().values / len(merged_df) * 100).round(2),
        "Non-Null Count": merged_df.notnull().sum().values
    })
    st.dataframe(merge_missing_df, use_container_width=True)

    st.title("Data Cleaning Part")

   

    st.write("Data types of each column:")
    dtypes_df = pd.DataFrame({
        "Column": st.session_state.cleaned_df.columns,
        "Data Type": st.session_state.cleaned_df.dtypes.values
    })
    st.dataframe(dtypes_df, use_container_width=True)

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
                        f"{col}"
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

            if not st.session_state.cleaned_df.equals(merged_df):
                st.session_state.history.append(
                    st.session_state.cleaned_df.copy()
                )

            st.session_state.cleaned_df = merged_df.copy()

            st.session_state.selected_columns = (
                current_selected_columns
            )

            st.success("Cleaned data reset! You can undo this reset if needed.")

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
        # Distribution + Boxplot + Bar Chart
        # =========================

        cat_cols = [
            col for col in
            st.session_state.cleaned_df
            .select_dtypes(include=["object", "category"]).columns
            if any(keyword in col.lower() for keyword in [
                "region",
                "category",
                "segment",
                "ship mode",
                "ship_mode",
                "shipmode"
            ])
        ]
        other_cat_cols = [
            col for col in
            st.session_state.cleaned_df
            .select_dtypes(include=["object", "category"]).columns
            if col not in cat_cols
        ]
        category_cols = list(dict.fromkeys(cat_cols + other_cat_cols))

        if numeric_cols:
            dist_col = st.selectbox(
                "Distribution column",
                numeric_cols,
                index=0,
                key="distribution_col"
            )
            box_col = st.selectbox(
                "Box plot column",
                numeric_cols,
                index=0,
                key="boxplot_col"
            )
        else:
            dist_col = None
            box_col = None

        if category_cols and numeric_cols:
            category_col = st.selectbox(
                "Category column",
                category_cols,
                index=0,
                key="bar_category_col"
            )
            metric_col = st.selectbox(
                "Numeric metric column",
                numeric_cols,
                index=0,
                key="bar_metric_col"
            )
            top_n = st.slider(
                "Top N categories to display",
                min_value=5,
                max_value=20,
                value=10,
                step=1,
                key="top_n_categories"
            )
        else:
            category_col = None
            metric_col = None
            top_n = 10

        if numeric_cols:
            st.markdown("---")
            st.subheader("Distribution Plot")
            dist_series = st.session_state.cleaned_df[dist_col].dropna()
            dist_skew = dist_series.skew() if not dist_series.empty else 0
            use_log_x = (
                dist_series.min() > 0 and abs(dist_skew) > 1.5
                and dist_series.max() / max(dist_series.quantile(0.75), 1) > 50
            )

            fig, ax = plt.subplots(figsize=(10, 5))
            if dist_series.nunique() <= 10:
                sns.countplot(
                    data=st.session_state.cleaned_df,
                    x=dist_col,
                    ax=ax,
                    palette="viridis"
                )
            else:
                sns.histplot(
                    dist_series,
                    kde=True,
                    ax=ax,
                    bins=30,
                    color="#2c7fb8",
                    edgecolor="black",
                    alpha=0.85
                )
                if use_log_x:
                    ax.set_xscale("log")
            ax.set_title(
                f"Distribution of {dist_col}",
                fontsize=16,
                fontweight="bold"
            )
            ax.set_xlabel(dist_col, fontsize=11)
            ax.set_ylabel("Frequency", fontsize=11)
            ax.grid(axis="y", alpha=0.2, linestyle="--")
            ax.tick_params(axis="both", labelsize=10)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            skew_type = "Approximately Normal"
            if abs(dist_skew) >= 0.5:
                skew_type = "Right Skewed" if dist_skew > 0 else "Left Skewed"

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Skewness", f"{round(dist_skew, 3)}")
            with col2:
                st.metric("Distribution type", skew_type)
            with col3:
                st.metric("Unique values", dist_series.nunique())

            st.markdown("---")
            st.subheader("Box Plot for Outlier Detection")
            box_series = st.session_state.cleaned_df[box_col].dropna()
            if box_series.empty:
                st.warning(f"{box_col} has no valid data to plot.")
            else:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.boxplot(
                    y=box_series,
                    ax=ax,
                    color="#9ecae1",
                    linewidth=2
                )
                box_skew = box_series.skew()
                if box_series.min() > 0 and abs(box_skew) > 1.5:
                    ax.set_yscale("log")
                ax.set_title(
                    f"Box Plot of {box_col}",
                    fontsize=16,
                    fontweight="bold"
                )
                ax.set_ylabel(box_col, fontsize=11)
                ax.grid(axis="y", alpha=0.2, linestyle="--")
                ax.tick_params(axis="both", labelsize=10)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)

                Q1 = box_series.quantile(0.25)
                Q3 = box_series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = box_series[(box_series < lower_bound) | (box_series > upper_bound)]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Q1", f"{round(Q1, 2)}")
                with col2:
                    st.metric("Q3", f"{round(Q3, 2)}")
                with col3:
                    st.metric("IQR", f"{round(IQR, 2)}")
                with col4:
                    st.metric(
                        "Outliers",
                        len(outliers),
                    )
        else:
            st.info("No numeric columns available for distribution and boxplot charts.")

        if category_col is not None and metric_col is not None:
            st.markdown("---")
            st.subheader("Bar Chart - Metric by Category")
            grouped = (
                st.session_state.cleaned_df
                .dropna(subset=[category_col, metric_col])
                .groupby(category_col)[metric_col]
                .sum()
                .sort_values(ascending=False)
            )
            grouped = grouped.head(top_n)

            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.bar(
                range(len(grouped)),
                grouped.values,
                color="#2ca25f",
                edgecolor="black",
                linewidth=1.2,
                alpha=0.85
            )
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(
                [str(x) for x in grouped.index],
                rotation=45,
                ha="right",
                fontsize=10
            )
            ax.set_title(
                f"{metric_col} by {category_col}",
                fontsize=16,
                fontweight="bold"
            )
            ax.set_xlabel(category_col, fontsize=11)
            ax.set_ylabel(f"Total {metric_col}", fontsize=11)
            ax.grid(axis="y", alpha=0.2, linestyle="--")
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f"{round(height, 2)}",
                    ha="center",
                    va="bottom",
                    fontsize=9
                )
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        elif category_cols and numeric_cols:
            st.warning("No categories were available after data cleaning to build a bar chart.")
        else:
            st.warning(
                "Need both a numeric metric and a categorical grouping column for the bar chart."
            )