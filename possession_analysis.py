import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Load Possession Data
def load_possession_data():
    team_1_conn = sqlite3.connect("team_1_possession_stats.db")
    team_2_conn = sqlite3.connect("team_2_possession_stats.db")

    team_1_possession = pd.read_sql("SELECT * FROM possession_stats", team_1_conn)
    team_2_possession = pd.read_sql("SELECT * FROM possession_stats", team_2_conn)

    possession_df = pd.concat([team_1_possession, team_2_possession], ignore_index=True)

    numeric_columns = [
        'Touches', 'Touches in Def Pen Area', 'Touches in Def Third', 'Touches in Middle Third',
        'Touches in Attacking Third', 'Touches in Attacking Penalty Area', 'Live-Ball Touches',
        'Take-Ons Attempted', 'Successful Take-Ons', 'Successful Take-On %', 'Times Tackled During Take-On',
        'Tackled During Take-on %', 'Carries', 'Total Carrying Distance', 'Progressive Carrying Distance',
        'Progressive Carries', 'Carries into Final Third', 'Carries into Penalty Area', 'Miscontrols',
        'Dispossessed', 'Passes Received', 'Progressive Passes Received'
    ]
    possession_df[numeric_columns] = possession_df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    return possession_df

# Step 2: Calculate Derived Metrics
def calculate_possession_metrics(possession_df):
    possession_df['Carrying Efficiency (%)'] = (
        possession_df['Progressive Carrying Distance'] / possession_df['Total Carrying Distance']
    ) * 100
    possession_df['Carrying Efficiency (%)'] = possession_df['Carrying Efficiency (%)'].fillna(0)

    possession_df['Take-On Success Rate (%)'] = (
        possession_df['Successful Take-Ons'] / possession_df['Take-Ons Attempted']
    ) * 100
    possession_df['Take-On Success Rate (%)'] = possession_df['Take-On Success Rate (%)'].fillna(0)

    possession_df['Progressive Pass Reception Rate (%)'] = (
        possession_df['Progressive Passes Received'] / possession_df['Passes Received']
    ) * 100
    possession_df['Progressive Pass Reception Rate (%)'] = possession_df['Progressive Pass Reception Rate (%)'].fillna(0)

    return possession_df

# Visualization 1: Carrying Efficiency and Take-On Success
def visualize_carry_take_on(possession_df):
    fig = px.bar(
        possession_df,
        x="Player",
        y=["Carrying Efficiency (%)", "Take-On Success Rate (%)"],
        barmode="group",
        color="Team",
        title="Carrying Efficiency and Take-On Success",
        labels={"value": "Percentage", "variable": "Metric"}
    )
    fig.update_layout(yaxis_title="Percentage", xaxis_title="Player")
    return fig.to_json()

# Visualization 2: Progressive Pass Reception Rate
def visualize_progressive_pass_reception(possession_df):
    fig = px.bar(
        possession_df,
        x="Player",
        y="Progressive Pass Reception Rate (%)",
        color="Team",
        title="Progressive Pass Reception Rate",
        text="Progressive Pass Reception Rate (%)"
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(yaxis_title="Percentage", xaxis_title="Player")
    return fig.to_json()

# Visualization 3: Touch Distribution
def visualize_touch_distribution(possession_df):
    team_metrics = possession_df.groupby('Team').sum()
    fig = go.Figure()
    for team, data in team_metrics.iterrows():
        fig.add_trace(go.Bar(
            x=['Defensive Third', 'Middle Third', 'Attacking Third'],
            y=[
                data['Touches in Def Third'] / data['Touches'] * 100,
                data['Touches in Middle Third'] / data['Touches'] * 100,
                data['Touches in Attacking Third'] / data['Touches'] * 100
            ],
            name=team
        ))

    fig.update_layout(
        title="Touch Distribution Across Thirds",
        xaxis_title="Field Third",
        yaxis_title="Percentage (%)",
        barmode="group"
    )
    return fig.to_json()

# Visualization 4: Miscontrols and Dispossessions
def visualize_miscontrols_dispossessions(possession_df):
    fig = px.bar(
        possession_df,
        x="Player",
        y=["Miscontrols", "Dispossessed"],
        barmode="group",
        color="Team",
        title="Miscontrols and Dispossessions",
        labels={"value": "Count", "variable": "Metric"}
    )
    fig.update_layout(yaxis_title="Count", xaxis_title="Player")
    return fig.to_json()

# Main Functionality
def main():
    possession_df = load_possession_data()
    possession_df = calculate_possession_metrics(possession_df)

    charts = {
        "carrying_and_take_on": visualize_carry_take_on(possession_df),
        "progressive_pass_reception": visualize_progressive_pass_reception(possession_df),
        "touch_distribution": visualize_touch_distribution(possession_df),
        "miscontrols_dispossessions": visualize_miscontrols_dispossessions(possession_df),
    }

    return charts

if __name__ == "__main__":
    charts = main()
    for chart_name, chart_data in charts.items():
        print(f"{chart_name}: {chart_data}\n")
