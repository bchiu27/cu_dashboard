
import pandas as pd
import numpy as np

df1 = pd.read_excel(
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
df2 = pd.read_excel(
    r"c:\Users\bchiu\Downloads\credit_union\credit_union_data.xlsx",
    sheet_name="Form_990_data",
    dtype={
        "name": str,
        "ein": str,
        "tax_prd_yr": int,
        "total_expenses": float,
        "investment_income": float,
        "executive_compensation": float,
        "total_assets": float
    })
df2 = df2.rename(columns={'tax_prd_yr': 'year'})
df_merged = pd.merge(
    df1,
    df2,
    on=['ein', 'year'],
    how='outer',
)

print(df_merged)

def add_ceo_sheet(dataframe, filename='credit_union_data.xlsx'):
    """Add CEO compensation data as a new sheet to credit union data file"""
    try:
        # Try to add to existing file using append mode
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name='full_data', index=False)
    except FileNotFoundError:
        # File doesn't exist, create new one
        dataframe.to_excel(filename, sheet_name='full_data', index=False)
    except Exception as e:
        print(f"Error: {e}")
        # Backup: save as separate file
        backup_filename = 'ceo_compensation_backup.xlsx'
        dataframe.to_excel(backup_filename, sheet_name='full_data', index=False)
add_ceo_sheet(df_merged)