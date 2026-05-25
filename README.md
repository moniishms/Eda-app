# Excel File Upload, Cleaner & EDA Visualizer

A web app built with Streamlit that lets you upload, merge, clean, and explore your Excel or CSV files — all without writing a single line of code.

---

## Live Demo

[EDA-APP](https://EDA-APP.streamlit.app)

---

## Features

### File Upload & Merging
- Upload up to 5 Excel (.xlsx) or CSV (.csv) files at once
- Merge files row-wise (stack rows) or column-wise (add columns side by side)
- Automatic duplicate column detection and removal
- Smart string-to-numeric type conversion on load

### Data Cleaning
- Select specific columns to clean
- Fill missing values using Mean, Median, or Mode
- Drop rows with missing values or drop entire columns
- Apply one method to all selected columns or handle each column individually
- Undo any cleaning step with one click
- Reset everything back to the original merged data

### EDA Visualization
- Dataset info — row count, column count, duplicate rows
- Summary statistics for all columns
- Correlation Heatmap for numeric columns
- Distribution Plot with skewness analysis
- Box Plot with automatic outlier detection using IQR method

### Export
- Download your cleaned data as a CSV file at any time

---

## Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web app framework |
| [Pandas](https://pandas.pydata.org) | Data manipulation |
| [Matplotlib](https://matplotlib.org) | Plot rendering |
| [Seaborn](https://seaborn.pydata.org) | Statistical visualizations |
| [OpenPyXL](https://openpyxl.readthedocs.io) | Excel file reading |

---

## Run Locally

**1. Clone the repository**

**2. Install dependencies**

**3. Run the app**

The app will open at `http://localhost:8501`

---

## Requirements

```
streamlit
pandas
matplotlib
seaborn
openpyxl
```

---

## Project Structure

```
EDA-APP/
├── app.py           
├── requirements.txt  
└── README.md         
```

---

## Screenshots
> (screenshots/upload.png)`

---

## Author
M.S.Moniish
---


