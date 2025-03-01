import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re

# Check if URL is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python team_2_player_stats.py <match_url>")
    sys.exit(1)

# Define the URL for the match
url = sys.argv[1]

# Function to fetch and parse the HTML page
def fetch_fbref_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print("Failed to retrieve data")
        return None


def extract_team_ids(soup):
    # Find all divs that contain team stats
    stats_divs = soup.find_all('div', id=re.compile(r'div_stats_.*_summary'))
    team_ids = []

    for div in stats_divs:
        # Extract team ID from the div id attribute
        div_id = div.get('id', '')
        match = re.search(r'div_stats_([a-f0-9]+)_summary', div_id)
        if match:
            team_ids.append(match.group(1))

    if len(team_ids) >= 2:
        return team_ids[0], team_ids[1]  # Return both team IDs
    else:
        print("Could not find team IDs")
        return None, None


soup = fetch_fbref_data(url)
team_1_id, team_2_id = extract_team_ids(soup)

team_id = team_2_id

if not team_id:
    print("Failed to extract team ID")
    sys.exit(1)

print(f"Processing stats for team ID: {team_id}")

def extract_team_name(soup):
    team_span = soup.find('span', {'class': 'section_anchor', 'id': f'keeper_stats_{team_id}_link'})
    if team_span and 'data-label' in team_span.attrs:
        team_name = team_span['data-label']
        # Remove 'Goalkeeper Stats' from the team name
        team_name = team_name.replace(" Goalkeeper Stats", "")
        return team_name
    else:
        print("Team name not found!")
        return None

# Extract team name (e.g., Real Madrid or Barcelona)
team_name = extract_team_name(soup)
print(f"Extracted Team Name: {team_name}")

# Function to extract section data by div id and convert it to DataFrame
def extract_section_data(soup, div_id, columns):
    section = soup.find('div', id=div_id)
    if not section:
        print(f"Data for section '{div_id}' not found")
        return None

    # Look for table directly within the div, if available
    table = section.find('table')
    if not table:
        print(f"No table found in section '{div_id}'")
        return None

    # Extract headers and rows
    data = []
    rows = table.find_all('tr')

    for row in rows[2:]:
        cells = row.find_all(['th', 'td'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        if len(row_data) == len(columns):  # Ensure row has expected number of columns
            data.append(row_data)

    # Convert to DataFrame with the specified columns
    df_section = pd.DataFrame(data, columns=columns)
    return df_section

# Function to store each DataFrame in a separate SQLite database
def store_dataframe_to_sql(df, team_name, db_name, table_name):
    df['Team'] = team_name
    conn = sqlite3.connect(db_name)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Data stored in '{table_name}' table of '{db_name}' successfully.")

# Define columns for each section and their respective div IDs
sections = {
    'summary': (f'div_stats_{team_id}_summary', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min',
        'Goals', 'Assists', 'Penalty Kicks Made', 'Penalty Kicks Attempted', 'Shots', 'Shots on Target', 'Yellow Cards',
        'Red Cards', 'Touches', 'Tackles', 'Interceptions', 'Blocks', 'Expected Goals', 'Non Penalty Expected Goals',
        'Expected Assisted Goals', 'Shot Creating Actions', 'Goal Creating Actions', 'Passes Completed',
        'Passes Attempted',
        'Pass Completion %', 'Progressive Passes', 'Carries', 'Progressive Carries', 'Take-Ons Attempted',
        'Successful Take-Ons',
    ]),
    'passing': (f'div_stats_{team_id}_passing', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min',
        'Passes Completed', 'Passes Attempted', 'Pass Completion %', 'Total Passing Distance',
        'Progressive Passing Distance', 'Short Passes Completed', 'Short Passes Attempted',
        'Short Pass Completion', 'Medium Passes Completed', 'Medium Passes Attempted',
        'Medium Pass Completion', 'Long Passes Completed', 'Long Passes Attempted',
        'Long Pass Completion', 'Assists', 'Expected Assisted Goals', 'Expected Assists', 'Key Passes',
        'Passes into final third', 'Passes into Penalty Area', 'Crosses into Penalty Area',
        'Progressive Passes',
    ]),
    'pass_type': (f'div_stats_{team_id}_passing_types', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min',
        'Passes Attempted', 'Live Ball Passes', 'Dead Ball Passes', 'Passes from Free Kicks', 'Through Balls',
        'Switches', 'Crosses',
        'Throw-ins Taken', 'Corner Kicks', 'Inswinging Corner Kicks', 'Outswinging Corner Kicks',
        'Straight Corner Kicks', 'Passes Completed', 'Passes Offside',
        'Passes Blocked',
    ]),
    'defense': (f'div_stats_{team_id}_defense', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min', 'Tackles', 'Tackles Won', 'Defensive Third Tackles',
        'Middle Third Tackles', 'Attacking Third Tackles', 'Dribblers Tackled', 'Dribbles Challenged',
        '% of Dribblers Tackled', 'Challenges Lost', 'Blocks', 'Shots Blocked', 'Passes Blocked', 'Interceptions',
        'Tackles plus Interceptions', 'Clearances', 'Errors'
    ]),
    'possession': (f'div_stats_{team_id}_possession', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min',
        'Touches', 'Touches in Def Pen Area', 'Touches in Def Third', 'Touches in Middle Third',
        'Touches in Attacking Third', 'Touches in Attacking Penalty Area', 'Live-Ball Touches',
        'Take-Ons Attempted', 'Successful Take-Ons', 'Successful Take-On %', 'Times Tackled During Take-On',
        'Tackled During Take-on %', 'Carries', 'Total Carrying Distance',
        'Progressive Carrying Distance', 'Progressive Carries', 'Carries into Final Third', 'Carries into Penalty Area',
        'Miscontrols',
        'Dispossessed', 'Passes Received', 'Progressive Passes Received',
    ]),
    'misc': (f'div_stats_{team_id}_misc', [
        'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min', 'Yellow Cards', 'Red Cards', 'Second Yellow Card',
        'Fouls Committed', 'Fouls Drawn', 'Offsides', 'Crosses', 'Interceptions', 'Tackles Won', 'Penalty Kicks Won',
        'Penalty Kicks Conceded', 'Own Goals', 'Ball Recoveries', 'Aerials Won', 'Aerials Lost', '% of Aerials Won',
    ]),
    'keeper': (f'div_keeper_stats_{team_id}', [
        'Player', 'Nation', 'Age', 'Min', 'Shots on Target Against', 'Goals Against', 'Saves', 'Save %',
        'Post Shot Expected Goals', 'Passes Completed', 'Passes Attempted', 'Pass Completion %',
        'Passes Attempted (GK)', 'Throws Attempted', 'Launch %',
        'Average Pass Length', 'Goal Kicks Attempted', '% of Goal Kicks Launched', 'Average Goal Kick Length',
        'Crosses Faced', 'Crosses Stopped', 'Crosses Stopped %',
        'Def Actions outside Pen Area', 'Average Distance of Def Actions',
    ]),
    'shots': (f'div_shots_{team_id}', [
        'Minute', 'Player', 'Squad', 'xG', 'PSxG', 'Outcome', 'Distance',
        'Body Part', 'Notes', 'SCA1_Player', 'SCA1_Event', 'SCA2_Player', 'SCA2_Event',
    ]),

}

# Extract and store each section in a separate database
for section_name, (div_id, columns) in sections.items():
    df = extract_section_data(soup, div_id, columns)
    if df is not None:
        # Add the 'Team' column to the DataFrame
        df['Team'] = team_name

        # Reorder the columns to move 'Team' to the second position
        cols = [df.columns[0]] + ['Team'] + [col for col in df.columns if col not in ['Team', df.columns[0]]]
        df = df[cols]

        # Define the database name and store the DataFrame
        db_name = f"team_2_{section_name}_stats.db"  # Unique database file for each section
        store_dataframe_to_sql(df, team_name, db_name, f"{section_name}_stats")
    else:
        print(f"Data for '{section_name}' section could not be extracted.")