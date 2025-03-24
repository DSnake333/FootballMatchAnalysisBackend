import sys
import asyncio
import pandas as pd
import sqlite3
import re
from bs4 import BeautifulSoup
from pydoll.browser.edge import Edge
from pydoll.browser.options import Options
from pydoll.constants import By

# Check if URL is provided as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python team_1_player_stats.py <match_url>")
    sys.exit(1)

# Define the URL for the match
url = sys.argv[1]
print(f"Attempting to fetch data from: {url}")

# Validate URL format
if not url.startswith('https://fbref.com/'):
    print("Warning: URL doesn't appear to be from fbref.com. Results may be unexpected.")


# Function to fetch and parse the HTML page using PyDoll
async def fetch_fbref_data(url):
    browser = None
    try:
        # Set up Chrome options
        options = Options()
        options.add_argument('--headless=new')  # Ensure headless mode
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')  # Helps in headless mode
        options.add_argument('--window-size=1920,1080')  # Ensure full page renders
        options.add_argument('--disable-dev-shm-usage')  # Fix crashes in headless mode
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')

        # Initialize browser with options - not using context manager to handle closing more explicitly
        browser = Edge(options=options)
        await browser.start()
        print("Browser started successfully")

        # Get a page
        page = await browser.get_page()

        # First visit the homepage to establish cookies
        print("Visiting FBref homepage...")
        await asyncio.wait_for(page.go_to("https://fbref.com/en/"), timeout=30)
        print("Homepage loaded")

        # Wait a moment for cookies to be set
        await asyncio.sleep(2)

        # Then visit the actual match page
        print(f"Now visiting the match page: {url}")
        await asyncio.wait_for(page.go_to(url), timeout=60)
        print("Match page loaded")

        # Wait for content to fully load
        await asyncio.sleep(5)

        # Get the page content
        html_content = await asyncio.wait_for(page.page_source, timeout=30)

        # Save the HTML to a file for inspection
        with open('response.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        print("HTML content parsed successfully")

        return soup
    except asyncio.TimeoutError:
        print("Operation timed out. The page may be loading too slowly.")
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        # Make sure to properly close the browser in all cases
        if browser:
            try:
                print("Closing browser...")
                await asyncio.wait_for(browser.stop(), timeout=10)
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {e}")


def extract_team_ids(soup):
    try:
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
    except Exception as e:
        print(f"Error extracting team IDs: {e}")
        return None, None


def extract_team_name(soup, team_id):
    try:
        # Try multiple ways to find the team name
        # First attempt: Look for keeper stats section
        team_span = soup.find('span', {'class': 'section_anchor', 'id': f'keeper_stats_{team_id}_link'})
        if team_span and 'data-label' in team_span.attrs:
            team_name = team_span['data-label']
            # Remove 'Goalkeeper Stats' from the team name
            team_name = team_name.replace(" Goalkeeper Stats", "")
            return team_name

        # Second attempt: Look for summary stats section
        team_span = soup.find('span', {'class': 'section_anchor', 'id': f'stats_{team_id}_summary_link'})
        if team_span and 'data-label' in team_span.attrs:
            team_name = team_span['data-label']
            # Remove 'Summary' from the team name
            team_name = team_name.replace(" Summary", "")
            return team_name

        # Third attempt: Look for team headers
        team_header = soup.find('h2', string=lambda text: text and 'Stats' in text)
        if team_header:
            team_name = team_header.get_text().replace(" Stats", "").strip()
            return team_name

        print("Team name not found using multiple methods!")
        return "Unknown Team"
    except Exception as e:
        print(f"Error extracting team name: {e}")
        return "Unknown Team"


# Function to extract section data by div id and convert it to DataFrame
def extract_section_data(soup, div_id, columns):
    try:
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

        # Skip header rows (first 2)
        if len(rows) < 3:
            print(f"Not enough rows in table for section '{div_id}'")
            return None

        for row in rows[2:]:
            cells = row.find_all(['th', 'td'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if len(row_data) == len(columns):  # Ensure row has expected number of columns
                data.append(row_data)
            else:
                print(f"Row has {len(row_data)} columns, expected {len(columns)} in section '{div_id}'")

        if not data:
            print(f"No data extracted for section '{div_id}'")
            return None

        # Convert to DataFrame with the specified columns
        df_section = pd.DataFrame(data, columns=columns)
        return df_section
    except Exception as e:
        print(f"Error extracting section data for {div_id}: {e}")
        return None


# Function to store each DataFrame in a separate SQLite database
def store_dataframe_to_sql(df, team_name, db_name, table_name):
    try:
        df['Team'] = team_name
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print(f"Data stored in '{table_name}' table of '{db_name}' successfully.")
    except Exception as e:
        print(f"Error storing data to database: {e}")


# Define columns for each section and their respective div IDs
def define_sections(team_id):
    return {
        'summary': (f'div_stats_{team_id}_summary', [
            'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min',
            'Goals', 'Assists', 'Penalty Kicks Made', 'Penalty Kicks Attempted', 'Shots', 'Shots on Target',
            'Yellow Cards',
            'Red Cards', 'Touches', 'Tackles', 'Interceptions', 'Blocks', 'Expected Goals',
            'Non Penalty Expected Goals',
            'Expected Assisted Goals', 'Shot Creating Actions', 'Goal Creating Actions', 'Passes Completed',
            'Passes Attempted',
            'Pass Completion %', 'Progressive Passes', 'Carries', 'Progressive Carries', 'Take-Ons Attempted',
            'Successful Take-Ons',
        ]),
        # Other sections remain the same as before...
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
            'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min', 'Tackles', 'Tackles Won',
            'Defensive Third Tackles',
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
            'Progressive Carrying Distance', 'Progressive Carries', 'Carries into Final Third',
            'Carries into Penalty Area',
            'Miscontrols',
            'Dispossessed', 'Passes Received', 'Progressive Passes Received',
        ]),
        'misc': (f'div_stats_{team_id}_misc', [
            'Player', 'Squad Number', 'Nation', 'Pos', 'Age', 'Min', 'Yellow Cards', 'Red Cards', 'Second Yellow Card',
            'Fouls Committed', 'Fouls Drawn', 'Offsides', 'Crosses', 'Interceptions', 'Tackles Won',
            'Penalty Kicks Won',
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


# Process all sections and store data
async def process_and_store_data(team_id, team_name, soup):
    sections = define_sections(team_id)

    for section_name, (div_id, columns) in sections.items():
        print(f"Processing {section_name} section...")
        df = extract_section_data(soup, div_id, columns)

        if df is not None and not df.empty:
            # Add the 'Team' column to the DataFrame
            df['Team'] = team_name

            # Reorder the columns to move 'Team' to the second position
            cols = [df.columns[0]] + ['Team'] + [col for col in df.columns if col not in ['Team', df.columns[0]]]
            df = df[cols]

            # Define the database name and store the DataFrame
            db_name = f"team_1_{section_name}_stats.db"  # Unique database file for each section
            store_dataframe_to_sql(df, team_name, db_name, f"{section_name}_stats")
        else:
            print(f"Data for '{section_name}' section could not be extracted or is empty.")

        # Add a small delay to avoid overwhelming the CPU
        await asyncio.sleep(0.2)


# Main async function to run the entire process
async def main():
    # Fetch the webpage data
    soup = await fetch_fbref_data(url)
    if soup is None:
        print("Failed to fetch and parse the webpage. Exiting.")
        sys.exit(1)

    # Check if we got any content
    if soup.find('body') is None or len(soup.text.strip()) < 100:
        print("Retrieved HTML appears to be empty or incomplete. Exiting.")
        sys.exit(1)

    # Save the soup to a file for debugging
    with open('parsed_soup.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

    # Extract team IDs
    team_1_id, team_2_id = extract_team_ids(soup)

    # For team_1_player_stats.py, use team_1_id
    team_id = team_1_id

    if not team_id:
        print("Failed to extract team ID")
        sys.exit(1)

    print(f"Processing stats for team ID: {team_id}")

    # Extract team name
    team_name = extract_team_name(soup, team_id)
    print(f"Team name: {team_name}")

    # Process all sections and store data
    await process_and_store_data(team_id, team_name, soup)

    print("Data extraction and storage complete.")


# Run the async main function with a global timeout
if __name__ == "__main__":
    try:
        # Set a global timeout of 5 minutes for the entire operation
        asyncio.run(asyncio.wait_for(main(), timeout=300))
    except asyncio.TimeoutError:
        print("The operation timed out after 5 minutes.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
