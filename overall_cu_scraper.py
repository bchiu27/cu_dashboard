import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def financial_scraper(ein_list):
    """Scrapes financial data from ProPublica Nonprofits site for given EINs.
    Args:
        ein_list (list): List of EINs to scrape financial data for.
    Returns:
        pd.DataFrame: DataFrame containing financial data for each EIN.
    """
    results = []
    
    # Credit unions that aren't in API
    multi_year_eins = ["420804594", "350978599", "590729366"]  # Greenstate, Crane, and Achieva Credit Union
    
    for ein in ein_list:
        print(f"Processing EIN: {ein}")
        url = f"https://projects.propublica.org/nonprofits/organizations/{ein}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get org name
            h1_element = soup.find('h1')
            if h1_element:
                h1_text = h1_element.text.strip().lower()
    
                # Check if header contains generic terms
                if any(term in h1_text for term in ['chartered in', 'credit unions in']):
                    # Extract from the specific div class to get sub name
                    org_div = soup.find('div', class_='text-hed-900 org-sort-name')
                    if org_div:
                        org_name = org_div.text.strip()
                        fixed_name = re.sub(r'^\d+\s+', '', org_name).strip()
                        org_name = fixed_name
                    else:
                        org_name = f"Unknown ({ein})"
                else:
                    # Use h1 as normal
                    org_name = h1_element.text.strip()
            else:
                org_name = f"Unknown ({ein})"
            print(f"Found organization: {org_name}")
            
            # Determine which years to scrape
            if ein in multi_year_eins:
                years_to_scrape = list(range(2012, 2024)) 
                print(f"Multi-year scraping: {years_to_scrape[0]}-{years_to_scrape[-1]}")
            else:
                years_to_scrape = [2023]  # Just 2023
                print(f"Single year scraping: 2023")
            
            # Process each year
            for year in years_to_scrape:
                filing_section = soup.find('section', id=f'filing{year}')
                
                if filing_section:
                    financial_data = extract_financial_data(filing_section, ein, org_name, year)
                    if financial_data:
                        results.append(financial_data)
                    else:
                        results.append(empty_financial_record(ein, org_name, year))
                        print(f"{year}: Failed to extract financial data")
                else:
                    results.append(empty_financial_record(ein, org_name, year))
                    print(f"{year}: No filing section found")
                    
        except Exception as e:
            print(f"Error processing EIN {ein}: {e}")
            # Add empty records for the years this EIN should have covered
            if ein in multi_year_eins:
                for year in range(2012, 2024):
                    results.append(empty_financial_record(ein, f"Unknown ({ein})", year))
            else:
                results.append(empty_financial_record(ein, f"Unknown ({ein})", 2023))
                
        time.sleep(1)
        
    return pd.DataFrame(results)


def extract_financial_data(filing_section, ein, org_name, year):
    """Extract financial data from the filing section"""
    try:
        data = {
            "ein": ein,
            "name": org_name,
            "Year": year,
            "Total Assets": None,
            "Total Liabilities": None,
            "Total Revenue": None,
            "Total Expenses": None,
            "Net Income": None,
            "Investment Income": None,
        }
        
        # Extract Revenue, Expenses, and Net Income from summary section (extract-summary)
        summary_section = filing_section.find('div', class_='extract-summary')
        if summary_section:
            # Total Revenue
            revenue_elem = summary_section.find('div', class_='row-revenue__number')
            if revenue_elem:
                data['Total Revenue'] = parse_money(revenue_elem.text)
            
            # Expenses, Net Income from row-summary section
            summary_items = summary_section.find_all('div', class_='row-summary__item')
            for item in summary_items:
                header = item.find('div', class_='row-summary__hed')
                number = item.find('div', class_='row-summary__number')
                
                if header and number:
                    header_text = header.text.strip().lower()
                    if 'expenses' in header_text:
                        data['Total Expenses'] = parse_money(number.text)
                    elif 'net income' in header_text:
                        data['Net Income'] = parse_money(number.text)
        
        # Extract Investment Income from revenue table
        revenue_table = filing_section.find('table', class_='revenue')
        if revenue_table:
            rows = revenue_table.find('tbody').find_all('tr') if revenue_table.find('tbody') else []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    revenue_type = cells[0].text.strip().lower()
                    if 'investment income' in revenue_type:
                        data['Investment Income'] = parse_money(cells[1].text)
                        break
        
        # Extract Assets and Liabilities from assets-debt table
        assets_table = filing_section.find('table', class_='assets-debt')
        if assets_table:
            rows = assets_table.find('tbody').find_all('tr') if assets_table.find('tbody') else []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    asset_type = cells[0].text.strip().lower()
                    if 'total assets' in asset_type:
                        data['Total Assets'] = parse_money(cells[1].text)
                    elif 'total liabilities' in asset_type:
                        data['Total Liabilities'] = parse_money(cells[1].text)
        
        # Return data
        if any(data[key] is not None for key in ['Total Revenue', 'Total Expenses', 'Total Assets']):
            return data
        else:
            return None
            
    except Exception as e:
        print(f"Error extracting financial data for {year}: {e}")
        return None


def parse_money(text):
    """Convert money text to float"""
    if not text or text.strip() in ['$0', '0', '-', '', 'N/A']:
        return None
    
    # Handle negative values
    is_negative = '-' in text or '(' in text
    
    # Remove $, commas, parentheses, and other non-numeric characters except decimal points
    cleaned = re.sub(r'[$,\(\)\-\+\s]', '', text.strip())
    
    try:
        value = float(cleaned)
        return -value if is_negative else value
    except ValueError:
        return None


def empty_financial_record(ein, org_name, year):
    """Create empty record for missing financial data"""
    return {
        'ein': ein,
        'name': org_name,
        'Year': year,
        'Total Revenue': None,
        'Total Expenses': None,
        'Net Income': None,
        'Total Assets': None,
        'Total Liabilities': None,
        'Investment Income': None
    }


# Feed in credit union EIN list
ein_list = [
    "381686050",
    "580960142", 
    "420804594",  # Greenstate
    "416028665",
    "590729366",
    "630353833",
    "630207315",
    "350978599",  # Crane 
    "381350130",
    "111644012",
    "590687423",
    "580147128",
    "910659059",
    "381215360",
    "370643547",
    "586032554",
    "596194363",
    "366006909",
    "396072970",
    "910557925",
    "590690965"
]

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Run the scraper
df = financial_scraper(ein_list)
print("\nResults:")
df = df[df['Total Revenue'].notnull()]
print(df)

def add_ceo_sheet(dataframe, filename='credit_union_data.xlsx'):
    """Add CEO compensation data as a new sheet to credit union data file"""
    try:
        # Try to add to existing file using append mode
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            dataframe.to_excel(writer, sheet_name='Financial_remaining', index=False)
    except FileNotFoundError:
        # File doesn't exist, create new one
        dataframe.to_excel(filename, sheet_name='Financial_remaining', index=False)
    except Exception as e:
        print(f"Error: {e}")
        
add_ceo_sheet(df)
