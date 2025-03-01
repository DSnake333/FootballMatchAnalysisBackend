import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Load and Preprocess Data
def load_defense_data():
    team_1_conn = sqlite3.connect("team_1_defense_stats.db")
    team_2_conn = sqlite3.connect("team_2_defense_stats.db")

    team_1_defense = pd.read_sql("SELECT * FROM defense_stats", team_1_conn)
    team_2_defense = pd.read_sql("SELECT * FROM defense_stats", team_2_conn)

    team_1_defense = team_1_defense.iloc[:-1]
    team_2_defense = team_2_defense.iloc[:-1]

    team_1_name = team_1_defense['Team'].iloc[0]
    team_2_name = team_2_defense['Team'].iloc[0]

    defense_df = pd.concat([team_1_defense, team_2_defense], ignore_index=True)


    numeric_columns = [
        'Tackles', 'Tackles Won', 'Defensive Third Tackles', 'Middle Third Tackles',
        'Attacking Third Tackles', 'Dribblers Tackled', 'Dribbles Challenged',
        '% of Dribblers Tackled', 'Challenges Lost', 'Blocks', 'Shots Blocked',
        'Passes Blocked', 'Interceptions', 'Tackles plus Interceptions', 'Clearances',
        'Errors', 'Min'
    ]
    defense_df[numeric_columns] = defense_df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Exclude total rows (if present)
    defense_df = defense_df[~defense_df['Player'].str.contains('Total', na=False)]

    # Derived Metrics
    defense_df['Dribbler Stop Rate (%)'] = (
        (defense_df['Dribblers Tackled'] / defense_df['Dribbles Challenged']) * 100
    ).fillna(0)

    defense_df['Defensive Impact Index'] = (
        0.4 * defense_df['Tackles Won'] +
        0.3 * defense_df['Interceptions'] +
        0.2 * defense_df['Blocks'] +
        0.1 * defense_df['Clearances']
    )

    defense_df['Defensive Pressure Success Rate (%)'] = (
        (defense_df['Tackles Won'] + defense_df['Dribblers Tackled'] + defense_df['Interceptions']) /
        (defense_df['Tackles'] + defense_df['Dribbles Challenged'] + defense_df['Interceptions'])
    ) * 100

    defense_df['Defensive Pressure Success Rate (%)'] = defense_df['Defensive Pressure Success Rate (%)'].fillna(0)

    return defense_df, team_1_name, team_2_name


# Visualization 1: Team-Level Tackling Efficiency
def visualize_tackling_efficiency(defense_df, team_1_name, team_2_name):
    team_stats = defense_df.groupby('Team').sum()
    tackling_efficiency = (team_stats['Tackles Won'] / team_stats['Tackles']) * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[team_1_name, team_2_name],
        y=tackling_efficiency,
        name="Tackling Efficiency (%)",
        marker_color=['rgb(102, 197, 204)', 'rgb(246, 78, 139)']
    ))

    fig.update_layout(
        title="Tackling Efficiency Comparison",
        xaxis_title="Team",
        yaxis_title="Efficiency (%)",
        barmode="group"
    )

    return fig.to_json()


# Visualization 2: Top Players by Tackles + Interceptions
def visualize_top_defenders(defense_df, team_1_name, team_2_name):
    top_defenders = defense_df.sort_values(by="Tackles plus Interceptions", ascending=False).head(10)
    fig = px.bar(
        top_defenders,
        x="Player",
        y="Tackles plus Interceptions",
        color="Team",
        title="Top Players by Tackles + Interceptions",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )
    fig.update_layout(xaxis_title="Player", yaxis_title="Tackles + Interceptions")

    return fig.to_json()


# Visualization 3: Dribbler Stop Rate
def visualize_dribbler_stop_rate(defense_df, team_1_name, team_2_name):
    top_dribbler_stoppers = defense_df.sort_values(by="Dribbler Stop Rate (%)", ascending=False).head(10)
    fig = px.bar(
        top_dribbler_stoppers,
        x="Player",
        y="Dribbler Stop Rate (%)",
        color="Team",
        title="Top Players by Dribbler Stop Rate",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig.update_layout(xaxis_title="Player", yaxis_title="Dribbler Stop Rate (%)")

    return fig.to_json()


# Visualization 4: Defensive Pressure Success Rate
def visualize_defensive_pressure(defense_df, team_1_name, team_2_name):
    top_defensive_pressure = defense_df.sort_values(by="Defensive Pressure Success Rate (%)", ascending=False).head(10)
    fig = px.bar(
        top_defensive_pressure,
        x="Player",
        y="Defensive Pressure Success Rate (%)",
        color="Team",
        title="Top Players by Defensive Pressure Success Rate",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig.update_layout(xaxis_title="Player", yaxis_title="Success Rate (%)")

    return fig.to_json()


# Visualization 5: Defensive Impact Index
def visualize_players_defensive_impact(defense_df, team_1_name, team_2_name):
    top_defensive_impact = defense_df.sort_values(by="Defensive Impact Index", ascending=False).head(10)
    fig = px.bar(
        top_defensive_impact,
        x="Player",
        y="Defensive Impact Index",
        color="Team",
        title="Top Players by Defensive Impact Index",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig.update_layout(xaxis_title="Player", yaxis_title="Defensive Impact Index")

    return fig.to_json()


# Main Function to Run Analysis
def main():
    defense_df, team_1_name, team_2_name = load_defense_data()

    # Generate Visualizations
    chart1 = visualize_tackling_efficiency(defense_df, team_1_name, team_2_name)
    chart2 = visualize_top_defenders(defense_df, team_1_name, team_2_name)
    chart3 = visualize_dribbler_stop_rate(defense_df, team_1_name, team_2_name)
    chart4 = visualize_defensive_pressure(defense_df, team_1_name, team_2_name)
    chart5 = visualize_players_defensive_impact(defense_df, team_1_name, team_2_name)

    return chart1, chart2, chart3, chart4, chart5


if __name__ == "__main__":
    charts = main()
