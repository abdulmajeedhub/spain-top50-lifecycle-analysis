import pandas as pd
df = pd.read_csv('cleaned_data.csv', parse_dates=['date'])
lifecycle = (
df.groupby('track_key')
.agg(
song=('song_display', 'first'),
artist=('artist_display', 'first'),
entry_date=('date', 'min'),
exit_date=('date', 'max'),
total_days=('date', 'nunique'),
peak_position=('position', 'min'),
album_type=('album_type', 'first'),
total_tracks=('total_tracks', 'first'),
is_explicit=('is_explicit', 'first'),
duration_ms=('duration_ms', 'first'),
avg_popularity=('popularity', 'mean'),
max_popularity=('popularity', 'max'),
)
.reset_index()
)
# date of peak position (first date it hit its best rank)
peak_dates = (
df.sort_values('date')
.merge(lifecycle[['track_key', 'peak_position']], on='track_key')
.query('position == peak_position')
.groupby('track_key')['date']
.min()
.rename('peak_date')
)
lifecycle = lifecycle.merge(peak_dates, on='track_key')
lifecycle['days_to_peak'] = (lifecycle['peak_date'] - lifecycle['entry_date']).dt.days
lifecycle['is_still_active'] = lifecycle['exit_date'] == df['date'].max()
lifecycle = lifecycle.sort_values('total_days', ascending=False).reset_index(drop=True)
print(f"Total unique tracks: {len(lifecycle)}")
print(f"Avg total_days: {lifecycle['total_days'].mean():.1f}")
print(f"Avg days_to_peak: {lifecycle['days_to_peak'].mean():.1f}")
print()
print("Top 5 longest-charting songs:")
print(lifecycle[['song', 'artist', 'total_days', 'peak_position', 'days_to_peak']].head())
lifecycle.to_csv('lifecycle_table.csv', index=False)
print("\nSaved lifecycle_table.csv")