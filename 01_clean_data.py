import pandas as pd

# --- Load ---
df = pd.read_csv('Atlantic_Spain.csv')

# --- Fix date format (source is DD-MM-YYYY) ---
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

# --- Fix the duplicated-day issue (2025-03-01 had 100 rows, two snapshots
# tagged with the same date). Keep the first occurrence of each (date, position). ---
before = len(df)
df = df.drop_duplicates(subset=['date', 'position'], keep='first')
print(f"Dropped {before - len(df)} duplicate (date, position) rows (from 2025-03-01 anomaly)")

# --- Normalize song/artist names for grouping, but keep a clean display name ---
# key used to identify "the same song" across the whole dataset
df['song_key'] = df['song'].str.strip().str.lower()
df['artist_key'] = df['artist'].str.strip().str.lower()
df['track_key'] = df['song_key'] + ' || ' + df['artist_key']


# pick the most frequent raw spelling as the canonical display name for each track_key
canonical_names = (
    df.groupby('track_key')['song']
    .agg(lambda x: x.value_counts().idxmax())
    .rename('song_display')
)
canonical_artists = (
    df.groupby('track_key')['artist']
    .agg(lambda x: x.value_counts().idxmax())
    .rename('artist_display')
)

df = df.merge(canonical_names, on='track_key').merge(canonical_artists, on='track_key')

# --- Sanity checks ---
assert df.groupby('date').size().eq(50).all(), "Some day still doesn't have exactly 50 rows!"
print(f"Final shape: {df.shape}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()} ({df['date'].nunique()} days)")
print(f"Unique tracks: {df['track_key'].nunique()}")

# --- Save checkpoint ---
df.to_csv('cleaned_data.csv', index=False)
print("Saved cleaned_data.csv")