# spain-top50-lifecycle-analysis
# Content Maturity, Release Lifecycle & Playlist Rotation
# Analysis of Spain Top 50 Songs
Machine Learning Internship project (Unified Mentor) for
Atlantic Recording Corporation.
## Setup
pip install -r requirements.txt
## Run the pipeline (in order)
python 01_clean_data.py
python 02_lifecycle_table.py
python 03_stage_classification.py
python 04_churn_rotation.py
python 05_content_attributes.py
python 06_kpi_summary.py
## Run the dashboard
streamlit run app.py
