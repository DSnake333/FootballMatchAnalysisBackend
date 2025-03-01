import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Load and Preprocess Data
def load_shots_data():
    team_1_conn = sqlite3.connect("team_1_shots_stats.db")
    team_2_conn = sqlite3.connect("team_2_shots_stats.db")

    team_1_shots = pd.read_sql("SELECT * FROM shots_stats", team_1_conn)
    team_2_shots = pd.read_sql("SELECT * FROM shots_stats", team_2_conn)

    team_1_shots = team_1_shots.iloc[:-1]  # Exclude total rows
    team_2_shots = team_2_shots.iloc[:-1]

    team_1_name = team_1_shots['Team'].iloc[0]
    team_2_name = team_2_shots['Team'].iloc[0]

    all_shots = pd.concat([team_1_shots.assign(Team=team_1_name), team_2_shots.assign(Team=team_2_name)], ignore_index=True)

    # Data cleaning and processing
    numeric_columns = ['xG', 'PSxG', 'Distance']
    all_shots[numeric_columns] = all_shots[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Calculate metrics for both teams
    team_1_metrics = calculate_shots_metrics(all_shots[all_shots['Team'] == team_1_name])
    team_2_metrics = calculate_shots_metrics(all_shots[all_shots['Team'] == team_2_name])

    return all_shots, team_1_name, team_2_name, team_1_metrics, team_2_metrics



# Step 2: Derive Key Metrics
def calculate_shots_metrics(shots_df):
    total_shots = len(shots_df)
    total_goals = shots_df[shots_df['Outcome'] == 'Goal'].shape[0]
    total_xg = shots_df['xG'].sum()
    total_psxg = shots_df['PSxG'].sum()
    avg_shot_distance = shots_df['Distance'].mean()
    goal_conversion_rate = (total_goals / total_shots) * 100 if total_shots > 0 else 0
    conversion_efficiency = (total_goals / total_xg) * 100 if total_xg > 0 else 0
    xg_performance = total_goals - total_xg
    psxg_performance = total_goals - total_psxg

    return {
        'Total Shots': total_shots,
        'Total Goals': total_goals,
        'Total xG': total_xg,
        'Total PSxG': total_psxg,
        'Average Shot Distance': avg_shot_distance,
        'Conversion Efficiency (%)': conversion_efficiency,
        'Goal Conversion Rate (%)': goal_conversion_rate,
        'xG Performance': xg_performance,
        'PSxG Performance': psxg_performance
    }


# Visualization 1: Shot Outcomes Distribution
def visualize_shot_outcomes(all_shots, team_1_name, team_2_name):
    fig = go.Figure()
    for team, shots_df, color in zip(
            [team_1_name, team_2_name],
            [all_shots[all_shots['Team'] == team_1_name], all_shots[all_shots['Team'] == team_2_name]],
            ['rgb(102, 197, 204)', 'rgb(246, 78, 139)']
    ):
        outcomes = shots_df['Outcome'].value_counts()
        fig.add_trace(go.Bar(
            x=outcomes.index,
            y=outcomes.values,
            name=team,
            marker_color=color
        ))

    fig.update_layout(
        title=f"Shot Outcomes Distribution: {team_1_name} vs {team_2_name}",
        xaxis_title="Outcome",
        yaxis_title="Count",
        barmode='group'
    )

    return fig.to_json()


# Visualization 2: xG Heatmap by Minute
def visualize_xg_heatmap(all_shots, team_1_name, team_2_name):
    fig = px.density_heatmap(
        all_shots, x='Minute', y='xG', facet_col='Team',
        title="xG Distribution Over Match Minutes",
        color_continuous_scale='Viridis'
    )
    fig.update_layout(xaxis_title="Minute", yaxis_title="xG Value")
    return fig.to_json()


# Visualization 3: Shot Distance Analysis
def visualize_shot_distance_analysis(all_shots, team_1_name, team_2_name):
    # Clean the 'xG' column in the DataFrame to remove or replace NaN values
    all_shots['xG'] = all_shots['xG'].fillna(0.01)  # You can replace NaN with a small value or 0

    # Plot the scatter plot with cleaned data
    fig = px.scatter(
        all_shots,
        x='Distance', y='xG',
        color='Team',
        size='xG',  # 'xG' has no NaN values here
        hover_data=['Player', 'Minute', 'Outcome'],
        title=f"Shot Distance vs xG: {team_1_name} vs {team_2_name}",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(
        xaxis_title="Shot Distance (yards)", yaxis_title="xG Value"
    )

    return fig.to_json()


# Visualization 4: Shooting Efficiency and Impact
def visualize_shooting_efficiency(all_shots, team_1_name, team_2_name, team_1_metrics, team_2_metrics):
    efficiency_df = pd.DataFrame([team_1_metrics, team_2_metrics], index=[team_1_name, team_2_name]).reset_index()
    fig = px.bar(
        efficiency_df.melt(id_vars='index', value_vars=['Total Goals', 'Total xG', 'xG Performance', 'PSxG Performance']),
        x='index', y='value', color='variable',
        title=f"Shooting Efficiency and Impact: {team_1_name} vs {team_2_name}",
        labels={'index': 'Team', 'value': 'Metric Value', 'variable': 'Metric'}
    )
    return fig.to_json()


# Visualization 5: Top Players by Shot Creation Actions (SCA) Revisited
def visualize_top_players_sca(all_shots, team_1_name, team_2_name):
    # Concatenate the data for both teams, making sure the 'Team' column is included for both
    sca_data = pd.concat([
        all_shots[['SCA1_Player', 'SCA1_Event']].rename(
            columns={'SCA1_Player': 'Player', 'SCA1_Event': 'Event'}).assign(Team=team_1_name),
        all_shots[['SCA1_Player', 'SCA1_Event']].rename(
            columns={'SCA1_Player': 'Player', 'SCA1_Event': 'Event'}).assign(Team=team_2_name)
    ])

    # Filter out rows where the 'Player' column is empty or NaN
    sca_data = sca_data[sca_data['Player'].notna() & (sca_data['Player'] != '')]

    # Count the number of SCAs for each player
    top_sca_players = sca_data['Player'].value_counts().head(10).reset_index()
    top_sca_players.columns = ['Player', 'SCA Count']

    # Now 'Team' column is part of the data, and it can be used for coloring
    fig = px.bar(
        top_sca_players, x='Player', y='SCA Count', color='Player',  # Use 'Player' for color
        title="Top Players by Shot Creation Actions (SCA)",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    # Remove the text from the bars by not including 'text' in the call
    fig.update_traces(texttemplate='', textposition='outside')
    fig.update_layout(
        xaxis_title="Player",
        yaxis_title="SCA Count",
        showlegend=True
    )

    return fig.to_json()



# Main Function to Run Analysis
def main():
    all_shots, team_1_name, team_2_name = load_shots_data()
    team_1_metrics = calculate_shots_metrics(all_shots[all_shots['Team'] == team_1_name])
    team_2_metrics = calculate_shots_metrics(all_shots[all_shots['Team'] == team_2_name])

    # Generate Visualizations
    chart1 = visualize_shot_outcomes(all_shots, team_1_name, team_2_name)
    chart2 = visualize_xg_heatmap(all_shots, team_1_name, team_2_name)
    chart3 = visualize_shot_distance_analysis(all_shots, team_1_name, team_2_name)
    chart4 = visualize_shooting_efficiency(all_shots, team_1_name, team_2_name, team_1_metrics, team_2_metrics)
    chart5 = visualize_top_players_sca(all_shots, team_1_name, team_2_name)

    return chart1, chart2, chart3, chart4, chart5


if __name__ == "__main__":
    charts = main()
