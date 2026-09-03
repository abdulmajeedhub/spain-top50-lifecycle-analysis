import pandas as pd
import numpy as np
df = pd.read_csv('cleaned_data.csv', parse_dates=['date'])
lifecycle = pd.read_csv('lifecycle_table.csv', parse_dates=['entry_date', 'exit_date', 'peak_date'])
df = df.sort_values(['track_key', 'date']).reset_index(drop=True)
df = df.merge(lifecycle[['track_key', 'entry_date']], on='track_key')
df['days_since_entry'] = (df['date'] - df['entry_date']).dt.days
# rank trend: position change vs previous day's appearance for the same track
df['prev_position'] = df.groupby('track_key')['position'].shift(1)
df['rank_change'] = df['prev_position'] - df['position'] # positive = improving (moved up chart)
def classify(row):
    if row['days_since_entry'] <= 7:
        return 'New Entry'
    if pd.isna(row['rank_change']):
        return 'New Entry'
    if row['position'] <= 10 and row['rank_change'] >= -2:
        return 'Peak'
    if row['rank_change'] > 2:
        return 'Growth'
    if row['rank_change'] < -2:
        return 'Decline'
    return 'Mature'
df['lifecycle_stage'] = df.apply(classify, axis=1)
print("Stage distribution (all daily observations):")
print(df['lifecycle_stage'].value_counts())
print()
print("Stage distribution (% of observations):")
print((df['lifecycle_stage'].value_counts(normalize=True) * 100).round(1))
df.to_csv('daily_with_stages.csv', index=False)
print("\nSaved daily_with_stages.csv")