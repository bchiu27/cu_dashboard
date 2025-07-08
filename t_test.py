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

# Identify M&A years
m_and_a = df_sorted[df_sorted['m_or_a'] == True]
non_m_and_a = df_sorted[df_sorted['m_or_a'] == False]

avg_m_and_a = m_and_a.groupby('name')['pct_increase'].mean().reset_index()
avg_m_and_a.columns = ['name', 'avg_pct_increase_m_and_a']

avg_non_m_and_a = non_m_and_a.groupby('name')['pct_increase'].mean().reset_index()
avg_non_m_and_a.columns = ['name', 'avg_pct_increase_non_m_and_a']

# Merge averages and calculate difference
results = avg_m_and_a.merge(avg_non_m_and_a, on='name', how='outer')
results['difference'] = results['avg_pct_increase_m_and_a'] - results['avg_pct_increase_non_m_and_a']

# Drop companies with missing data
differences = results['difference'].dropna()

# Run t-test 1
t_stat, p_value = ttest_1samp(differences, 0)

# Add t-test statistics at the bottom
stats_row = pd.DataFrame({
    'name': ['T-Statistic', 'P-Value'],
    'avg_pct_increase_m_and_a': [np.nan, np.nan],
    'avg_pct_increase_non_m_and_a': [np.nan, np.nan],
    'difference': [t_stat, p_value]
})

results_with_stats = pd.concat([results, stats_row], ignore_index=True)

print(f"t-test 1 Sample size: {len(differences)} companies")
print(f"mean difference: {differences.mean():.2f}%")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.4f}")

# t-test 2 Analyze 3 years before and after first M&A for each credit union

# Step 1: Identify first M&A year for each credit union (using name)
first_ma = df_sorted[df_sorted['m_or_a'] == True].groupby('name')['year'].min().reset_index()
first_ma.columns = ['name', 'first_ma_year']

# Step 2: Function to check if 3 years before and after exist
def check_complete_periods(name, first_year, df):
    """Check if credit union has complete 3 years before and after first M&A"""
    years = df[df['name'] == name]['year'].tolist()
    
    # Define required years (excluding M&A year itself)
    pre_years = [first_year - 3, first_year - 2, first_year - 1]
    post_years = [first_year + 1, first_year + 2, first_year + 3]
    
    missing_pre = [y for y in pre_years if y not in years]
    missing_post = [y for y in post_years if y not in years]
    
    return missing_pre, missing_post

# Step 3: Check all credit unions and track exclusions
valid_names = []
excluded_results = []

print("\n" + "="*60)
print("CREDIT UNION INCLUSION/EXCLUSION ANALYSIS")
print("="*60)

for _, row in first_ma.iterrows():
    missing_pre, missing_post = check_complete_periods(row['name'], row['first_ma_year'], df_sorted)
    
    if missing_pre or missing_post:
        reason = 'Excluded Reason: '
        if missing_pre:
            reason += f"missing 3 years before: {missing_pre}. "
        if missing_post:
            reason += f"missing 3 years after: {missing_post}."
        
        excluded_results.append({
            'name': row['name'],
            'avg_pct_increase_pre': np.nan,
            'avg_pct_increase_post': np.nan,
            'difference': np.nan,
            'reason': reason
        })
        
        print(f"EXCLUDED: {row['name']} - First M&A year: {row['first_ma_year']}")
        print(f"  {reason}")
        print()
    else:
        valid_names.append(row['name'])
        print(f"INCLUDED: {row['name']} - First M&A year: {row['first_ma_year']}")

print(f"\nSUMMARY: {len(valid_names)} credit unions included, {len(excluded_results)} excluded")

# Step 4: Calculate 3-year before/after averages for valid credit unions
def assign_period(row, first_ma_dict):
    """Assign period label based on first M&A year"""
    if row['name'] not in first_ma_dict:
        return np.nan
    
    first_year = first_ma_dict[row['name']]
    
    if row['year'] < first_year and row['year'] >= first_year - 3:
        return 'pre'
    elif row['year'] > first_year and row['year'] <= first_year + 3:
        return 'post'
    else:
        return np.nan

# Create dictionary for faster lookup
first_ma_dict = dict(zip(first_ma['name'], first_ma['first_ma_year']))

# Filter to valid credit unions and assign periods
analysis_df = df_sorted[df_sorted['name'].isin(valid_names)].copy()
analysis_df['period'] = analysis_df.apply(lambda row: assign_period(row, first_ma_dict), axis=1)

# Calculate average growth rates by period
if len(analysis_df) > 0:
    avg_growth = analysis_df.groupby(['name', 'period'])['pct_increase'].mean().unstack().reset_index()
    
    # Handle column naming safely
    avg_growth.columns.name = None
    current_cols = list(avg_growth.columns)
    
    # Create new column mapping
    col_mapping = {'name': 'name'}
    if 'post' in current_cols:
        col_mapping['post'] = 'avg_pct_increase_post'
    if 'pre' in current_cols:
        col_mapping['pre'] = 'avg_pct_increase_pre'
    
    avg_growth = avg_growth.rename(columns=col_mapping)
    
    # Ensure both columns exist
    if 'avg_pct_increase_pre' not in avg_growth.columns:
        avg_growth['avg_pct_increase_pre'] = np.nan
    if 'avg_pct_increase_post' not in avg_growth.columns:
        avg_growth['avg_pct_increase_post'] = np.nan
    
    # Calculate difference
    avg_growth['difference'] = avg_growth['avg_pct_increase_post'] - avg_growth['avg_pct_increase_pre']
    
    # Create final results with included credit unions
    t_test_2_results = avg_growth[['name', 'avg_pct_increase_pre', 'avg_pct_increase_post', 'difference']].copy()
    t_test_2_results['reason'] = ''
    
    # Add excluded credit unions to the same dataframe
    for excluded in excluded_results:
        excluded_row = pd.DataFrame({
            'name': [excluded['name']],
            'avg_pct_increase_pre': [excluded['avg_pct_increase_pre']],
            'avg_pct_increase_post': [excluded['avg_pct_increase_post']],
            'difference': [excluded['difference']],
            'reason': [excluded['reason']]
        })
        
        t_test_2_results = pd.concat([t_test_2_results, excluded_row], ignore_index=True)
    
    # Run t-test for valid differences
    valid_differences_2 = t_test_2_results[t_test_2_results['reason'] == '']['difference'].dropna()
    
    if len(valid_differences_2) > 0:
        t_stat_2, p_value_2 = ttest_1samp(valid_differences_2, 0)
        
        # Add t-test statistics at the bottom
        stats_row_2 = pd.DataFrame({
            'name': ['T-Statistic', 'P-Value'],
            'avg_pct_increase_pre': [np.nan, np.nan],
            'avg_pct_increase_post': [np.nan, np.nan],
            'difference': [t_stat_2, p_value_2],
            'reason': ['', '']
        })
        
        t_test_2_results = pd.concat([t_test_2_results, stats_row_2], ignore_index=True)
        
        print("\n" + "="*60)
        print("T-TEST 2 RESULTS: 3 YEARS BEFORE vs 3 YEARS AFTER FIRST M&A")
        print("="*60)
        print(f"Sample size: {len(valid_differences_2)} companies")
        print(f"Mean difference (post - pre): {valid_differences_2.mean():.2f}%")
        print(f"T-statistic: {t_stat_2:.4f}")
        print(f"P-value: {p_value_2:.4f}")
    else:
        print("No valid credit unions found for 3-year before/after analysis")
        t_test_2_results = pd.DataFrame()
else:
    t_test_2_results = pd.DataFrame()

def add_combined_sheet(dataframe, sheet_name, filename=r'c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx'):
    """Add combined financial data as a new sheet to credit union data file"""
    try:
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Successfully saved {len(dataframe)} records to sheet '{sheet_name}'")
    except FileNotFoundError:
        dataframe.to_excel(filename, sheet_name=sheet_name, index=False)
        print(f"Created new file {filename} with {len(dataframe)} records")
    except Exception as e:
        print(f"Error: {e}")

# Save both results
add_combined_sheet(results_with_stats, 't_test_1')

if len(t_test_2_results) > 0:
    add_combined_sheet(t_test_2_results, 't_test_2')
