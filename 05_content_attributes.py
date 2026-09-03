import pandas as pd
lifecycle = pd.read_csv('lifecycle_table.csv')
print("=== Explicit vs Clean content ===")
explicit_cmp = lifecycle.groupby('is_explicit').agg(
avg_total_days=('total_days', 'mean'),
avg_days_to_peak=('days_to_peak', 'mean'),
avg_peak_position=('peak_position', 'mean'),
n_songs=('song', 'count'),
)
print(explicit_cmp.round(2))
print()
print("=== Single vs Album ===")
album_cmp = lifecycle.groupby('album_type').agg(
avg_total_days=('total_days', 'mean'),
avg_days_to_peak=('days_to_peak', 'mean'),
avg_peak_position=('peak_position', 'mean'),
n_songs=('song', 'count'),
)
print(album_cmp.round(2))
print()
print("=== Song duration vs total_days on chart (correlation) ===")
corr = lifecycle[['duration_ms', 'total_days']].corr().iloc[0, 1]
print(f"Correlation (duration_ms vs total_days): {corr:.3f}")
print()
print("=== Album size (total_tracks) vs lifecycle stability (total_days) ===")
lifecycle['album_size_bucket'] = pd.cut(
lifecycle['total_tracks'], bins=[0, 1, 5, 12, 30],
labels=['Single (1)', 'EP (2-5)', 'Album (6-12)', 'Large Album (13+)']
)
size_cmp = lifecycle.groupby('album_size_bucket', observed=True).agg(
avg_total_days=('total_days', 'mean'),
n_songs=('song', 'count'),
)
print(size_cmp.round(2))
# Single vs Album Longevity Ratio (one of the required KPIs)
single_avg = lifecycle[lifecycle['album_type'] == 'single']['total_days'].mean()
album_avg = lifecycle[lifecycle['album_type'] == 'album']['total_days'].mean()
ratio = single_avg / album_avg
print(f"\nSingle vs Album Longevity Ratio: {ratio:.2f} (single avg {single_avg:.1f}d / album avg {album_avg:.1f}d)")
lifecycle.to_csv('lifecycle_with_buckets.csv', index=False)
print("\nSaved lifecycle_with_buckets.csv")