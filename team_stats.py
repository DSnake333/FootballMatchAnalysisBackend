import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import sys

# Function to fetch and parse the HTML page
def fetch_fbref_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print("Failed to retrieve data")
        return None

# Function to extract section data by div id and convert it to DataFrame
def extract_section_data(soup, div_id, columns):
    section = soup.find('div', id=div_id)
    if not section:
        print(f"Section '{div_id}' not found")
        return None

    table = section.find('table')
    if not table:
        print(f"No table found in section '{div_id}'")
        return None

    data = []
    rows = table.find_all('tr')

    for row in rows:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        if row_data:  # Skip empty rows
            data.append(row_data)

    # Ensure the DataFrame has the same number of columns as expected
    if data and len(data[0]) == len(columns):
        df_section = pd.DataFrame(data, columns=columns)
        return df_section
    else:
        print(f"Data in section '{div_id}' does not match expected columns")
        return None

# Function to store DataFrame in SQLite database
def store_dataframe_to_sql(df, db_name, table_name):
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Data stored in '{table_name}' table of '{db_name}' successfully.")

# Main function to scrape and store data
def main(url):
    soup = fetch_fbref_data(url)
    if not soup:
        print("Failed to fetch data from the provided URL")
        return

    # Define the columns for each section
    stats_columns = ['Team_1', 'Team_2']
    stats_extra_columns = ['Team_1_Fouls', 'Team_2_Fouls']

    # Extract stats and additional data
    shots_df = extract_section_data(soup, 'team_stats', stats_columns)
    extra_stats_df = extract_section_data(soup, 'team_stats_extra', stats_extra_columns)

    # Log the extracted data
    print(f"Shots DataFrame:\n{shots_df}")
    print(f"Extra Stats DataFrame:\n{extra_stats_df}")

    # Store the DataFrames individually if combined DataFrame is not possible
    if shots_df is not None:
        store_dataframe_to_sql(shots_df, "team_stats.db", "shots_data")
    if extra_stats_df is not None:
        store_dataframe_to_sql(extra_stats_df, "team_stats.db", "extra_stats_data")

# Entry point for the script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python team_stats.py <match_url>")
        sys.exit(1)

    match_url = sys.argv[1]
    main(match_url)