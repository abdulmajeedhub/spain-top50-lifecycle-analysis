import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
st.set_page_config(
    page_title="Spain Top 50 | Lifecycle Analytics",
    page_icon="n",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ---------- Custom styling ----------
st.markdown("""
<style>
    .main { background-color: #fafafa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
h1, h2, h3 { color: #1a1a2e; }
.stTabs [data-baseweb="tab"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)
# ---------- Data loading ----------
@st.cache_data
def load_data():
    daily = pd.read_csv('daily_with_stages.csv', parse_dates=['date', 'entry_date'])
    lifecycle = pd.read_csv('lifecycle_with_buckets.csv', parse_dates=['entry_date', 'exit_date', 'peak_date'])
    churn = pd.read_csv('daily_churn.csv', parse_dates=['date'])
    kpis = pd.read_csv('final_kpis.csv', index_col=0)
    return daily, lifecycle, churn, kpis
daily, lifecycle, churn, kpis = load_data()
PALETTE = {
    'New Entry': '#4C72B0', 'Growth': '#55A868', 'Peak': '#C44E52',
    'Mature': '#8172B2', 'Decline': '#CCB974'
}
# ---------- Sidebar filters ----------
st.sidebar.title("nn Filters")
min_date, max_date = daily['date'].min(), daily['date'].max()
date_range = st.sidebar.date_input(
"Date range", value=(min_date.date(), max_date.date()),
min_value=min_date.date(), max_value=max_date.date()
)
stage_filter = st.sidebar.multiselect(
"Lifecycle stage", options=list(PALETTE.keys()), default=list(PALETTE.keys())
)
explicit_filter = st.sidebar.radio("Explicit content", ["All", "Explicit only", "Clean only"], index=0)
album_filter = st.sidebar.multiselect(
"Album type", options=lifecycle['album_type'].unique().tolist(),
default=lifecycle['album_type'].unique().tolist()
)
# apply filters
mask = (
(daily['date'].dt.date >= date_range[0]) & (daily['date'].dt.date <= date_range[-1])
if len(date_range) == 2 else (daily['date'].dt.date == date_range[0])
)
daily_f = daily[mask & daily['lifecycle_stage'].isin(stage_filter)]
lc_f = lifecycle[lifecycle['album_type'].isin(album_filter)]
if explicit_filter == "Explicit only":
    lc_f = lc_f[lc_f['is_explicit']]
    daily_f = daily_f[daily_f['is_explicit']]
elif explicit_filter == "Clean only":
    lc_f = lc_f[~lc_f['is_explicit']]
    daily_f = daily_f[~daily_f['is_explicit']]
# ---------- Header ----------
st.title("n Spain Top 50 — Content Lifecycle Analytics")
st.caption("Content Maturity, Release Lifecycle & Playlist Rotation Analysis · Prepared for Atlantic Recording Corporation")
# ---------- KPI row ----------
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Avg Days on Playlist", f"{kpis.loc['Average Days on Playlist','value']:.1f}")
c2.metric("Entry-to-Peak Time", f"{kpis.loc['Entry-to-Peak Time (days, avg)','value']:.1f} d")
c3.metric("Churn Rate", f"{kpis.loc['Playlist Churn Rate (%/day)','value']:.1f}%")
c4.metric("Retention Stability", f"{kpis.loc['Retention Stability Index (%)','value']:.1f}%")
c5.metric("Explicit Lifecycle Score", f"{kpis.loc['Explicit Content Lifecycle Score','value']:.2f}")
c6.metric("Single vs Album Ratio", f"{kpis.loc['Single vs Album Longevity Ratio','value']:.2f}")
st.divider()
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"n Lifecycle Timeline", "n Entry/Exit Flow", "n Stage Distribution",
"n Content Maturity", "n Churn Analytics"
])
# ---------- Tab 1: Timeline visualizer ----------
with tab1:
    st.subheader("Song Lifecycle Timeline Visualizer")
    top_songs = lc_f.nlargest(15, 'total_days')
    fig = go.Figure()
    for _, row in top_songs.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['entry_date'], row['exit_date']], y=[row['song'], row['song']],
            mode='lines+markers', line=dict(width=6, color='#4C72B0'),
            marker=dict(size=8), showlegend=False,
            hovertemplate=f"{row['song']} — {row['artist']}<br>{row['total_days']} days<extra></extra>"
))
fig.update_layout(height=550, xaxis_title="Date", yaxis_title="",
template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)
st.caption("Top 15 longest-charting tracks in the current filter selection, shown from entry to exit date.")
# ---------- Tab 2: Entry/Exit flow ----------
with tab2:
    st.subheader("Entry vs Exit Flow")
    churn_monthly = churn.copy()
    churn_monthly['month'] = churn_monthly['date'].dt.to_period('M').astype(str)
    monthly_flow = churn_monthly.groupby('month')[['entries', 'exits']].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=monthly_flow['month'], y=monthly_flow['entries'], name='Entries', marker_color='#55A868'))
    fig2.add_trace(go.Bar(x=monthly_flow['month'], y=monthly_flow['exits'], name='Exits', marker_color='#C44E52'))
    fig2.update_layout(barmode='group', height=450, template="plotly_white",
xaxis_title="Month", yaxis_title="Count", margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)
st.caption("Monthly total new entries vs exits from the Top 50.")
# ---------- Tab 3: Stage distribution ----------
with tab3:
    st.subheader("Lifecycle Stage Distribution")
    col_a, col_b = st.columns(2)
with col_a:
    stage_counts = daily_f['lifecycle_stage'].value_counts()
    fig3 = px.pie(values=stage_counts.values, names=stage_counts.index,
color=stage_counts.index, color_discrete_map=PALETTE, hole=0.45)
fig3.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig3, use_container_width=True)
with col_b:
    pop_by_stage = daily_f.groupby('lifecycle_stage')['popularity'].mean().reindex(PALETTE.keys())
    fig4 = px.bar(x=pop_by_stage.index, y=pop_by_stage.values,
color=pop_by_stage.index, color_discrete_map=PALETTE,
labels={'x': 'Stage', 'y': 'Avg Popularity'})
fig4.update_layout(height=400, showlegend=False, template="plotly_white",
margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig4, use_container_width=True)
st.caption("Left: share of daily observations per stage. Right: average popularity score per stage.")
# ---------- Tab 4: Content maturity ----------
with tab4:
    st.subheader("Content Maturity Comparisons")
    col_c, col_d = st.columns(2)
with col_c:
    exp_cmp = lc_f.groupby('is_explicit')['total_days'].mean().rename(index={True: 'Explicit', False: 'Clean'})
    fig5 = px.bar(x=exp_cmp.index, y=exp_cmp.values, color=exp_cmp.index,
labels={'x': '', 'y': 'Avg Days on Chart'}, title="Explicit vs Clean — Avg Chart Life")
fig5.update_layout(height=380, showlegend=False, template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig5, use_container_width=True)
with col_d:
    alb_cmp = lc_f.groupby('album_type')['total_days'].mean()
    fig6 = px.bar(x=alb_cmp.index, y=alb_cmp.values, color=alb_cmp.index,
labels={'x': '', 'y': 'Avg Days on Chart'}, title="Single vs Album — Avg Chart Life")
fig6.update_layout(height=380, showlegend=False, template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig6, use_container_width=True)
st.dataframe(
lc_f[['song', 'artist', 'total_days', 'peak_position', 'days_to_peak', 'album_type', 'is_explicit']]
.sort_values('total_days', ascending=False).head(20),
use_container_width=True, hide_index=True
)
# ---------- Tab 5: Churn analytics ----------
with tab5:
    st.subheader("Playlist Churn Analytics")
    churn_monthly2 = churn.copy()
    churn_monthly2['month'] = churn_monthly2['date'].dt.to_period('M').astype(str)
    monthly_churn_rate = churn_monthly2.groupby('month')['churn_rate'].mean().reset_index()
    fig7 = px.line(monthly_churn_rate, x='month', y='churn_rate', markers=True,
labels={'month': 'Month', 'churn_rate': 'Avg Churn Rate'})
fig7.update_traces(line_color='#4C72B0')
fig7.update_layout(height=420, template="plotly_white", yaxis_tickformat='.1%',
margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig7, use_container_width=True)
st.caption("Average daily churn rate (share of the Top 50 that changed) aggregated by month.")
st.divider()
st.caption("Built for the Unified Mentor Machine Learning Internship · Content Maturity, Release Lifecycle & Playlist Rotation")