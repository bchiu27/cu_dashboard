import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def overall_scraper(ein_list):
    """Scrapes all data from ProPublica Nonprofits site for given EINs.
    Args:
        ein_list (list): List of EINs to scrape data for.
    Returns:
        pd.DataFrame: DataFrame containing CEO compensation data for each EIN and year.
    """
    results = []
    
    for ein in ein_list:
        print(f"Processing EIN: {ein}")
        url = f"https://projects.propublica.org/nonprofits/organizations/{ein}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get org name
            org_name = soup.find('h1').text.strip() if soup.find('h1') else f"Unknown ({ein})"
            print(f"Found organization: {org_name}")
            
            # Find all filing sections available (like filing2022, filing2023, etc.)
            filing_sections = soup.find_all('section', class_='single-filing-period')
            print(f"Found {len(filing_sections)} filing sections")
            
            for section in filing_sections:
                # Extract year from the section id (like "filing2022")
                section_id = section.get('id', '')
                year_match = re.search(r'filing(\d{4})', section_id)
                
                if year_match:
                    year = int(year_match.group(1))
                    
                    if 2013 <= year <= 2023:
                        # Find the employees table in this section
                        employees_table = section.find('table', class_='revenue')
                        
                        if employees_table:
                            # Find ALL employee-row shortlist rows
                            ceo_rows = employees_table.find_all('tr', class_='employee-row shortlist')
                            
                            if ceo_rows:
                                ceo_data = None
                                
                                # Check first row
                                if len(ceo_rows) >= 1:
                                    ceo_data = extract_ceo_from_row(ceo_rows[0], ein, org_name, year)
                                    if ceo_data:
                                        print(f"{year}: Found CEO in row 1 - {ceo_data['ceo_name']} - ${ceo_data['total']:,}")
                                
                                # If no CEO found in first row, check second row
                                if not ceo_data and len(ceo_rows) >= 2:
                                    ceo_data = extract_ceo_from_row(ceo_rows[1], ein, org_name, year)
                                    if ceo_data:
                                        print(f"  ✓ {year}: Found CEO in row 2 - {ceo_data['ceo_name']} - ${ceo_data['total']:,}")
                                
                                # Add the result (either CEO data or empty record)
                                if ceo_data:
                                    results.append(ceo_data)
                                else:
                                    results.append(empty_record(ein, org_name, year))
                                    print(f"{year}: No CEO found in first 2 rows")
                            else:
                                results.append(empty_record(ein, org_name, year))
                                print(f"{year}: No employee-row shortlist found")
                        else:
                            results.append(empty_record(ein, org_name, year))
                            print(f"{year}: No employees table found")
            
            # Add empty records for missing years
            found_years = {r['year'] for r in results if r['ein'] == ein}
            for year in range(2013, 2024):
                if year not in found_years:
                    results.append(empty_record(ein, org_name, year))
                    print(f"{year}: No filing section found")
                    
        except Exception as e:
            print(f"Error processing EIN {ein}: {e}")
            for year in range(2013, 2024):
                results.append(empty_record(ein, f"Unknown ({ein})", year))
                
        time.sleep(1)
        
    return pd.DataFrame(results)

def extract_financial_data(row, ein, org_name, year):
    """Extract CEO data from the first employee-row shortlist"""
    cells = row.find_all('td')
    
    if len(cells) >= 4:
        # First cell contains name and title
        name_cell = cells[0].text.strip()
        
        # Check if the name contains CEO or President
        if not any(title in name_cell.lower() for title in ['ceo', 'president', 'chief executive officer']):
            return None
        # Extract compensation from numeric cells (based on your screenshot structure)
        compensation = parse_money(cells[1].text)  # direct compensation
        other = parse_money(cells[3].text)         # other section
        
        total = (compensation or 0) + (other or 0)
        
        # Extract name (remove title in parentheses if present)
        name = re.sub(r'\s*\([^)]*\)', '', name_cell).strip()
        name = re.sub(r'\([^)]*\)', '', name_cell).strip()
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'[^\w\s.-]+$', '', name)
        
        return {
            'name': org_name,
            'ein': ein,
            'year': year,
            'ceo_name': name,
            'compensation': compensation,
            'other': other,
            'total': total if total > 0 else None
        }
    
    return None

def parse_money(text):
    """Convert money text to number"""
    if not text or text.strip() in ['$0', '0', '-', '']:
        return None
    
    # Remove $ and commas
    cleaned = re.sub(r'[$,]', '', text.strip())
    try:
        return float(cleaned)
    except:
        return None

def empty_financial_record(ein, org_name, year):
    """Create empty record for missing financial data"""
    return {
        'ein': ein,
        'organization': org_name,
        'year': year,
        'total_expenses': None,
        'investment_income': None,
        'executive_compensation': None,
        'total_assets': None,
        'total_liabilities': None
    }

# Test with your EIN
ein_list = [
    "381686050",
    "580960142",
    "420804594",
    "416028665",
    "590729366",
    "630353833",
    "630207315",
    "350978599",
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
df = overall_scraper(ein_list)
print("\nResults:")
print(df)
