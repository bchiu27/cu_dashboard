import pandas as pd
import numpy as np
import requests
import re

ein = "381686050"   #EIN for Credit Union
url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
params = {"q": "Advia Credit Union"}
cu_list = [
    "Advia Credit Union",
    "Five Star Credit Union",
    "Greenstate Credit Union",
    "Wings Financial Credit Union",
    "Alabama One Credit Union",
    "Avadian Credit Union",
    "Crane Credit Union",
    "DFCU Financial",
    "FAIRWINDS Credit Union",
    "First Commerce Credit Union",
    "Georgia's Own Credit Union",
    "Harborstone Credit Union",
    "Lake Michigan Credit Union",
    "Land of Lincoln Credit Union",
    "LGE Community Credit Union",
    "MIDFLORIDA Credit Union",
    "NuMark Credit Union",
    "Royal Credit Union",
    "Sound Credit Union",
    "VyStar Credit Union"
]
all_cu_data = []

def get_credit_union_ein(name):
    """
    Fetch the EIN and name of a credit union by its name.
    Parameters:
    name (str): The name of the credit union.
    """

    url = "https://projects.propublica.org/nonprofits/api/v2/search.json"
    params = {"q": name}
    # Make a GET request to the API and parse the JSON response
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("organizations"):
       org = data["organizations"][0]
       return org.get("ein"), org['name']
    else:
        return None, None


def get_credit_union_data(ein):
    """
    Fetch data from a given API endpoint.

    Parameters:
    url (str): The API endpoint URL.
    params (dict, optional): Dictionary of query parameters to include in the request.

    Returns:
    pd.DataFrame: Data fetched from the API as a pandas DataFrame.
    """
    url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
    data = response.json()
    filings = data.get("filings_with_data", [])
    if not filings: 
        return pd.DataFrame()  # Return empty DataFrame if no filings found
    df = pd.json_normalize(filings)

    #Add organization data
    org_data = data.get("organization", {})
    for key, value in org_data.items():
        df[key] = value
    # print("Organization Data:", org_data)
    print("Org name:", org_data.get("name", "").lower())
    if any(substr in org_data.get("name", "").lower() for substr in ["chartered in", "credit unions in"]):
        if "sort_name" in org_data:
            fixed_name = re.sub(r'^\d+\s+', '', org_data["sort_name"]).strip()
            print("Fixed name:", fixed_name)
            df["name"] = fixed_name

    #Filter relevant columns
    df = df[["name", "ein", "tax_prd_yr", "totassetsend", "totliabend", "totrevenue", "totfuncexpns", "invstmntinc"]]
    df.rename(columns={
        "tax_prd_yr": "Year",
        "totassetsend": "Total Assets",
        "totliabend": "Total Liabilities",
        "totrevenue": "Total Revenue",
        "totfuncexpns": "Total Expenses",
        "invstmntinc": "Investment Income"
    }, inplace=True)
    return df

# def get_ceo_compensation(ein):
#     """
#     Fetch CEO compensation data for a given EIN.
    
#     Parameters:
#     ein (str): The EIN of the credit union.
    
#     Returns:
#     pd.DataFrame: DataFrame containing CEO compensation information.
#     """
#     url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         raise Exception(f"Error fetching data: {response.status_code} - {response.text}")
    
#     data = response.json()
#     filings = data.get("filings_with_data", [])
#     records = []
#     for filing in filings:
#         year = filing.get("tax_prd_yr")
#         officers = filing.get("officers", [])
#         for officer in officers:
#             if "ceo" in officer.get("title", "").lower() or "chief executive officer" in officer.get("title", "").lower():
#                 records.append({
#                     "year": year,
#                     "name": officer.get("name"),
#                     "title": officer.get("title"),
#                     "compensation": officer.get("compensation"),
#                     "ein": ein
#                 })
#                 break  # Stop after finding the first CEO in the filing
#     if not officers:
#         return pd.DataFrame()  # Return empty DataFrame if no officers found
    
#     df = pd.DataFrame(records)
#     return df

for cu in cu_list:
    ein, name = get_credit_union_ein(cu)
    if ein:
        print(f"Found credit union: {name} with EIN: {ein}")
        df = get_credit_union_data(ein)
        if not df.empty:
            all_cu_data.append(df)
        else:
            print(f"No data available for {cu}.")
    else:
        print(f"Credit union {cu} not found.")
# 
# for cu in cu_list:
#     ein, name = get_credit_union_ein(cu)
#     if ein:
#         print(f"Found credit union: {name} with EIN: {ein}")
#         df = get_ceo_compensation(ein)
#         if not df.empty:
#             all_cu_data.append(df)
#         else:
#             print(f"No data available for {cu}.")
#     else:
#         print(f"Credit union {cu} not found.") 

if all_cu_data:
    combined_df = pd.concat(all_cu_data, ignore_index=True)
    combined_df['Net Income'] = combined_df['Total Revenue'] - combined_df['Total Expenses']
    # Download the data to Excel file
    with pd.ExcelWriter('credit_union_data.xlsx', engine='openpyxl') as writer:
        combined_df.to_excel(writer, sheet_name='Financials', index=False)
else:
    print("No data found for any credit unions.")

print(combined_df)

""" credit_union_name = input("Enter the name of the credit union: ")
ein, name = get_credit_union_ein(credit_union_name)
if ein:
    print(f"Found credit union: {name} with EIN: {ein}")
    df = get_credit_union_data(ein)
    print(df)
else:
    print("Credit union not found.")
 """
