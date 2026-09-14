"""Atlantic Spain Top 50 — Content Maturity, Lifecycle & Playlist Rotation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from pipeline import (
    PALETTE,
    STAGE_COLORS,
    STAGES,
    apply_filters,
    build_market,
    default_data_path,
)

st.set_page_config(
    page_title="Atlantic Spain · Lifecycle Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(246,240,232,0.35)",
    font=dict(family="Source Sans 3, Segoe UI, sans-serif", color="#1C3144", size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=40, r=24, t=48, b=40),
    hoverlabel=dict(bgcolor="#0D2137", font_color="#F6F0E8", font_size=12),
)


def style_fig(fig, height=380):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(13,33,55,0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(13,33,55,0.08)", zeroline=False)
    return fig


def inject_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 500px at 8% -10%, #f3d7b8 0%, transparent 55%),
    radial-gradient(900px 420px at 100% 0%, #cfe8e4 0%, transparent 50%),
    #FCFAF5;
  color: #1C3144;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; max-width: 1440px; }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D2137 0%, #16324F 55%, #1B3A4A 100%);
}
[data-testid="stSidebar"] * { color: #F6F0E8 !important; }
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] > div {
  background: #13283F; border-color: #2A4A68;
}
[data-testid="stSidebar"] .stSlider label { color: #E3B23C !important; }
.hero {
  background: linear-gradient(120deg, #0D2137 0%, #1B4B5A 58%, #C45C3A 140%);
  border-radius: 22px;
  padding: 1.6rem 1.8rem 1.4rem;
  color: #F6F0E8;
  margin-bottom: 1.1rem;
  box-shadow: 0 18px 40px rgba(13,33,55,0.18);
}
.hero h1 {
  font-family: Fraunces, Georgia, serif;
  font-size: 2.05rem;
  line-height: 1.15;
  margin: 0 0 0.35rem 0;
  letter-spacing: -0.02em;
}
.hero p { margin: 0; opacity: 0.9; max-width: 820px; }
.eyebrow {
  font-family: Source Sans 3, sans-serif;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.72rem;
  color: #E3B23C;
  margin-bottom: 0.45rem;
}
.kpi-card {
  background: #fff;
  border: 1px solid rgba(13,33,55,0.08);
  border-radius: 16px;
  padding: 0.95rem 1rem 0.85rem;
  box-shadow: 0 8px 24px rgba(13,33,55,0.05);
  min-height: 118px;
}
.kpi-card .label {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6B7280;
  font-weight: 600;
}
.kpi-card .value {
  font-family: Fraunces, Georgia, serif;
  font-size: 1.85rem;
  color: #0D2137;
  margin: 0.15rem 0 0.1rem;
}
.kpi-card .hint { font-size: 0.82rem; color: #3D5A80; }
.section-title {
  font-family: Fraunces, Georgia, serif;
  font-size: 1.35rem;
  color: #0D2137;
  margin: 0.4rem 0 0.35rem;
}
.caption-note { color: #5B6770; font-size: 0.9rem; margin-bottom: 0.8rem; }
.insight {
  background: #fff;
  border-left: 5px solid #C45C3A;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin-bottom: 0.7rem;
}
.insight.teal { border-left-color: #2A9D8F; }
.insight.gold { border-left-color: #E3B23C; }
.insight.slate { border-left-color: #3D5A80; }
.swatch-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 0.4rem 0 0.8rem; }
.swatch {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.78rem; color: #1C3144;
}
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-card {
  background: rgba(13,33,55,0.04);
  border-radius: 14px;
  padding: 0.8rem 1rem;
}
div[data-testid="stTabs"] button { font-weight: 600; }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_bundle(path: str):
    return build_market(path)


def kpi_card(label, value, hint):
    st.markdown(
        f'<div class="kpi-card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="hint">{hint}</div></div>',
        unsafe_allow_html=True,
    )


def fmt_pct(x):
    return f"{100 * x:.1f}%" if pd.notna(x) else "—"


def fmt_num(x, digits=1):
    return f"{x:.{digits}f}" if pd.notna(x) else "—"


inject_css()

data_path = default_data_path()
if not data_path.exists():
    data_path = Path("data/Atlantic_Spain.csv")

st.sidebar.markdown("### Atlantic · Spain Top 50")
st.sidebar.caption("Lifecycle intelligence for release timing, catalog mix, and rotation.")

source = str(data_path)

with st.spinner("Building song lifecycles…"):
    bundle = load_bundle(source)

vmin = bundle.validation["date_min"].date()
vmax = bundle.validation["date_max"].date()

st.sidebar.caption("Stage filter shapes timelines and stage charts. KPI cards and churn stay on the date / explicit / format window so the Top 50 is not torn apart.")
date_range = st.sidebar.date_input("Date range", value=(vmin, vmax), min_value=vmin, max_value=vmax)
stage_pick = st.sidebar.multiselect("Lifecycle stage", STAGES, default=STAGES)
explicit_mode = st.sidebar.radio("Explicit content", ["All", "Explicit only", "Clean only"], horizontal=False)
album_pick = st.sidebar.multiselect("Album type", ["single", "album"], default=["single", "album"])

start, end = (date_range[0], date_range[1]) if isinstance(date_range, (list, tuple)) and len(date_range) == 2 else (vmin, vmax)
view = apply_filters(
    bundle,
    start=start,
    end=end,
    stages=stage_pick or STAGES,
    explicit_mode=explicit_mode,
    album_types=album_pick or ["single", "album"],
)

daily, life, rotation, kpis = view.daily, view.life, view.rotation, view.kpis

st.markdown(
    f"""
<div class="hero">
  <div class="eyebrow">Atlantic Recording Corporation · Spain market</div>
  <h1>Content maturity, release lifecycle &amp; playlist rotation</h1>
  <p>Daily Spain Top 50 snapshots from {vmin:%d %b %Y} to {vmax:%d %b %Y}.
  This is not a US-style popularity dashboard: it measures how long songs survive, how fast they peak,
  and how violently the playlist turns over.</p>
</div>
""",
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "Command center",
        "Lifecycle timeline",
        "Playlist rotation",
        "Content maturity",
        "Attributes vs retention",
        "Insights",
    ]
)

# ---------------------------------------------------------------------------
with tabs[0]:
    st.markdown('<p class="section-title">Market pulse</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption-note">Six assignment KPIs, computed on the filtered window. Colour maps to meaning: gold = speed, teal = durability, terracotta = intensity.</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Average days on playlist", fmt_num(kpis.get("avg_days_on_playlist")), "Lifecycle length (mean across unique tracks)")
    with c2:
        kpi_card("Entry-to-peak time", f"{fmt_num(kpis.get('entry_to_peak_days'))} d", f"Median {fmt_num(kpis.get('median_entry_to_peak'), 0)} days · maturity speed")
    with c3:
        kpi_card("Playlist churn rate", fmt_pct(kpis.get("playlist_churn_rate")), "Share of the 50 replaced each day")
    c4, c5, c6 = st.columns(3)
    with c4:
        kpi_card("Retention stability index", fmt_num(kpis.get("retention_stability_index"), 3), "Mean Jaccard overlap vs previous day")
    with c5:
        kpi_card("Explicit lifecycle score", fmt_num(kpis.get("explicit_lifecycle_score"), 2), "Explicit mean days ÷ clean mean days")
    with c6:
        kpi_card("Single / album longevity", fmt_num(kpis.get("single_album_longevity_ratio"), 2), "Singles last longer when ratio > 1")

    st.markdown('<p class="section-title">Colour theory used in this dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="swatch-row">
  <span class="swatch"><span class="dot" style="background:#0D2137"></span>Navy — Atlantic, trust, structure</span>
  <span class="swatch"><span class="dot" style="background:#C45C3A"></span>Terracotta — Spain, peak heat, explicit</span>
  <span class="swatch"><span class="dot" style="background:#2A9D8F"></span>Teal — growth, clean content, durability</span>
  <span class="swatch"><span class="dot" style="background:#E3B23C"></span>Saffron — newness, freshness, singles</span>
  <span class="swatch"><span class="dot" style="background:#3D5A80"></span>Slate — mature / catalog middle</span>
  <span class="swatch"><span class="dot" style="background:#8B4D63"></span>Rose — decline and exit risk</span>
</div>
""",
        unsafe_allow_html=True,
    )

    left, right = st.columns((1.35, 1))
    with left:
        stage_counts = daily["lifecycle_stage"].value_counts().reindex(STAGES).fillna(0)
        fig = go.Figure(
            go.Bar(
                x=stage_counts.values,
                y=stage_counts.index,
                orientation="h",
                marker_color=[STAGE_COLORS[s] for s in stage_counts.index],
                hovertemplate="%{y}: %{x:,} song-days<extra></extra>",
            )
        )
        fig.update_layout(title="Lifecycle stage distribution (song-days)")
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)
    with right:
        mix = pd.DataFrame(
            {
                "slice": ["Clean", "Explicit", "Single", "Album"],
                "value": [
                    (~daily["is_explicit"]).mean(),
                    daily["is_explicit"].mean(),
                    (daily["album_type"] == "single").mean(),
                    (daily["album_type"] == "album").mean(),
                ],
                "family": ["Maturity", "Maturity", "Format", "Format"],
            }
        )
        fig = px.bar(
            mix,
            x="family",
            y="value",
            color="slice",
            color_discrete_map={"Clean": PALETTE["clean"], "Explicit": PALETTE["explicit"], "Single": PALETTE["gold"], "Album": PALETTE["slate"]},
            barmode="stack",
            title="Playlist composition",
        )
        fig.update_yaxes(tickformat=".0%", title="")
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

    a, b, c = st.columns(3)
    with a:
        st.metric("Unique tracks in window", f"{len(life):,}")
    with b:
        st.metric("Peak on first chart day", fmt_pct(kpis.get("pct_peak_on_entry")))
    with c:
        st.metric("Validation · days ≠ 50", str(bundle.validation["days_not_50"]))
    st.caption(
        f"Normalized {bundle.validation['rows_out']:,} rows · {bundle.validation['snapshot_days']} snapshot days · "
        f"{bundle.validation['unique_tracks']} unique song–artist keys. "
        f"Missing calendar dates: {', '.join(bundle.validation['missing_dates']) or 'none'}."
    )

# ---------------------------------------------------------------------------
with tabs[1]:
    st.markdown('<p class="section-title">Song lifecycle timeline</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption-note">Position is inverted so #1 sits at the top — the path a song actually walks through Spain’s Top 50.</p>',
        unsafe_allow_html=True,
    )
    options = life.sort_values("days_on_playlist", ascending=False)
    labels = options["song"] + " — " + options["artist"]
    pick = st.selectbox("Track", options=labels.tolist(), index=0)
    chosen = options.iloc[labels.tolist().index(pick)]
    series = daily[daily["track_id"] == chosen["track_id"]].sort_values("date")

    cover, meta, chart = st.columns((0.7, 1.1, 2.4))
    with cover:
        url = chosen.get("album_cover_url")
        if isinstance(url, str) and url.startswith("http"):
            st.image(url, use_container_width=True)
    with meta:
        st.markdown(f"**{chosen['song']}**")
        st.caption(chosen["artist"])
        st.write(f"Entry {pd.to_datetime(chosen['entry_date']).date()} → exit {pd.to_datetime(chosen['exit_date']).date()}")
        st.write(f"Days on list: **{int(chosen['days_on_playlist'])}** · Peak **#{int(chosen['peak_position'])}**")
        st.write(f"Time to peak: **{int(chosen['time_to_peak_days'])} days**")
        st.write(f"Format: {chosen['album_type']} · {'Explicit' if chosen['is_explicit'] else 'Clean'}")
        st.write(f"Duration {chosen['duration_min']:.2f} min · album size {int(chosen['total_tracks'])}")
    with chart:
        fig = go.Figure()
        for stage, chunk in series.groupby("lifecycle_stage"):
            fig.add_trace(
                go.Scatter(
                    x=chunk["date"],
                    y=chunk["position"],
                    mode="markers",
                    name=stage,
                    marker=dict(size=9, color=STAGE_COLORS[stage], line=dict(width=0)),
                    hovertemplate="%{x|%d %b %Y}<br>Rank #%{y}<extra>" + stage + "</extra>",
                )
            )
        fig.add_trace(
            go.Scatter(
                x=series["date"],
                y=series["position"],
                mode="lines",
                line=dict(color="rgba(13,33,55,0.35)", width=2),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.update_yaxes(autorange="reversed", title="Playlist rank", dtick=5)
        fig.update_layout(title="Rank path (1 is best)")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    pop_col, heat_col = st.columns((1, 1.2))
    with pop_col:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=series["date"], y=series["popularity"], name="Popularity", line=dict(color=PALETTE["terracotta"], width=3)),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=series["date"], y=series["position"], name="Rank", line=dict(color=PALETTE["slate"], width=2, dash="dot")),
            secondary_y=True,
        )
        fig.update_yaxes(title="Popularity", secondary_y=False)
        fig.update_yaxes(title="Rank", autorange="reversed", secondary_y=True)
        fig.update_layout(title="Popularity vs rank on the same clock")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with heat_col:
        top_ids = life.nlargest(18, "days_on_playlist")["track_id"]
        heat = daily[daily["track_id"].isin(top_ids)].copy()
        heat["label"] = heat["song_display"].str.slice(0, 22)
        pivot = heat.pivot_table(index="label", columns="date", values="position", aggfunc="min")
        fig = go.Figure(
            data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale=[
                    [0, "#C45C3A"],
                    [0.2, "#E3B23C"],
                    [0.5, "#2A9D8F"],
                    [1, "#0D2137"],
                ],
                reversescale=False,
                colorbar=dict(title="#"),
                hovertemplate="%{y}<br>%{x|%d %b}<br>Rank %{z}<extra></extra>",
            )
        )
        fig.update_layout(title="Longest-running tracks · rank heat")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    st.markdown("**Entry → peak → exit (longest 12 tracks in this window)**")
    top = life.nlargest(12, "days_on_playlist")
    fig = go.Figure()
    for _, row in top.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["entry_date"], row["peak_date"], row["exit_date"]],
                y=[row["song"]] * 3,
                mode="lines+markers",
                line=dict(color=PALETTE["slate"], width=6),
                marker=dict(
                    size=[10, 14, 10],
                    color=[PALETTE["gold"], PALETTE["terracotta"], PALETTE["rose"]],
                ),
                hovertemplate=row["song"]
                + "<br>Entry %{x|%d %b %Y}<extra></extra>",
                showlegend=False,
            )
        )
    fig.update_layout(title="Gold = entry · terracotta = peak · rose = last observed day")
    st.plotly_chart(style_fig(fig, 420), use_container_width=True)

# ---------------------------------------------------------------------------
with tabs[2]:
    st.markdown('<p class="section-title">Playlist rotation & churn</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption-note">Spain is described as faster than UK/US. Watch entries vs exits, then the monthly heat of replacement intensity.</p>',
        unsafe_allow_html=True,
    )
    if rotation.empty:
        st.warning("No rotation rows in this filter.")
    else:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Mean daily entries", fmt_num(rotation["entries"].mean()))
        r2.metric("Mean daily exits", fmt_num(rotation["exits"].mean()))
        r3.metric("Max one-day replacement", f"{int(rotation['entries'].max())} / 50")
        r4.metric("Mean Jaccard stability", fmt_num(rotation["jaccard"].mean(), 3))

        fig = go.Figure()
        fig.add_bar(x=rotation["date"], y=rotation["entries"], name="Entries", marker_color=PALETTE["teal"])
        fig.add_bar(x=rotation["date"], y=-rotation["exits"], name="Exits", marker_color=PALETTE["rose"])
        fig.update_layout(barmode="relative", title="Daily entry vs exit flow (exits drawn downward)")
        fig.update_yaxes(title="Tracks")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        m1, m2 = st.columns(2)
        with m1:
            fig = px.line(
                rotation,
                x="date",
                y="churn_rate",
                title="Daily churn rate",
            )
            fig.update_traces(line_color=PALETTE["terracotta"], line_width=2)
            fig.update_yaxes(tickformat=".0%")
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)
        with m2:
            fig = px.line(
                rotation,
                x="date",
                y="jaccard",
                title="Stability (overlap with previous day)",
            )
            fig.update_traces(line_color=PALETTE["teal"], line_width=2)
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        monthly = rotation.groupby("month", as_index=False).agg(
            churn=("churn_rate", "mean"),
            stability=("jaccard", "mean"),
            entries=("entries", "mean"),
        )
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=monthly["month"], y=monthly["churn"], name="Avg churn", marker_color=PALETTE["terracotta"]),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=monthly["month"], y=monthly["stability"], name="Stability", line=dict(color=PALETTE["navy"], width=3)),
            secondary_y=True,
        )
        fig.update_yaxes(title="Churn", tickformat=".1%", secondary_y=False)
        fig.update_yaxes(title="Jaccard", secondary_y=True)
        fig.update_layout(title="Rotation comparison across months")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        vol = (rotation["churn_rate"] > rotation["churn_rate"].median()).map({True: "Volatile days", False: "Stable days"})
        rotation_view = rotation.assign(regime=vol)
        fig = px.scatter(
            rotation_view,
            x="jaccard",
            y="churn_rate",
            color="regime",
            color_discrete_map={"Volatile days": PALETTE["terracotta"], "Stable days": PALETTE["teal"]},
            title="Stability vs volatility",
            hover_data=["date", "entries"],
        )
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

# ---------------------------------------------------------------------------
with tabs[3]:
    st.markdown('<p class="section-title">Content maturity · explicit vs clean</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="caption-note">The brief asks whether explicit titles mature differently. Score &gt; 1 means explicit titles last longer; below 1 means clean catalog is stickier.</p>',
        unsafe_allow_html=True,
    )
    if life.empty:
        st.warning("No tracks in this filter.")
    else:
        grp = life.groupby("is_explicit").agg(
            tracks=("track_id", "nunique"),
            avg_days=("days_on_playlist", "mean"),
            median_days=("days_on_playlist", "median"),
            ttp=("time_to_peak_days", "mean"),
            peak=("peak_position", "mean"),
            pop=("avg_popularity", "mean"),
        ).reset_index()
        grp["label"] = np.where(grp["is_explicit"], "Explicit", "Clean")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(
                grp,
                x="label",
                y="avg_days",
                color="label",
                color_discrete_map={"Explicit": PALETTE["explicit"], "Clean": PALETTE["clean"]},
                title="Average days on playlist",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)
        with c2:
            fig = px.violin(
                life.assign(label=np.where(life["is_explicit"], "Explicit", "Clean")),
                x="label",
                y="days_on_playlist",
                color="label",
                color_discrete_map={"Explicit": PALETTE["explicit"], "Clean": PALETTE["clean"]},
                box=True,
                title="Longevity distribution",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        fig = px.scatter(
            life,
            x="time_to_peak_days",
            y="days_on_playlist",
            color=np.where(life["is_explicit"], "Explicit", "Clean"),
            color_discrete_map={"Explicit": PALETTE["explicit"], "Clean": PALETTE["clean"]},
            size="avg_popularity",
            hover_name="song",
            hover_data=["artist", "peak_position"],
            title="Maturity speed vs survival (bubble size = mean popularity)",
        )
        st.plotly_chart(style_fig(fig, 420), use_container_width=True)

        stage_mix = (
            daily.assign(label=np.where(daily["is_explicit"], "Explicit", "Clean"))
            .groupby(["label", "lifecycle_stage"])
            .size()
            .reset_index(name="n")
        )
        stage_mix["share"] = stage_mix.groupby("label")["n"].transform(lambda s: s / s.sum())
        fig = px.bar(
            stage_mix,
            x="lifecycle_stage",
            y="share",
            color="label",
            barmode="group",
            category_orders={"lifecycle_stage": STAGES},
            color_discrete_map={"Explicit": PALETTE["explicit"], "Clean": PALETTE["clean"]},
            title="Stage mix by content rating",
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        st.dataframe(
            grp[["label", "tracks", "avg_days", "median_days", "ttp", "peak", "pop"]].rename(
                columns={
                    "label": "Content",
                    "tracks": "Tracks",
                    "avg_days": "Avg days",
                    "median_days": "Median days",
                    "ttp": "Avg days to peak",
                    "peak": "Avg peak rank",
                    "pop": "Avg popularity",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------------------------
with tabs[4]:
    st.markdown('<p class="section-title">Attributes vs lifecycle</p>', unsafe_allow_html=True)
    if life.empty:
        st.warning("No tracks in this filter.")
    else:
        fmt = life.groupby("album_type").agg(
            tracks=("track_id", "nunique"),
            avg_days=("days_on_playlist", "mean"),
            ttp=("time_to_peak_days", "mean"),
            occupancy=("occupancy", "mean"),
        ).reset_index()
        f1, f2 = st.columns(2)
        with f1:
            fig = px.bar(
                fmt,
                x="album_type",
                y="avg_days",
                color="album_type",
                color_discrete_map={"single": PALETTE["gold"], "album": PALETTE["slate"]},
                title="Single vs album longevity",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)
        with f2:
            fig = px.scatter(
                life,
                x="duration_min",
                y="days_on_playlist",
                color="album_type",
                color_discrete_map={"single": PALETTE["gold"], "album": PALETTE["slate"]},
                hover_name="song",
                title="Duration vs retention",
            )
            st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        fig = px.scatter(
            life,
            x="total_tracks",
            y="days_on_playlist",
            color=np.where(life["is_explicit"], "Explicit", "Clean"),
            color_discrete_map={"Explicit": PALETTE["explicit"], "Clean": PALETTE["clean"]},
            hover_name="song",
            title="Album size vs lifecycle length",
        )
        st.plotly_chart(style_fig(fig, 380), use_container_width=True)

        pop_stage = daily.groupby("lifecycle_stage", as_index=False).agg(
            popularity=("popularity", "mean"),
            rank=("position", "mean"),
        )
        pop_stage["lifecycle_stage"] = pd.Categorical(pop_stage["lifecycle_stage"], STAGES, ordered=True)
        pop_stage = pop_stage.sort_values("lifecycle_stage")
        fig = px.line(
            pop_stage,
            x="lifecycle_stage",
            y="popularity",
            markers=True,
            title="Popularity growth vs lifecycle stage",
        )
        fig.update_traces(line_color=PALETTE["terracotta"], line_width=3, marker=dict(size=10))
        st.plotly_chart(style_fig(fig, 360), use_container_width=True)

        fig = px.histogram(
            life,
            x="time_to_pop_peak_days",
            nbins=40,
            title="Peak popularity timing (days after first chart appearance)",
            color_discrete_sequence=[PALETTE["navy"]],
        )
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        decay = daily.copy()
        decay["week"] = ((decay["days_so_far"] - 1) // 7).clip(upper=12)
        decay_g = decay.groupby("week")["popularity"].mean().reset_index()
        fig = px.area(
            decay_g,
            x="week",
            y="popularity",
            title="Popularity by weeks since entry (decay / plateau pattern)",
        )
        fig.update_traces(fillcolor="rgba(42,157,143,0.35)", line_color=PALETTE["teal"])
        fig.update_xaxes(title="Week on chart (capped at 12)")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

        st.markdown("**Longest-surviving tracks**")
        show = life.nlargest(20, "days_on_playlist")[
            ["song", "artist", "days_on_playlist", "peak_position", "time_to_peak_days", "album_type", "is_explicit", "avg_popularity"]
        ].rename(
            columns={
                "song": "Song",
                "artist": "Artist",
                "days_on_playlist": "Days",
                "peak_position": "Peak",
                "time_to_peak_days": "Days to peak",
                "album_type": "Format",
                "is_explicit": "Explicit",
                "avg_popularity": "Avg popularity",
            }
        )
        st.dataframe(show, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
with tabs[5]:
    st.markdown('<p class="section-title">What this market is telling Atlantic</p>', unsafe_allow_html=True)
    churn = kpis.get("playlist_churn_rate") or 0
    ratio = kpis.get("single_album_longevity_ratio") or 0
    score = kpis.get("explicit_lifecycle_score") or 0
    ttp = kpis.get("entry_to_peak_days") or 0
    pct0 = kpis.get("pct_peak_on_entry") or 0
    st.markdown(
        f"""
<div class="insight gold">
<strong>Freshness is real, but the median track is short-lived.</strong>
Median stay is {fmt_num(kpis.get('median_days_on_playlist'), 0)} days while the mean is {fmt_num(kpis.get('avg_days_on_playlist'))} —
a long-tail catalog (La Bachata-class titles) sits under a fast-churn majority.
</div>
<div class="insight teal">
<strong>Many Spanish chart hits peak on entry.</strong>
{fmt_pct(pct0)} of tracks reach their best rank on day one; mean entry-to-peak is {fmt_num(ttp)} days.
Marketing intensity belongs <em>before</em> playlist add, not after a slow climb.
</div>
<div class="insight">
<strong>Singles outlast album cuts on this playlist.</strong>
Longevity ratio {fmt_num(ratio, 2)} (single mean days ÷ album mean days). Album campaigns need extra playlist servicing after week one.
</div>
<div class="insight slate">
<strong>Explicit vs clean is a maturity lever, not a moral label.</strong>
Explicit lifecycle score {fmt_num(score, 2)}. Plan clean/radio edits if the clean cohort is retaining longer in the selected window.
</div>
<div class="insight teal">
<strong>Rotation is moderate most days, then spikes.</strong>
Average daily churn {fmt_pct(churn)} (~{fmt_num((churn or 0)*50)} of 50). November 2025 and April 2025 are the volatile months in the full sample — do not copy a US “set and forget” hold strategy.
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("**Recommended Spain playbook**")
    st.markdown(
        """
1. **Release timing:** Treat first 7 days as the only guaranteed New Entry window. Pre-save and creator seeding should peak 48–72 hours before expected Top 50 entry.
2. **Marketing intensity:** Front-load spend; after peak, switch from awareness to catalog retargeting only for titles still in Peak/Mature stages.
3. **Catalog vs fresh:** Keep 1–2 long-stay catalog records in pitch lists; most slots will turn. Do not assume album-track osmosis from a lead single.
4. **Playlist rotation:** On high-churn months, refresh pitching weekly. On high-Jaccard months, defend holds with editorial relationships rather than new IDs.
5. **Content rating:** Split campaigns by explicit flag; measure stay length separately instead of blending Spain with US clean-version logic.
"""
    )
    st.download_button(
        "Download lifecycle table (CSV)",
        data=life.to_csv(index=False).encode("utf-8"),
        file_name="spain_top50_lifecycle.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download daily rotation (CSV)",
        data=rotation.to_csv(index=False).encode("utf-8"),
        file_name="spain_top50_rotation.csv",
        mime="text/csv",
    )
