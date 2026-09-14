"""Spain Top 50 lifecycle pipeline: validation, lifecycle tables, KPIs, stages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

STAGES = ["New Entry", "Growth Phase", "Peak Phase", "Mature Phase", "Decline Phase"]

STAGE_COLORS = {
    "New Entry": "#E3B23C",
    "Growth Phase": "#2A9D8F",
    "Peak Phase": "#C45C3A",
    "Mature Phase": "#3D5A80",
    "Decline Phase": "#8B4D63",
}

PALETTE = {
    "navy": "#0D2137",
    "ink": "#1C3144",
    "teal": "#2A9D8F",
    "terracotta": "#C45C3A",
    "gold": "#E3B23C",
    "rose": "#8B4D63",
    "slate": "#3D5A80",
    "sand": "#F6F0E8",
    "paper": "#FCFAF5",
    "muted": "#6B7280",
    "explicit": "#C45C3A",
    "clean": "#2A9D8F",
    "single": "#3D5A80",
    "album": "#E3B23C",
}


def default_data_path() -> Path:
    project_dir = Path(__file__).resolve().parent
    root_path = project_dir / "Atlantic_Spain.csv"
    data_dir_path = project_dir / "data" / "Atlantic_Spain.csv"
    return root_path if root_path.exists() else data_dir_path


def load_raw(path: str | Path | None = None) -> pd.DataFrame:
    if path is not None and not isinstance(path, (str, Path)):
        return pd.read_csv(path, encoding="utf-8")
    path = Path(path) if path else default_data_path()
    return pd.read_csv(path, encoding="utf-8")


def normalize_name(value: str) -> str:
    if pd.isna(value):
        return ""
    text = " ".join(str(value).strip().split())
    return text.casefold()


def validate_and_normalize(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    work = df.copy()
    work.columns = [c.strip() for c in work.columns]
    work["date"] = pd.to_datetime(work["date"], dayfirst=True, errors="coerce")
    work["position"] = pd.to_numeric(work["position"], errors="coerce")
    work["popularity"] = pd.to_numeric(work["popularity"], errors="coerce")
    work["duration_ms"] = pd.to_numeric(work["duration_ms"], errors="coerce")
    work["total_tracks"] = pd.to_numeric(work["total_tracks"], errors="coerce")
    work["is_explicit"] = (
        work["is_explicit"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
        .astype(bool)
    )
    work["album_type"] = work["album_type"].astype(str).str.strip().str.lower()
    work["song_display"] = work["song"].astype(str).str.strip()
    work["artist_display"] = work["artist"].astype(str).str.strip()
    work["song_norm"] = work["song_display"].map(normalize_name)
    work["artist_norm"] = work["artist_display"].map(normalize_name)
    work["track_id"] = work["song_norm"] + " || " + work["artist_norm"]

    work = work.dropna(subset=["date", "position", "track_id"])
    work = work[(work["position"] >= 1) & (work["position"] <= 50)]
    work = work.sort_values(["date", "position", "popularity"])
    work = work.drop_duplicates(["date", "position"], keep="last")
    work = work.drop_duplicates(["date", "track_id"], keep="last")

    counts = work.groupby("date").size()
    calendar = pd.date_range(work["date"].min(), work["date"].max(), freq="D")
    report = {
        "rows_in": int(len(df)),
        "rows_out": int(len(work)),
        "snapshot_days": int(work["date"].nunique()),
        "calendar_days": int(len(calendar)),
        "missing_dates": [d.date().isoformat() for d in calendar.difference(work["date"].unique())],
        "days_not_50": int((counts != 50).sum()),
        "unique_tracks": int(work["track_id"].nunique()),
        "unique_artists": int(work["artist_norm"].nunique()),
        "date_min": work["date"].min(),
        "date_max": work["date"].max(),
    }
    return work, report


def build_lifecycle(df: pd.DataFrame) -> pd.DataFrame:
    names = (
        df.groupby("track_id")
        .agg(
            song=("song_display", lambda s: s.value_counts().index[0]),
            artist=("artist_display", lambda s: s.value_counts().index[0]),
            album_cover_url=("album_cover_url", "last"),
        )
        .reset_index()
    )

    ranked = df.sort_values(["track_id", "position", "date"])
    peak_rows = ranked.groupby("track_id", as_index=False).first()[
        ["track_id", "date", "position", "popularity"]
    ]
    peak_rows = peak_rows.rename(
        columns={"date": "peak_date", "position": "peak_position", "popularity": "popularity_at_peak"}
    )

    pop_peak = df.sort_values(["track_id", "popularity", "date"], ascending=[True, False, True])
    pop_rows = pop_peak.groupby("track_id", as_index=False).first()[["track_id", "date", "popularity"]]
    pop_rows = pop_rows.rename(columns={"date": "peak_popularity_date", "popularity": "peak_popularity"})

    life = df.groupby("track_id").agg(
        entry_date=("date", "min"),
        exit_date=("date", "max"),
        days_on_playlist=("date", "nunique"),
        appearances=("date", "count"),
        avg_position=("position", "mean"),
        median_position=("position", "median"),
        avg_popularity=("popularity", "mean"),
        min_popularity=("popularity", "min"),
        max_popularity=("popularity", "max"),
        duration_ms=("duration_ms", "median"),
        total_tracks=("total_tracks", "median"),
        album_type=("album_type", lambda s: s.value_counts().index[0]),
        is_explicit=("is_explicit", lambda s: bool(s.mode().iloc[0]) if len(s.mode()) else bool(s.iloc[0])),
    ).reset_index()

    life = life.merge(peak_rows, on="track_id", how="left")
    life = life.merge(pop_rows, on="track_id", how="left")
    life = life.merge(names, on="track_id", how="left")
    life["time_to_peak_days"] = (life["peak_date"] - life["entry_date"]).dt.days
    life["time_to_pop_peak_days"] = (life["peak_popularity_date"] - life["entry_date"]).dt.days
    life["span_days"] = (life["exit_date"] - life["entry_date"]).dt.days + 1
    life["occupancy"] = life["days_on_playlist"] / life["span_days"]
    life["duration_min"] = life["duration_ms"] / 60000.0
    span = (df["date"].max() - df["date"].min()).days + 1
    life["right_censored"] = life["exit_date"] >= (df["date"].max() - pd.Timedelta(days=2))
    life["catalog_share"] = life["days_on_playlist"] / span
    return life.sort_values("days_on_playlist", ascending=False)


def annotate_daily_stages(df: pd.DataFrame, life: pd.DataFrame) -> pd.DataFrame:
    daily = df.sort_values(["track_id", "date"]).copy()
    daily["days_so_far"] = daily.groupby("track_id").cumcount() + 1
    daily["prev_position"] = daily.groupby("track_id")["position"].shift(1)
    daily["rank_delta"] = daily.groupby("track_id")["position"].diff()
    daily["roll_delta"] = daily.groupby("track_id")["rank_delta"].transform(
        lambda s: s.rolling(3, min_periods=1).mean()
    )
    extra = life[["track_id"]].copy()
    extra["song_peak_position"] = life["peak_position"]
    extra["song_days_total"] = life["days_on_playlist"]
    daily = daily.merge(extra, on="track_id", how="left")

    def classify(row) -> str:
        if row["days_so_far"] <= 7:
            return "New Entry"
        delta = row["rank_delta"]
        if pd.isna(delta):
            delta = 0
        if row["position"] <= 10 and abs(delta) <= 2:
            return "Peak Phase"
        if delta <= -2:
            return "Growth Phase"
        if delta >= 2:
            return "Decline Phase"
        if row["position"] <= 10:
            return "Peak Phase"
        if 11 <= row["position"] <= 35:
            return "Mature Phase"
        return "Decline Phase"

    daily["lifecycle_stage"] = daily.apply(classify, axis=1)
    return daily


def daily_rotation(df: pd.DataFrame) -> pd.DataFrame:
    days = sorted(df["date"].unique())
    sets = {d: set(g["track_id"]) for d, g in df.groupby("date")}
    rows = []
    for i, day in enumerate(days):
        current = sets[day]
        if i == 0:
            entries = exits = 0
            jaccard = 1.0
        else:
            prev = sets[days[i - 1]]
            entries = len(current - prev)
            exits = len(prev - current)
            union = len(current | prev)
            jaccard = (len(current & prev) / union) if union else 1.0
        rows.append(
            {
                "date": day,
                "entries": entries,
                "exits": exits,
                "churn_rate": entries / 50.0,
                "turnover": (entries + exits) / 100.0,
                "stability": 1.0 - (entries / 50.0),
                "jaccard": jaccard,
                "unique_tracks": len(current),
                "explicit_share": float(df.loc[df["date"] == day, "is_explicit"].mean()),
                "single_share": float((df.loc[df["date"] == day, "album_type"] == "single").mean()),
                "avg_popularity": float(df.loc[df["date"] == day, "popularity"].mean()),
            }
        )
    out = pd.DataFrame(rows)
    out["month"] = pd.to_datetime(out["date"]).dt.to_period("M").astype(str)
    return out


def compute_kpis(life: pd.DataFrame, rotation: pd.DataFrame) -> dict:
    explicit = life[life["is_explicit"]]
    clean = life[~life["is_explicit"]]
    singles = life[life["album_type"] == "single"]
    albums = life[life["album_type"] == "album"]
    exp_days = explicit["days_on_playlist"].mean() if len(explicit) else np.nan
    clean_days = clean["days_on_playlist"].mean() if len(clean) else np.nan
    single_days = singles["days_on_playlist"].mean() if len(singles) else np.nan
    album_days = albums["days_on_playlist"].mean() if len(albums) else np.nan
    return {
        "avg_days_on_playlist": float(life["days_on_playlist"].mean()),
        "median_days_on_playlist": float(life["days_on_playlist"].median()),
        "entry_to_peak_days": float(life["time_to_peak_days"].mean()),
        "median_entry_to_peak": float(life["time_to_peak_days"].median()),
        "playlist_churn_rate": float(rotation["churn_rate"].mean()),
        "retention_stability_index": float(rotation["jaccard"].mean()),
        "explicit_lifecycle_score": float(exp_days / clean_days) if clean_days else np.nan,
        "single_album_longevity_ratio": float(single_days / album_days) if album_days else np.nan,
        "explicit_avg_days": float(exp_days),
        "clean_avg_days": float(clean_days),
        "single_avg_days": float(single_days),
        "album_avg_days": float(album_days),
        "unique_tracks": int(len(life)),
        "pct_peak_on_entry": float((life["time_to_peak_days"] == 0).mean()),
        "avg_peak_position": float(life["peak_position"].mean()),
    }


@dataclass
class MarketBundle:
    daily: pd.DataFrame
    life: pd.DataFrame
    rotation: pd.DataFrame
    kpis: dict
    validation: dict


def build_market(path: str | Path | None = None) -> MarketBundle:
    raw = load_raw(path)
    daily, report = validate_and_normalize(raw)
    life = build_lifecycle(daily)
    staged = annotate_daily_stages(daily, life)
    rotation = daily_rotation(staged)
    kpis = compute_kpis(life, rotation)
    return MarketBundle(
        daily=staged,
        life=life,
        rotation=rotation,
        kpis=kpis,
        validation=report,
    )


CORE_COLS = [
    "date",
    "position",
    "song",
    "artist",
    "popularity",
    "duration_ms",
    "album_type",
    "total_tracks",
    "is_explicit",
    "album_cover_url",
    "song_display",
    "artist_display",
    "song_norm",
    "artist_norm",
    "track_id",
]


def apply_filters(
    bundle: MarketBundle,
    start=None,
    end=None,
    stages: list[str] | None = None,
    explicit_mode: str = "All",
    album_types: list[str] | None = None,
) -> MarketBundle:
    daily = bundle.daily.copy()
    if start is not None:
        daily = daily[daily["date"] >= pd.to_datetime(start)]
    if end is not None:
        daily = daily[daily["date"] <= pd.to_datetime(end)]
    if explicit_mode == "Explicit only":
        daily = daily[daily["is_explicit"]]
    elif explicit_mode == "Clean only":
        daily = daily[~daily["is_explicit"]]
    if album_types:
        daily = daily[daily["album_type"].isin(album_types)]

    if daily.empty:
        empty_life = bundle.life.iloc[0:0].copy()
        empty_rot = bundle.rotation.iloc[0:0].copy()
        return MarketBundle(daily, empty_life, empty_rot, bundle.kpis, bundle.validation)

    core = daily[[c for c in CORE_COLS if c in daily.columns]].copy()
    life = build_lifecycle(core)
    restaged = annotate_daily_stages(core, life)
    if restaged.empty or life.empty:
        empty_rot = bundle.rotation.iloc[0:0].copy()
        return MarketBundle(restaged, life, empty_rot, bundle.kpis, bundle.validation)
    rotation = daily_rotation(restaged)
    kpis = compute_kpis(life, rotation)
    if stages and set(stages) != set(STAGES):
        restaged = restaged[restaged["lifecycle_stage"].isin(stages)]
        life = life[life["track_id"].isin(restaged["track_id"].unique())]
    return MarketBundle(restaged, life, rotation, kpis, bundle.validation)
