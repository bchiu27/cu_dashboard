import pandas as pd
import numpy as np

def transform_imported(df_wide):
    """Transform wide format data to long format for ONLY the three specific variables + 2024 data for existing variables"""
    
    df_wide = df_wide.copy()
    
    # Handle header rows
    if df_wide.iloc[0, 0] == 'Company Name' or pd.isna(df_wide.iloc[0, 0]):
        df_wide = df_wide.iloc[1:].reset_index(drop=True)
    
    # Get company name and EIN columns
    company_col = 0  # Company Name column index
    ein_col = 1      # EIN column index
    
    # **SCALE FACTOR - multiply all financial data by 1000**
    scale_factor = 1000
    
    # Define year ranges for the 3 new variables
    cash_years = list(range(2015, 2025))  # 2015-2024 (10 years)
    loans_years = list(range(2015, 2025))  # 2015-2024 (10 years)
    commercial_years = list(range(2018, 2025))  # 2018-2024 (7 years)
    
    # Extract data for the 3 new variables
    cash_on_hand_data = df_wide.iloc[:, 5:15].copy()  # Columns 5-14
    total_loans_data = df_wide.iloc[:, 15:25].copy()  # Columns 15-24
    commercial_loans_data = df_wide.iloc[:, 25:32].copy()  # Columns 25-31
    
    # **APPLY SCALING TO ALL FINANCIAL DATA**
    cash_on_hand_data = cash_on_hand_data * scale_factor
    total_loans_data = total_loans_data * scale_factor
    commercial_loans_data = commercial_loans_data * scale_factor
    
    # Extract 2024 data for existing variables
    net_income_2024 = df_wide.iloc[:, 41].copy() * scale_factor  # **SCALED**
    total_assets_2024 = df_wide.iloc[:, 51].copy() * scale_factor  # **SCALED**
    
    # Assign proper column names
    cash_on_hand_data.columns = cash_years
    total_loans_data.columns = loans_years
    commercial_loans_data.columns = commercial_years
    
    # Add company name and EIN back to each dataset
    cash_on_hand_data.insert(0, 'Company Name', df_wide.iloc[:, company_col])
    cash_on_hand_data.insert(1, 'EIN', df_wide.iloc[:, ein_col])
    
    total_loans_data.insert(0, 'Company Name', df_wide.iloc[:, company_col])
    total_loans_data.insert(1, 'EIN', df_wide.iloc[:, ein_col])
    
    commercial_loans_data.insert(0, 'Company Name', df_wide.iloc[:, company_col])
    commercial_loans_data.insert(1, 'EIN', df_wide.iloc[:, ein_col])
    
    # Create 2024 dataframe for existing variables
    existing_vars_2024 = pd.DataFrame({
        'Company Name': df_wide.iloc[:, company_col],
        'EIN': df_wide.iloc[:, ein_col],
        'Year': 2024,
        'Net Income': net_income_2024,
        'Total Assets': total_assets_2024
    })
    
    # Melt each variable to long format
    cash_melted = pd.melt(cash_on_hand_data, 
                         id_vars=['Company Name', 'EIN'],
                         var_name='Year', 
                         value_name='Cash On Hand')
    
    loans_melted = pd.melt(total_loans_data,
                          id_vars=['Company Name', 'EIN'],
                          var_name='Year',
                          value_name='Total Loans & Leases')
    
    commercial_melted = pd.melt(commercial_loans_data,
                               id_vars=['Company Name', 'EIN'],
                               var_name='Year',
                               value_name='Commercial and Industrial Loans')
    
    # Merge the 3 new variables together
    final_df = cash_melted.merge(
        loans_melted, 
        on=['Company Name', 'EIN', 'Year'], 
        how='outer'
    )
    
    final_df = final_df.merge(
        commercial_melted, 
        on=['Company Name', 'EIN', 'Year'], 
        how='outer'
    )
    
    # Merge with 2024 existing variables
    final_df = final_df.merge(
        existing_vars_2024,
        on=['Company Name', 'EIN', 'Year'],
        how='outer'
    )
    
    # Clean up column names and data types
    final_df = final_df.rename(columns={'Company Name': 'name', 'EIN': 'ein'})
    final_df['Year'] = final_df['Year'].astype(int)
    
    # Clean the EIN column
    final_df['ein'] = final_df['ein'].astype(str).str.strip()
    
    # Remove contaminated header rows and empty rows
    final_df = final_df[~final_df['name'].astype(str).str.contains('Company Name', na=False)]
    final_df = final_df[final_df['name'].notna()]
    final_df = final_df[final_df['ein'].notna()]
    final_df = final_df[final_df['ein'] != 'nan']
    
    # Convert financial columns to numeric
    financial_cols = ['Cash On Hand', 'Total Loans & Leases', 'Commercial and Industrial Loans', 'Net Income', 'Total Assets']
    for col in financial_cols:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
    
    # Remove rows where ALL financial columns are NA
    final_df = final_df.dropna(subset=financial_cols, how='all')
    
    return final_df

# Read the existing long format data
df1 = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
    sheet_name="Combined_Financials",
    dtype={
        "ein": str,
        "Year": int, 
        "Total Assets": float,
        "Total Liabilities": float,
        "Total Revenue": float,
        "Total Expenses": float,
        "Net Income": float,
        "Investment Income": float,
    })

# Ensure EIN is string format in the main dataset
df1['ein'] = df1['ein'].astype(str).str.strip()

# Read the wide format data
df2_wide = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\imported_cu.xlsx",
    sheet_name="just_21",
    header=None)

# Transform wide format to long format
df2_long = transform_imported(df2_wide)

print("Transformed wide data to long format:")
print(df2_long.head())
print(f"Shape: {df2_long.shape}")
print(f"Unique EINs in transformed data: {df2_long['ein'].nunique()}")

# Check for EIN matches before merging
common_eins = set(df1['ein'].unique()) & set(df2_long['ein'].unique())
print(f"Common EINs between datasets: {len(common_eins)}")

# Separate 2024 rows (new rows to add) from other years (columns to merge)
df2_2024 = df2_long[df2_long['Year'] == 2024].copy()
df2_other_years = df2_long[df2_long['Year'] != 2024].copy()

# First, merge the 3 new variables for existing years
df_combined = df1.merge(
    df2_other_years[['ein', 'Year', 'Cash On Hand', 'Total Loans & Leases', 'Commercial and Industrial Loans']], 
    on=['ein', 'Year'], 
    how='left'
)

# Then, append 2024 rows as completely new rows
if not df2_2024.empty:
    # Prepare 2024 rows with all required columns, setting missing ones to NaN
    df2_2024_full = df2_2024.copy()
    
    # Add missing columns from df1 that aren't in df2_2024
    existing_columns = set(df1.columns)
    new_columns = set(df2_2024.columns)
    missing_columns = existing_columns - new_columns
    
    for col in missing_columns:
        df2_2024_full[col] = np.nan
    
    # Reorder columns to match df_combined
    df2_2024_full = df2_2024_full[df_combined.columns]
    
    # Append 2024 rows
    df_combined = pd.concat([df_combined, df2_2024_full], ignore_index=True)

print(f"\nCombined DataFrame with 2024 rows added:")
print(df_combined.tail(25))  # Show last 25 rows to see 2024 data
print(f"\nTotal records: {len(df_combined)}")
print(f"Unique organizations: {df_combined['ein'].nunique()}")
print(f"Years covered: {sorted(df_combined['Year'].unique())}")

# Show summary of new columns and 2024 data
print("\nNew columns added to existing rows:")
new_cols = ['Cash On Hand', 'Total Loans & Leases', 'Commercial and Industrial Loans']
for col in new_cols:
    non_null_count = df_combined[col].notna().sum()
    print(f"- {col}: {non_null_count} non-null values")

print(f"\n2024 rows added: {len(df_combined[df_combined['Year'] == 2024])}")
print("2024 Net Income values:", df_combined[df_combined['Year'] == 2024]['Net Income'].notna().sum())
print("2024 Total Assets values:", df_combined[df_combined['Year'] == 2024]['Total Assets'].notna().sum())

def add_combined_sheet(dataframe, filename=r'c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx'):
    """Add combined financial data as a new sheet to credit union data file"""
    try:
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name='Combined_Financials_2', index=False)
        print(f"Successfully saved {len(dataframe)} records to {filename}")
        print("New sheet 'Combined_Financials_2' created with the combined data")
    except FileNotFoundError:
        dataframe.to_excel(filename, sheet_name='Combined_Financials_2', index=False)
        print(f"Created new file {filename} with {len(dataframe)} records")
    except Exception as e:
        print(f"Error: {e}")

# Save the combined data
add_combined_sheet(df_combined)
