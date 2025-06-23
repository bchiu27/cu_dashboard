import pandas as pd
import numpy as np

# Read the two sheets
df1 = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
    sheet_name="Financials",
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

df2 = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
    sheet_name="Financial_remaining",
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

# Ensure both dataframes have the same column names and order
expected_columns = ['ein', 'name', 'Year', 'Total Assets', 'Total Liabilities', 
                   'Total Revenue', 'Total Expenses', 'Net Income', 'Investment Income']

# Reorder columns if they exist, add missing ones with NaN
for df in [df1, df2]:
    for col in expected_columns:
        if col not in df.columns:
            df[col] = np.nan

df1['name'] = df1['name'].str.replace('Achieve Credit Union Inc', 'Achieva Credit Union')
# Reorder columns to match
df1 = df1[expected_columns]
df2 = df2[expected_columns]

# Combine the dataframes by appending (concatenating)
df_combined = pd.concat([df1, df2], ignore_index=True)

# Sort by EIN and Year for better organization
df_combined = df_combined.sort_values(['ein', 'Year']).reset_index(drop=True)

print("Combined DataFrame:")
print(df_combined.head(10))
print(f"\nTotal records: {len(df_combined)}")
print(f"Unique organizations: {df_combined['ein'].nunique()}")

def add_combined_sheet(dataframe, filename='credit_union_data.xlsx'):
    """Add combined financial data as a new sheet to credit union data file"""
    try:
        # Try to add to existing file using append mode
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name='Combined_Financials', index=False)
        print(f"Successfully saved {len(dataframe)} records to {filename}")
    except FileNotFoundError:
        # File doesn't exist, create one
        dataframe.to_excel(filename, sheet_name='Combined_Financials', index=False)
        print(f"Created new file {filename} with {len(dataframe)} records")
    except Exception as e:
        print(f"Error: {e}")

add_combined_sheet(df_combined)
