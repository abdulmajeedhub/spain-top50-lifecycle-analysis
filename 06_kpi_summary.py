import pandas as pd
lifecycle = pd.read_csv('lifecycle_with_buckets.csv')
stages = pd.read_csv('daily_with_stages.csv')
daily_flow = pd.read_csv('daily_churn.csv')
print("=== Popularity growth vs lifecycle stage ===")
pop_by_stage = stages.groupby('lifecycle_stage')['popularity'].mean().sort_values(ascending=False)
print(pop_by_stage.round(2))
print()
print("=== Peak popularity timing (days_to_peak distribution) ===")
print(lifecycle['days_to_peak'].describe().round(1))
print()
# Explicit Content Lifecycle Score: composite of relative avg_total_days
# and relative avg_popularity for explicit vs non-explicit, expressed as a ratio
explicit_days = lifecycle[lifecycle['is_explicit']]['total_days'].mean()
clean_days = lifecycle[~lifecycle['is_explicit']]['total_days'].mean()
explicit_pop = lifecycle[lifecycle['is_explicit']]['avg_popularity'].mean()
clean_pop = lifecycle[~lifecycle['is_explicit']]['avg_popularity'].mean()
explicit_lifecycle_score = (explicit_days / clean_days) # >1 = explicit content lasts longer
print(f"Explicit Content Lifecycle Score (explicit avg days / clean avg days): {explicit_lifecycle_score:.2f}")
print(f" Explicit avg popularity: {explicit_pop:.1f} | Clean avg popularity: {clean_pop:.1f}")
print()
# ===== FINAL KPI SUMMARY =====
kpis = {
"Average Days on Playlist": round(lifecycle['total_days'].mean(), 1),
"Entry-to-Peak Time (days, avg)": round(lifecycle['days_to_peak'].mean(), 1),
"Playlist Churn Rate (%/day)": round(daily_flow['churn_rate'].mean() * 100, 1),
"Retention Stability Index (%)": round(stages['lifecycle_stage'].isin(['Mature', 'Peak']).mean() * 100, 1),
"Explicit Content Lifecycle Score": round(explicit_lifecycle_score, 2),
"Single vs Album Longevity Ratio": round(
lifecycle[lifecycle['album_type'] == 'single']['total_days'].mean()
/ lifecycle[lifecycle['album_type'] == 'album']['total_days'].mean(), 2
),
}
print("=== FINAL KPI SUMMARY ===")
for k, v in kpis.items():
    print(f"{k}: {v}")
pd.Series(kpis).to_csv('final_kpis.csv', header=['value'])
print("\nSaved final_kpis.csv")