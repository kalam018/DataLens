# 🔬 DataLens — Interactive Data Analysis & Visualization Platform

DataLens is a Python-based interactive data analysis platform built with Streamlit. It helps users upload datasets, clean data, explore statistical insights, visualize relationships, perform correlation analysis, run SQL queries, and export analysis results through an intuitive web interface.

---

## ✨ Features

### 📤 Data Upload & Ingestion

- Supports CSV, Excel, Parquet, and JSON files.
- Data preview and schema inspection.
- Automatic data type detection.
- Efficient data handling for larger datasets.

### 🧹 Data Cleaning

- Handle missing values using different strategies.
- Remove duplicate records.
- Trim whitespace from text fields.
- Detect and remove outliers using the IQR method.
- Change column data types.
- Rename columns.
- Reset cleaned data to the original uploaded dataset.

### 📊 Statistical Analysis & Profiling

- Descriptive statistics.
- Column-level analysis.
- Skewness and kurtosis.
- Normality testing using Shapiro-Wilk and Kolmogorov-Smirnov tests.
- Value frequency analysis.
- Distribution visualizations and Q-Q plots.

### 📈 Interactive Dashboard

- Histogram, scatter, bar, line, and box plots.
- Interactive chart customization.
- Trendline support for scatter plots.
- Sampling for visualization of larger datasets.
- DuckDB-powered SQL query sandbox.

### 🔗 Correlation & Association Analysis

- Pearson correlation.
- Spearman correlation.
- Cramér's V for categorical associations.
- Chi-square statistical tests.
- Correlation heatmaps.
- Ranking of strongly associated variable pairs.

### 💾 Data Export

- Export data to CSV, Excel, Parquet, and JSON.
- Styled Excel output.
- Download cleaned datasets.
- Download original CSV data.
- Generate downloadable PDF analysis reports.

### 📄 PDF Analysis Report

The application can generate a PDF report containing:

- Dataset overview.
- Data quality information.
- Descriptive statistics.
- Embedded charts.
- Interpretations and key findings.

---

## 🛠️ Tech Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Core programming language     |
| Streamlit  | Interactive web application   |
| Polars     | DataFrame processing          |
| DuckDB     | SQL queries and data analysis |
| NumPy      | Numerical computing           |
| SciPy      | Statistical analysis          |
| Plotly     | Interactive visualizations    |
| OpenPyXL   | Excel export and formatting   |

---

## 📁 Project Structure

```text
data_lens/
│
├── app.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── DEPLOYMENT.md
├── QUICKSTART.md
│
├── pages/
│   ├── upload.py
│   ├── cleaning.py
│   ├── statistics.py
│   ├── dashboard.py
│   ├── correlation.py
│   └── export.py
│
├── services/
│   ├── loader.py
│   ├── cleaner.py
│   ├── stats.py
│   ├── charts.py
│   ├── correlation.py
│   └── exporter.py
│
└── .streamlit/
```
