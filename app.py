import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Spain Top 50 · Lifecycle Analytics",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# DESIGN TOKENS
# ---------------------------------------------------------------------
# A record-label listening room, not a SaaS template: near-black studio
# background, warm amber for the thing that matters most (like a VU
# meter needle in the red), cool blue/teal for the rest of the signal
# chain. Numbers read in a monospaced, digital-counter face; headings
# in a squared-off grotesk with a bit of character.
# =====================================================================
BG = "#0A0C10"
PANEL = "#12151C"
PANEL_ALT = "#171B24"
BORDER = "#262B37"
TEXT = "#ECEEF2"
MUTED = "#8B93A3"
AMBER = "#F0A83B"
TEAL = "#3FC6C6"

STAGE_COLORS = {
    "New Entry": "#4C8EF0",
    "Growth": "#3FC6C6",
    "Peak": "#F0A83B",
    "Mature": "#9C8CF0",
    "Decline": "#E8615C",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.stApp {{
    background-color: {BG};
}}

/* ---- Headings ---- */
h1, h2, h3 {{
    font-family: 'Space Grotesk', sans-serif;
    color: {TEXT};
    letter-spacing: -0.01em;
}}

/* ---- Hero ---- */
.hero-wrap {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 22px;
    margin-bottom: 6px;
}}
.hero-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    color: {AMBER};
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 40px;
    font-weight: 700;
    color: {TEXT};
    line-height: 1.1;
    margin: 0;
}}
.hero-sub {{
    color: {MUTED};
    font-size: 14.5px;
    margin-top: 8px;
    max-width: 640px;
}}
.hero-meta {{
    text-align: right;
    color: {MUTED};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    line-height: 1.7;
}}
.hero-meta b {{ color: {TEXT}; font-weight: 500; }}

/* ---- KPI ticker strip ---- */
.ticker {{
    display: flex;
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin: 22px 0 30px 0;
    overflow: hidden;
}}
.ticker-cell {{
    flex: 1;
    padding: 16px 18px;
    border-right: 1px solid {BORDER};
}}
.ticker-cell:last-child {{ border-right: none; }}
.ticker-label {{
    color: {MUTED};
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}}
.ticker-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 25px;
    font-weight: 600;
    color: {TEXT};
}}
.ticker-value.accent {{ color: {AMBER}; }}
.ticker-note {{
    color: {MUTED};
    font-size: 11px;
    margin-top: 5px;
}}

/* ---- Section framing ---- */
.panel-note {{
    color: {MUTED};
    font-size: 13px;
    margin-top: 2px;
    margin-bottom: 18px;
}}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 14.5px;
    color: {MUTED};
    padding: 10px 4px;
}}
.stTabs [aria-selected="true"] {{
    color: {AMBER} !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: {AMBER} !important;
}}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}
section[data-testid="stSidebar"] h3 {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: {AMBER};
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 18px;
    margin-bottom: 4px;
}}

/* ---- Dataframe ---- */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER};
    border-radius: 6px;
}}

/* ---- Divider tone-down ---- */
hr {{ border-color: {BORDER}; }}
</style>
""", unsafe_allow_html=True)

PLOTLY_FONT = dict(family="Inter, sans-serif", color=TEXT, size=12)


def style_fig(fig, height=420, legend=False):
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=PLOTLY_FONT,
        margin=dict(l=10, r=10, t=36, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=MUTED, size=11)),
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, color=MUTED)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, color=MUTED)
    return fig


# ---------- Data loading ----------
@st.cache_data
def load_data():
    daily = pd.read_csv('daily_with_stages.csv', parse_dates=['date', 'entry_date'])
    lifecycle = pd.read_csv('lifecycle_with_buckets.csv', parse_dates=['entry_date', 'exit_date', 'peak_date'])
    churn = pd.read_csv('daily_churn.csv', parse_dates=['date'])
    kpis = pd.read_csv('final_kpis.csv', index_col=0)
    return daily, lifecycle, churn, kpis


daily, lifecycle, churn, kpis = load_data()

# ---------- Sidebar filters ----------
st.sidebar.markdown("### Time window")
min_date, max_date = daily['date'].min(), daily['date'].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date.date(), max_date.date()),
    min_value=min_date.date(), max_value=max_date.date(),
    label_visibility="collapsed",
)

st.sidebar.markdown("### Lifecycle stage")
stage_filter = st.sidebar.multiselect(
    "Lifecycle stage", options=list(STAGE_COLORS.keys()), default=list(STAGE_COLORS.keys()),
    label_visibility="collapsed",
)

st.sidebar.markdown("### Content rating")
explicit_filter = st.sidebar.radio(
    "Explicit content", ["All", "Explicit only", "Clean only"], index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("### Release format")
album_filter = st.sidebar.multiselect(
    "Album type", options=lifecycle['album_type'].unique().tolist(),
    default=lifecycle['album_type'].unique().tolist(),
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Atlantic Recording Corporation · Internal analytics")

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

# ---------- Hero ----------
current_no1 = daily.loc[daily['date'] == daily['date'].max()].sort_values('position').iloc[0]
no1_name = current_no1['song_display'] if 'song_display' in daily.columns else current_no1.get('song', '')

st.markdown(f"""
<div class="hero-wrap">
  <div>
    <div class="hero-eyebrow">SPAIN · DAILY TOP 50</div>
    <p class="hero-title">Content Lifecycle Analytics</p>
    <p class="hero-sub">How songs enter, climb, hold and fall off the chart — and what that says
    about release strategy, explicit content and single vs. album performance.</p>
  </div>
  <div class="hero-meta">
    CURRENTLY AT NO. 1<br>
    <b>{no1_name}</b><br>
    {daily['date'].min().strftime('%d %b %Y')} → {daily['date'].max().strftime('%d %b %Y')}
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- KPI ticker ----------
def ticker_cell(label, value, note="", accent=False):
    cls = "ticker-value accent" if accent else "ticker-value"
    return f"""<div class="ticker-cell">
        <div class="ticker-label">{label}</div>
        <div class="{cls}">{value}</div>
        <div class="ticker-note">{note}</div>
    </div>"""

st.markdown(f"""
<div class="ticker">
    {ticker_cell("Avg. days on playlist", f"{kpis.loc['Average Days on Playlist','value']:.1f}", "per track, full run", accent=True)}
    {ticker_cell("Entry → peak time", f"{kpis.loc['Entry-to-Peak Time (days, avg)','value']:.1f}d", "median climb speed")}
    {ticker_cell("Daily churn rate", f"{kpis.loc['Playlist Churn Rate (%/day)','value']:.1f}%", "of the 50 slots turn over")}
    {ticker_cell("Retention stability", f"{kpis.loc['Retention Stability Index (%)','value']:.1f}%", "obs. in Mature / Peak")}
    {ticker_cell("Explicit lifecycle score", f"{kpis.loc['Explicit Content Lifecycle Score','value']:.2f}", "vs. clean, 1.00 = parity")}
    {ticker_cell("Single vs. album", f"{kpis.loc['Single vs Album Longevity Ratio','value']:.2f}×", "longevity ratio")}
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Lifecycle Timeline", "Entry & Exit Flow", "Stage Mix",
    "Content Profile", "Churn Over Time",
])

# ---------- Tab 1: Timeline visualizer ----------
with tab1:
    st.subheader("Longest-running tracks, entry to exit")
    st.markdown('<p class="panel-note">Top 15 tracks in the current filter, by total days charted.</p>', unsafe_allow_html=True)

    top_songs = lc_f.nlargest(15, 'total_days').sort_values('total_days')
    fig = go.Figure()
    for _, row in top_songs.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['entry_date'], row['exit_date']], y=[row['song'], row['song']],
            mode='lines+markers', line=dict(width=5, color=AMBER),
            marker=dict(size=7, color=AMBER), showlegend=False,
            hovertemplate=f"{row['song']} — {row['artist']}<br>{row['total_days']} days<extra></extra>",
        ))
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(style_fig(fig, height=560), use_container_width=True)

# ---------- Tab 2: Entry/Exit flow ----------
with tab2:
    st.subheader("New entries vs. exits, by month")
    st.markdown('<p class="panel-note">How much of the chart turns over each month.</p>', unsafe_allow_html=True)

    churn_monthly = churn.copy()
    churn_monthly['month'] = churn_monthly['date'].dt.to_period('M').astype(str)
    monthly_flow = churn_monthly.groupby('month')[['entries', 'exits']].sum().reset_index()

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=monthly_flow['month'], y=monthly_flow['entries'], name='Entries', marker_color=TEAL))
    fig2.add_trace(go.Bar(x=monthly_flow['month'], y=monthly_flow['exits'], name='Exits', marker_color="#E8615C"))
    fig2.update_layout(barmode='group', xaxis_title="", yaxis_title="Count")
    st.plotly_chart(style_fig(fig2, height=440, legend=True), use_container_width=True)

# ---------- Tab 3: Stage distribution ----------
with tab3:
    st.subheader("Where tracks sit in their lifecycle")
    st.markdown('<p class="panel-note">Left: share of daily observations per stage. Right: average popularity score per stage.</p>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        stage_counts = daily_f['lifecycle_stage'].value_counts()
        fig3 = px.pie(
            values=stage_counts.values, names=stage_counts.index,
            color=stage_counts.index, color_discrete_map=STAGE_COLORS, hole=0.55,
        )
        fig3.update_traces(textfont=dict(color=TEXT))
        st.plotly_chart(style_fig(fig3, height=380, legend=True), use_container_width=True)
    with col_b:
        pop_by_stage = daily_f.groupby('lifecycle_stage')['popularity'].mean().reindex(STAGE_COLORS.keys())
        fig4 = px.bar(
            x=pop_by_stage.index, y=pop_by_stage.values,
            color=pop_by_stage.index, color_discrete_map=STAGE_COLORS,
            labels={'x': '', 'y': 'Avg. popularity'},
        )
        st.plotly_chart(style_fig(fig4, height=380), use_container_width=True)

# ---------- Tab 4: Content maturity ----------
with tab4:
    st.subheader("Explicit vs. clean, single vs. album")
    st.markdown('<p class="panel-note">Average chart life by content rating and release format.</p>', unsafe_allow_html=True)

    col_c, col_d = st.columns(2)
    with col_c:
        exp_cmp = lc_f.groupby('is_explicit')['total_days'].mean().rename(index={True: 'Explicit', False: 'Clean'})
        fig5 = px.bar(
            x=exp_cmp.index, y=exp_cmp.values,
            color=exp_cmp.index, color_discrete_map={'Explicit': AMBER, 'Clean': TEAL},
            labels={'x': '', 'y': 'Avg. days on chart'},
        )
        st.plotly_chart(style_fig(fig5, height=360), use_container_width=True)
    with col_d:
        alb_cmp = lc_f.groupby('album_type')['total_days'].mean()
        fig6 = px.bar(
            x=alb_cmp.index, y=alb_cmp.values,
            color=alb_cmp.index, color_discrete_map={'single': AMBER, 'album': TEAL},
            labels={'x': '', 'y': 'Avg. days on chart'},
        )
        st.plotly_chart(style_fig(fig6, height=360), use_container_width=True)

    st.markdown("##### Longest-charting tracks in this view")
    st.dataframe(
        lc_f[['song', 'artist', 'total_days', 'peak_position', 'days_to_peak', 'album_type', 'is_explicit']]
        .sort_values('total_days', ascending=False).head(20)
        .rename(columns={
            'song': 'Song', 'artist': 'Artist', 'total_days': 'Days charted',
            'peak_position': 'Peak position', 'days_to_peak': 'Days to peak',
            'album_type': 'Format', 'is_explicit': 'Explicit',
        }),
        use_container_width=True, hide_index=True,
    )

# ---------- Tab 5: Churn analytics ----------
with tab5:
    st.subheader("Monthly churn rate over time")
    st.markdown('<p class="panel-note">Average daily churn rate (share of the Top 50 that changed), aggregated by month.</p>', unsafe_allow_html=True)

    churn_monthly2 = churn.copy()
    churn_monthly2['month'] = churn_monthly2['date'].dt.to_period('M').astype(str)
    monthly_churn_rate = churn_monthly2.groupby('month')['churn_rate'].mean().reset_index()

    fig7 = px.line(monthly_churn_rate, x='month', y='churn_rate', markers=True,
                    labels={'month': '', 'churn_rate': 'Avg. churn rate'})
    fig7.update_traces(line_color=AMBER, marker=dict(size=7, color=AMBER))
    fig7.update_layout(yaxis_tickformat='.1%')
    st.plotly_chart(style_fig(fig7, height=420), use_container_width=True)

st.markdown(
    f'<p style="text-align:center; color:{MUTED}; font-size:12px; margin-top:28px;">'
    'Built for the Unified Mentor Machine Learning Internship · Content Maturity, '
    'Release Lifecycle & Playlist Rotation</p>',
    unsafe_allow_html=True,
)