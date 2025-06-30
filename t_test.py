import pandas as pd
import numpy as np
from scipy.stats import ttest_1samp

# Load data
df = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
    sheet_name="CEO_Comp",
    dtype={
        "name": str,
        "ein": str,
        "year": int,
        "total": float,
        "ceo_name": str,
        "compensation": float
    })


df_sorted = df.sort_values(['ein', 'year'])

# Calculate percentage change for each year
df_sorted['pct_increase'] = df_sorted.groupby('ein')['total_comp'].pct_change() * 100


m_and_a = df_sorted[df_sorted['m_or_a'] == True]
non_m_and_a = df_sorted[df_sorted['m_or_a'] == False]

# Calculate avg comp increase for M&A year
avg_m_and_a = m_and_a.groupby('ein')['pct_increase'].mean().reset_index()
avg_m_and_a.columns = ['ein', 'avg_pct_increase_m_and_a']

# Calculate avg comp increase for non-M&A year 
avg_non_m_and_a = non_m_and_a.groupby('ein')['pct_increase'].mean().reset_index()
avg_non_m_and_a.columns = ['ein', 'avg_pct_increase_non_m_and_a']

# Merge averages and calculate difference
results = avg_m_and_a.merge(avg_non_m_and_a, on='ein', how='outer')
results['difference'] = results['avg_pct_increase_m_and_a'] - results['avg_pct_increase_non_m_and_a']

# Drop companies with missing data
differences = results['difference'].dropna()

# Run t-test
t_stat, p_value = ttest_1samp(differences, 0)

print(f"Sample size: {len(differences)} companies")
print(f"Mean difference: {differences.mean():.2f}%")
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_value:.4f}")

# Show  results
print("\nResults by company:")
print(results[['ein', 'avg_pct_increase_m_and_a', 'avg_pct_increase_non_m_and_a', 'difference']])