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

_Note: The structure above represents the application's intended organization. Actual files may vary depending on the current project version._

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- VS Code (recommended).

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/DataLens.git
cd DataLens
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

The application will normally open in your browser at:

http://localhost:8501

---

## 📖 How to Use DataLens

### 1. Upload a Dataset

Upload a CSV, Excel, Parquet, or JSON file and preview its contents.

### 2. Clean Data

Explore missing values, remove duplicates, handle outliers, modify column types, and clean your dataset.

### 3. Explore Statistics

Analyze descriptive statistics, column distributions, frequencies, and statistical properties.

### 4. Build Visualizations

Create and customize interactive charts using the Dashboard page.

### 5. Analyze Relationships

Explore numerical correlations and categorical associations.

### 6. Run SQL Queries

Use the SQL sandbox to query data with DuckDB.

### 7. Export Results

Download cleaned data and generate PDF analysis reports.

---

## ⚡ Performance Considerations

DataLens incorporates techniques intended to improve analysis efficiency:

- Sampling for chart visualization.
- DuckDB-based query processing.
- Polars-based DataFrame operations.
- Efficient processing strategies for larger datasets.
- Optimized statistical computations where applicable.

Actual performance depends on dataset size, data format, available RAM, CPU, and the operations performed.

---

## 💡 Example SQL Query

```sql
SELECT col_a, AVG(col_b) AS avg_b
FROM tbl
WHERE col_c > 100
GROUP BY col_a
ORDER BY avg_b DESC
LIMIT 20;
```

---

## 🔒 Data & Privacy

DataLens is designed to process uploaded datasets within the application session.

- Upload data for analysis through the application interface.
- Export processed datasets when required.
- Avoid uploading sensitive datasets to publicly hosted deployments.
- Data persistence and privacy depend on the environment in which the application is deployed.

---

## 🔧 Troubleshooting

### Streamlit command is not recognized

Use:

```bash
python -m streamlit run app.py
```

### Dependency installation problems

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Then install the dependencies again:

```bash
python -m pip install -r requirements.txt
```

### Application port is already in use

Run the application on a different port:

```bash
python -m streamlit run app.py --server.port 8502
```

---

## 🎯 Project Objective

DataLens aims to simplify exploratory data analysis by bringing data cleaning, statistical exploration, visualization, correlation analysis, SQL querying, and report generation together in a single interactive platform.

---

## 👨‍💻 Author

**Abdul Kalam K**

M.Sc. Applied Data Science Student

---

## 📌 Project Status

Developed as a Python-based interactive data analysis and visualization project.

---
