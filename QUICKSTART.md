# ⚡ Quick Start Guide

Get DataLens running in **5 minutes**.

---

## 1️⃣ Download & Extract

Extract the `data-analyzer.zip` file to your desired location:
```bash
unzip data-analyzer.zip
cd data-analyzer
```

---

## 2️⃣ Install Python Dependencies

### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 3️⃣ Launch the App

```bash
streamlit run app.py
```

Your browser will open to **http://localhost:8501** automatically.

---

## 4️⃣ Upload a Dataset

1. Click **📤 Upload** in the sidebar
2. Drag & drop your file (CSV, Excel, Parquet, JSON)
3. See instant preview and schema info

---

## ✨ What's Next?

- **Clean data** → Go to 🧹 Cleaning
- **Explore stats** → Go to 📊 Statistics  
- **Build charts** → Go to 📈 Dashboard
- **Check correlations** → Go to 🔗 Correlation
- **Export results** → Go to 💾 Export

---

## 🎯 Example Datasets

### Generate test data (100MB CSV):
```python
import polars as pl
import random

data = {
    "id": range(1_000_000),
    "value": [random.gauss(100, 20) for _ in range(1_000_000)],
    "category": [random.choice(["A","B","C"]) for _ in range(1_000_000)],
    "amount": [random.uniform(10, 1000) for _ in range(1_000_000)],
}

pl.DataFrame(data).write_csv("test_data.csv")
```

Then upload `test_data.csv` in the app!

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port 8501 in use** | `streamlit run app.py --server.port 8502` |
| **Memory error** | Close other apps, use Parquet format |
| **ModuleNotFoundError** | Ensure venv is activated & pip install ran |
| **Slow on large files** | This is normal—data is streaming efficiently |

---

## 📚 Full Documentation

See **README.md** for comprehensive guide, advanced features, and API reference.

---

**Happy analyzing! 🚀**


## PDF chart export

The PDF report embeds the Plotly charts as images. The project uses Kaleido 1.x
for chart image export. After installing requirements, if Kaleido reports that
Chrome/Chromium is missing, run:

```bash
python -m kaleido.get_chrome
```

Then restart Streamlit and generate the report again.
