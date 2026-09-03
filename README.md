# 🎵 Spain Top 50 — Content Lifecycle & Playlist Analytics

> **Content Maturity, Release Lifecycle & Playlist Rotation Analysis of Spain Top 50 Songs**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas\&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?logo=numpy\&logoColor=white)](https://numpy.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly\&logoColor=white)](https://plotly.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit\&logoColor=white)](https://streamlit.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github\&logoColor=white)](https://github.com/)

---

## 📌 Project Overview

This project analyzes the **Spain Top 50 music chart** to understand how songs enter, grow, peak, mature, and eventually leave the playlist.

The project combines:

* Data cleaning and preprocessing
* Song lifecycle analysis
* Lifecycle stage classification
* Playlist churn and rotation analysis
* Content attribute analysis
* KPI generation
* Interactive data visualization
* Streamlit dashboard development

The goal is to transform raw chart observations into meaningful insights about **song longevity, popularity, playlist stability, content maturity, and chart movement**.

---

## 🎯 Objectives

1. Analyze the lifecycle of songs appearing in the Spain Top 50.
2. Measure how long songs remain on the playlist.
3. Calculate entry-to-peak performance time.
4. Classify songs into lifecycle stages.
5. Measure playlist churn and rotation.
6. Compare explicit and clean content.
7. Compare single and album releases.
8. Analyze song attributes against chart longevity.
9. Generate business-focused KPIs.
10. Present the results through an interactive dashboard.

---

## 🧠 Key Business Questions

* How long does an average song remain on the Spain Top 50?
* How quickly does a song reach its peak position?
* How frequently does the playlist change?
* How stable is the playlist?
* Which lifecycle stages dominate the chart?
* Does explicit content have a different lifecycle from clean content?
* Do singles remain on the chart longer than album tracks?
* Is song duration related to chart longevity?
* How does popularity vary across lifecycle stages?

---

# 🔬 Lifecycle Framework

Songs are classified into five lifecycle stages:

| Stage            | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| 🆕 **New Entry** | Song within the first 7 days since chart entry                |
| 📈 **Growth**    | Song showing significant improvement in chart position        |
| 🏆 **Peak**      | Song performing near its strongest chart position             |
| ➡️ **Mature**    | Song showing relatively stable chart performance              |
| 📉 **Decline**   | Song experiencing significant deterioration in chart position |

---

# 🔄 Data Analysis Pipeline

```text
                    ┌─────────────────────┐
                    │ Atlantic_Spain.csv  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 01_clean_data.py    │
                    │ Data Cleaning       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 02_lifecycle_table  │
                    │ Lifecycle Analysis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ 03_stage_classifi.  │
                    │ Stage Classification│
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       ┌─────────────────────┐     ┌─────────────────────┐
       │ 04_churn_rotation   │     │ 05_content_attributes│
       │ Playlist Analytics  │     │ Content Analysis    │
       └──────────┬──────────┘     └──────────┬──────────┘
                  │                           │
                  └─────────────┬─────────────┘
                                ▼
                     ┌─────────────────────┐
                     │ 06_kpi_summary.py   │
                     │ KPI Generation      │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │     app.py          │
                     │ Streamlit Dashboard │
                     └─────────────────────┘
```

---

# 🛠️ Technology Stack

| Technology    | Purpose                        |
| ------------- | ------------------------------ |
| **Python**    | Core programming and analysis  |
| **Pandas**    | Data manipulation and analysis |
| **NumPy**     | Numerical operations           |
| **Plotly**    | Interactive visualizations     |
| **Streamlit** | Interactive dashboard          |
| **Git**       | Version control                |
| **GitHub**    | Repository and project hosting |

---

# 📁 Project Structure

```text
spain-top50-lifecycle-analysis/
│
├── Atlantic_Spain.csv
│
├── 01_clean_data.py
├── 02_lifecycle_table.py
├── 03_stage_classification.py
├── 04_churn_rotation.py
├── 05_content_attributes.py
├── 06_kpi_summary.py
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── cleaned_data.csv
├── lifecycle_table.csv
├── daily_with_stages.csv
├── daily_churn.csv
├── monthly_churn.csv
├── lifecycle_with_buckets.csv
└── final_kpis.csv
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/abdulmajeedhub/spain-top50-lifecycle-analysis.git
```

```bash
cd spain-top50-lifecycle-analysis
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

```text
pandas
numpy
streamlit
plotly
```

---

# ▶️ Run the Complete Analysis

The scripts must be executed **in order**, because each stage produces files required by the following stage.

## Step 1 — Clean the Dataset

```bash
python 01_clean_data.py
```

Generates:

```text
cleaned_data.csv
```

---

## Step 2 — Build Lifecycle Table

```bash
python 02_lifecycle_table.py
```

Generates:

```text
lifecycle_table.csv
```

---

## Step 3 — Classify Lifecycle Stages

```bash
python 03_stage_classification.py
```

Generates:

```text
daily_with_stages.csv
```

---

## Step 4 — Analyze Playlist Churn

```bash
python 04_churn_rotation.py
```

Generates:

```text
daily_churn.csv
monthly_churn.csv
```

---

## Step 5 — Analyze Content Attributes

```bash
python 05_content_attributes.py
```

Generates:

```text
lifecycle_with_buckets.csv
```

---

## Step 6 — Generate Final KPIs

```bash
python 06_kpi_summary.py
```

Generates:

```text
final_kpis.csv
```

---

# 🚀 Run the Streamlit Dashboard

After completing all six analysis scripts:

```bash
streamlit run app.py
```

The dashboard will normally be available at:

```text
http://localhost:8501
```

Press `Ctrl + C` in the terminal to stop the dashboard.

---

# 📊 Dashboard Features

## 🎵 Lifecycle Timeline

Displays the lifecycle timeline of the longest-charting songs from entry to exit.

## 🔄 Entry / Exit Flow

Shows monthly playlist entries and exits.

## 📊 Lifecycle Stage Distribution

Visualizes the distribution of:

* New Entry
* Growth
* Peak
* Mature
* Decline

and compares average popularity across stages.

## 🎧 Content Maturity

Compares:

* Explicit vs. Clean songs
* Single vs. Album releases

## 📉 Churn Analytics

Displays playlist churn trends over time.

---

# 📌 Key Performance Indicators

The project calculates six major KPIs:

| KPI                                  | Description                                                 |
| ------------------------------------ | ----------------------------------------------------------- |
| **Average Days on Playlist**         | Average number of days songs remain on the chart            |
| **Entry-to-Peak Time**               | Average number of days required to reach peak position      |
| **Playlist Churn Rate**              | Daily percentage of playlist slots changing                 |
| **Retention Stability Index**        | Share of observations classified as Mature or Peak          |
| **Explicit Content Lifecycle Score** | Explicit lifecycle duration relative to clean content       |
| **Single vs. Album Longevity Ratio** | Average single lifecycle divided by average album lifecycle |

---

# 🔍 Analysis Components

### Data Cleaning

* Date standardization
* Duplicate chart observation removal
* Song and artist normalization
* Track identification

### Lifecycle Analysis

* Entry date
* Exit date
* Total chart duration
* Peak position
* Peak date
* Days-to-peak

### Playlist Analytics

* Daily entries
* Daily exits
* Churn rate
* Retention stability
* Monthly rotation

### Content Analytics

* Explicit vs. clean
* Single vs. album
* Song duration
* Album size
* Popularity

---

# 📈 Generated Output Files

| File                         | Purpose                                |
| ---------------------------- | -------------------------------------- |
| `cleaned_data.csv`           | Cleaned dataset                        |
| `lifecycle_table.csv`        | Track-level lifecycle information      |
| `daily_with_stages.csv`      | Daily lifecycle stage classifications  |
| `daily_churn.csv`            | Daily playlist churn                   |
| `monthly_churn.csv`          | Monthly churn analysis                 |
| `lifecycle_with_buckets.csv` | Lifecycle data with album-size buckets |
| `final_kpis.csv`             | Final KPI summary                      |

---

# 🔧 Git & GitHub

## Initialize Git

If you are creating the repository locally for the first time:

```bash
git init
```

## Check Repository Status

```bash
git status
```

## Add All Project Files

```bash
git add .
```

## Create the First Commit

```bash
git commit -m "Initial commit: Spain Top 50 lifecycle analysis project"
```

## Connect Local Repository to GitHub

```bash
git remote add origin https://github.com/abdulmajeedhub/spain-top50-lifecycle-analysis.git
```

## Set Main Branch

```bash
git branch -M main
```

## Push Project to GitHub

```bash
git push -u origin main
```

---

# 🔄 Updating the GitHub Repository

After modifying your code, dashboard, README, or analysis:

```bash
git status
```

```bash
git add .
```

```bash
git commit -m "Update analysis and dashboard"
```

```bash
git push
```

---

# 🔗 Verify Git Remote

To check which GitHub repository your local project is connected to:

```bash
git remote -v
```

Expected:

```text
origin  https://github.com/abdulmajeedhub/spain-top50-lifecycle-analysis.git (fetch)
origin  https://github.com/abdulmajeedhub/spain-top50-lifecycle-analysis.git (push)
```

---

# 🧹 Git Ignore

The project should not upload the virtual environment or Python cache files.

Recommended `.gitignore`:

```text
venv/
__pycache__/
*.pyc
.streamlit/
```

---

# ☁️ Streamlit Cloud Deployment

The dashboard can be deployed using Streamlit Community Cloud.

### Deployment Configuration

```text
Repository:
abdulmajeedhub/spain-top50-lifecycle-analysis

Branch:
main

Main file:
app.py
```

The deployment process automatically installs the dependencies specified in:

```text
requirements.txt
```

Make sure all CSV files required by `app.py` are committed to the repository.

---

# 🎓 Project Context

**Project:** Content Maturity, Release Lifecycle & Playlist Rotation Analysis of Spain Top 50 Songs

**Internship:** Unified Mentor Machine Learning Internship

**Industry:** Music & Entertainment Analytics

**Focus Areas:**

* Data Analytics
* Python
* Lifecycle Analysis
* Playlist Analytics
* Content Intelligence
* Data Visualization
* Streamlit Dashboard

---

# 🚀 Future Enhancements

Potential improvements include:

* Machine learning-based lifecycle prediction
* Song survival analysis
* Chart position forecasting
* Artist-level analytics
* Genre-level analysis
* Real-time chart data ingestion
* Automated reporting
* Song lifecycle prediction
* Advanced recommendation models
* Interactive song-level drill-down

---

# 👨‍💻 Author

## Abdul Majeed A

**Computer Science Engineering | AI & Machine Learning**

GitHub:
https://github.com/abdulmajeedhub

---

# ⭐ Project Highlights

```text
✓ End-to-end Python analytics pipeline
✓ Data cleaning and preprocessing
✓ Song lifecycle modeling
✓ Lifecycle stage classification
✓ Playlist churn analysis
✓ Content attribute analysis
✓ KPI generation
✓ Interactive Streamlit dashboard
✓ Plotly visualizations
✓ Git & GitHub version control
✓ Deployment-ready project
```

---

## ⭐ Support

If you find this project useful, consider giving the repository a **star ⭐**.
