import pandas as pd
import numpy as np

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
df = df.dropna(subset=["compensation"])
# print(df)
# print(df.isnull().sum())
# print(df[df['other'].isnull()])
df = df.fillna(0)
print(df)
def standardize_ceo_names(df):
    """Standardize CEO names by grouping any names that share first or last name,
       then replacing each group with its most frequent name.
       i.e. 'Richard Brandsma (three matches) and Rick Brandsma (one matches) -> Richard Brandsma'"""
    for cu in df['name'].unique():
        cu_df = df[df['name'] == cu]
        ceo_names = list(cu_df['ceo_name'].unique())
        if len(ceo_names) <= 1:
            continue

        # 1. Build adjacency: connect any two names sharing first or last name
        adj = {name: set() for name in ceo_names}
        for i, name1 in enumerate(ceo_names):
            f1, l1 = name1.split()[0].lower(), name1.split()[-1].lower()
            for name2 in ceo_names[i+1:]:
                f2, l2 = name2.split()[0].lower(), name2.split()[-1].lower()
                if f1 == f2 or l1 == l2:
                    adj[name1].add(name2)
                    adj[name2].add(name1)

        # 2. Find connected components (groups of linked names) via simple DFS
        visited = set()
        for name in ceo_names:
            if name in visited:
                continue
            stack = [name]
            group = []
            while stack:
                curr = stack.pop()
                if curr in visited:
                    continue
                visited.add(curr)
                group.append(curr)
                # add its neighbors to explore
                stack.extend(adj[curr] - visited)

            # 3. In each group, choose the most frequent name from the original counts
            if len(group) > 1:
                counts = cu_df['ceo_name'].value_counts()
                canonical = max(group, key=lambda x: counts.get(x, 0))
                df.loc[
                    (df['name'] == cu) & (df['ceo_name'].isin(group)),
                    'ceo_name'
                ] = canonical

    return df
df_clean = standardize_ceo_names(df)
def ceo_comparison(df):
    df_clean = df.copy()
    # 1) Sort so each CU’s years are consecutive
    df_clean = df_clean.sort_values(['name','year'])
    # 2) Initialize to False
    df_clean['ceo_change'] = False

    # 3) Loop per CU
    for cu in df_clean['name'].unique():
        sub = df_clean[df_clean['name']==cu]  # only this CU
        idxs = sub.index.tolist()
        names = sub['ceo_name'].tolist()

        # 4) Compare each year to the prior one (within the same CU!)
        for i in range(1, len(names)):
            if names[i] != names[i-1]:
                df_clean.loc[idxs[i], 'ceo_change'] = True
    return df_clean

def add_merger_acquisition(df):
    """Mark each year as True if the CU had a merger or acquisition that year based on the provided data"""
    df_ma = df.copy()
    df_ma['m_or_a'] = False  # Initialize to False
    merger_data = {
        'Advia Credit Union': [2016, 2017, 2019],
        'Five Star Credit Union': [2014, 2015],
        'Greenstate Credit Union': [2020, 2022],
        'Wings Financial Credit Union': [2020, 2021, 2023],
        'Achieva Credit Union': [2015, 2018],
        'Alabama One Credit Union': [2021, 2023],
        'Avadian Credit Union': [2016, 2022],
        'Crane Credit Union': [2020, 2021],
        'Dfcu Financial': [2023],
        'Fairwinds Credit Union': [2019, 2022],
        'First Commerce Credit Union': [2014, 2020],
        'Georgias Own Credit Union': [2018, 2022],
        'Harborstone Credit Union': [2024],
        'Lake Michigan Credit Union': [2018, 2021],
        'Land Of Lincoln Credit Union': [2023],
        'Lge Community Credit Union': [2018, 2023],
        'Midflorida Credit Union': [2019],
        'Numark Credit Union': [2021, 2023],
        'Royal Credit Union': [2016, 2022],
        'Sound Credit Union': [2019],
        'Vystar Credit Union': [2019, 2022]
    }
    # Iterate through each row and check if the CU and year match a M&A year
    for index, row in df_ma.iterrows():
        cu_name = row['name']
        year = row['year']
        if cu_name in merger_data and year in merger_data[cu_name]:
            df_ma.loc[index, 'm_or_a'] = True
    return df_ma

df_clean = ceo_comparison(df_clean)
df_clean = add_merger_acquisition(df_clean)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
print(df_clean)

df_clean = df_clean.rename(columns={
    'other': 'other_comp',
    'total': 'total_comp'
})

def add_ceo_sheet(dataframe, filename='credit_union_data.xlsx'):
    """Add CEO compensation data as a new sheet to credit union data file"""
    try:
        # Try to add to existing file using append mode
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name='CEO_Comp', index=False)
    except FileNotFoundError:
        # File doesn't exist, create new one
        dataframe.to_excel(filename, sheet_name='CEO_Comp', index=False)
    except Exception as e:
        print(f"Error: {e}")
add_ceo_sheet(df_clean)
