import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Step 1: Load and Preprocess Data
def load_passing_data():
    team_1_conn = sqlite3.connect("team_1_passing_stats.db")
    team_2_conn = sqlite3.connect("team_2_passing_stats.db")

    team_1_passing = pd.read_sql("SELECT * FROM passing_stats", team_1_conn)
    team_2_passing = pd.read_sql("SELECT * FROM passing_stats", team_2_conn)

    team_1_pass_type_conn = sqlite3.connect("team_1_pass_type_stats.db")
    team_2_pass_type_conn = sqlite3.connect("team_2_pass_type_stats.db")

    team_1_pass_type = pd.read_sql("SELECT * FROM pass_type_stats", team_1_pass_type_conn)
    team_2_pass_type = pd.read_sql("SELECT * FROM pass_type_stats", team_2_pass_type_conn)

    team_1_passing = team_1_passing.iloc[:-1]
    team_2_passing = team_2_passing.iloc[:-1]

    team_1_passing = pd.merge(team_1_passing, team_1_pass_type, on="Player", suffixes=("", "_type"))
    team_2_passing = pd.merge(team_2_passing, team_2_pass_type, on="Player", suffixes=("", "_type"))

    team_1_name = team_1_passing['Team'].iloc[0]
    team_2_name = team_2_passing['Team'].iloc[0]

    passing_df = pd.concat([team_1_passing, team_2_passing], ignore_index=True)

    numeric_columns = [
        'Passes Completed', 'Passes Attempted', 'Total Passing Distance', 'Progressive Passing Distance',
        'Short Passes Attempted', 'Medium Passes Attempted', 'Long Passes Attempted', 'Key Passes', 'Assists',
        'Passes into final third', 'Passes into Penalty Area', 'Crosses into Penalty Area',
        'Live Ball Passes', 'Dead Ball Passes', 'Through Balls', 'Switches', 'Corner Kicks',
        'Inswinging Corner Kicks', 'Outswinging Corner Kicks', 'Straight Corner Kicks'
    ]

    passing_df[numeric_columns] = passing_df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    passing_df['Pass Accuracy (%)'] = (passing_df['Passes Completed'] / passing_df['Passes Attempted']) * 100
    passing_df['Penetrative Passes'] = (
            passing_df['Passes into final third'] + passing_df['Passes into Penalty Area'] + passing_df[
        'Crosses into Penalty Area']
    )

    return passing_df, team_1_name, team_2_name


# Visualization 1: Team-Level Metrics
def visualize_team_passing_metrics(passing_df, team_1_name, team_2_name):
    team_stats = passing_df.groupby('Team').sum()
    team_accuracy = (team_stats['Passes Completed'] / team_stats['Passes Attempted']) * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[team_1_name, team_2_name],
        y=team_stats['Passes Attempted'],
        name="Passes Attempted",
        marker_color=['rgb(102, 197, 204)', 'rgb(246, 78, 139)']
    ))
    fig.add_trace(go.Bar(
        x=[team_1_name, team_2_name],
        y=team_stats['Passes Completed'],
        name="Passes Completed",
        marker_color=['rgb(33, 158, 188)', 'rgb(255, 127, 80)']
    ))
    fig.add_trace(go.Scatter(
        x=[team_1_name, team_2_name],
        y=team_accuracy,
        name="Pass Accuracy (%)",
        mode='lines+markers+text',
        text=team_accuracy.round(2).astype(str) + "%",
        marker=dict(size=12, color='rgb(70, 130, 180)')
    ))

    fig.update_layout(
        title="Team-Level Passing Metrics",
        xaxis_title="Team",
        yaxis_title="Metrics",
        barmode="group"
    )

    return fig.to_json()


# Visualization 2: Pass Type Distribution
def visualize_pass_type_distribution(passing_df, team_1_name, team_2_name):
    pass_type_stats = passing_df.groupby('Team').sum()
    pass_type_ratios = {
        'Short Passes (%)': pass_type_stats['Short Passes Attempted'] / pass_type_stats['Passes Attempted'] * 100,
        'Medium Passes (%)': pass_type_stats['Medium Passes Attempted'] / pass_type_stats['Passes Attempted'] * 100,
        'Long Passes (%)': pass_type_stats['Long Passes Attempted'] / pass_type_stats['Passes Attempted'] * 100
    }

    fig = go.Figure()
    for pass_type, values in pass_type_ratios.items():
        fig.add_trace(go.Bar(
            x=[team_1_name, team_2_name],
            y=values,
            name=pass_type,
            text=values.round(2).astype(str) + "%",
            textposition="auto"
        ))

    fig.update_layout(
        title="Pass Type Distribution",
        xaxis_title="Team",
        yaxis_title="Percentage (%)",
        barmode="stack"
    )

    return fig.to_json()


# Visualization 3: Top Players by Passing Accuracy
def visualize_top_passing_accuracy(passing_df, team_1_name, team_2_name):
    filtered_df = passing_df[passing_df['Passes Attempted'] >= 20]
    top_players = filtered_df.sort_values(by="Pass Accuracy (%)", ascending=False).head(10)

    fig = px.bar(
        top_players,
        x="Player",
        y="Pass Accuracy (%)",
        color="Team",
        title="Top Players by Passing Accuracy",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(xaxis_title="Player", yaxis_title="Pass Accuracy (%)")

    return fig.to_json()


# Visualization 4: Progressive Passing Leaders
def visualize_progressive_passers(passing_df, team_1_name, team_2_name):
    top_progressive_passers = passing_df.sort_values(by="Progressive Passing Distance", ascending=False).head(10)

    fig = px.bar(
        top_progressive_passers,
        x="Player",
        y="Progressive Passing Distance",
        color="Team",
        title="Progressive Passing Leaders",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(xaxis_title="Player", yaxis_title="Distance (m)")

    return fig.to_json()


# Visualization 5: Key Pass Contributors
def visualize_key_pass_contributors(passing_df, team_1_name, team_2_name):
    top_key_passers = passing_df.sort_values(by="Key Passes", ascending=False).head(10)

    fig = px.bar(
        top_key_passers,
        x="Player",
        y="Key Passes",
        color="Team",
        title="Key Pass Contributors",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(xaxis_title="Player", yaxis_title="Key Passes")

    return fig.to_json()


# Visualization 6: Penetrative Passing Leaders
def visualize_penetrative_passers(passing_df, team_1_name, team_2_name):
    top_penetrative_passers = passing_df.sort_values(by="Penetrative Passes", ascending=False).head(10)

    fig = px.bar(
        top_penetrative_passers,
        x="Player",
        y="Penetrative Passes",
        color="Team",
        title="Penetrative Passing Leaders",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(xaxis_title="Player", yaxis_title="Penetrative Passes")

    return fig.to_json()


# Visualization 7: Long-Pass Specialists
def visualize_long_pass_specialists(passing_df, team_1_name, team_2_name):
    passing_df['Long Passes Completed'] = pd.to_numeric(passing_df['Long Passes Completed'], errors='coerce')
    passing_df['Long Passes Attempted'] = pd.to_numeric(passing_df['Long Passes Attempted'], errors='coerce')
    passing_df['Long Pass Accuracy (%)'] = (passing_df['Long Passes Completed'] / passing_df['Long Passes Attempted']) * 100
    passing_df['Long Pass Accuracy (%)'] = passing_df['Long Pass Accuracy (%)'].fillna(0)
    top_long_passers = passing_df.sort_values(by="Long Pass Accuracy (%)", ascending=False).head(10)

    fig = px.bar(
        top_long_passers,
        x="Player",
        y="Long Pass Accuracy (%)",
        color="Team",
        title="Long-Pass Specialists",
        barmode="group",
        color_discrete_map={team_1_name: 'rgb(102, 197, 204)', team_2_name: 'rgb(246, 78, 139)'}
    )

    fig.update_layout(xaxis_title="Player", yaxis_title="Accuracy (%)")

    return fig.to_json()


# Visualization 8: Advanced Pass Metrics
def visualize_advanced_pass_metrics(passing_df, team_1_name, team_2_name):
    team_stats = passing_df.groupby('Team').sum()
    advanced_metrics = {
        'Live Ball Pass Ratio (%)': team_stats['Live Ball Passes'] / team_stats['Passes Attempted'] * 100,
        'Dead Ball Pass Ratio (%)': team_stats['Dead Ball Passes'] / team_stats['Passes Attempted'] * 100
    }

    fig = go.Figure()
    for metric, values in advanced_metrics.items():
        fig.add_trace(go.Bar(
            x=[team_1_name, team_2_name],
            y=values,
            name=metric,
            text=values.round(2).astype(str) + "%",
            textposition="auto"
        ))

    fig.update_layout(
        title="Advanced Passing Metrics",
        xaxis_title="Team",
        yaxis_title="Percentage (%)",
        barmode="group"
    )

    return fig.to_json()


# Visualization 9: Corner Kick Analysis
def visualize_corner_kicks(passing_df, team_1_name, team_2_name):
    team_stats = passing_df.groupby('Team').sum()
    corner_ratios = {
        'Inswing Corners (%)': team_stats['Inswinging Corner Kicks'] / team_stats['Corner Kicks'] * 100,
        'Outswing Corners (%)': team_stats['Outswinging Corner Kicks'] / team_stats['Corner Kicks'] * 100,
        'Straight Corners (%)': team_stats['Straight Corner Kicks'] / team_stats['Corner Kicks'] * 100
    }

    fig = go.Figure()
    for corner_type, values in corner_ratios.items():
        fig.add_trace(go.Bar(
            x=[team_1_name, team_2_name],
            y=values,
            name=corner_type,
            text=values.round(2).astype(str) + "%",
            textposition="auto"
        ))

    fig.update_layout(
        title="Corner Kick Analysis",
        xaxis_title="Team",
        yaxis_title="Percentage (%)",
        barmode="stack"
    )

    return fig.to_json()


# Main Function to Run Analysis
def main():
    passing_df, team_1_name, team_2_name = load_passing_data()

    # Generate Visualizations
    chart1 = visualize_team_passing_metrics(passing_df, team_1_name, team_2_name)
    chart2 = visualize_pass_type_distribution(passing_df, team_1_name, team_2_name)
    chart3 = visualize_top_passing_accuracy(passing_df, team_1_name, team_2_name)
    chart4 = visualize_progressive_passers(passing_df, team_1_name, team_2_name)
    chart5 = visualize_key_pass_contributors(passing_df, team_1_name, team_2_name)
    chart6 = visualize_penetrative_passers(passing_df, team_1_name, team_2_name)
    chart7 = visualize_long_pass_specialists(passing_df, team_1_name, team_2_name)
    chart8 = visualize_advanced_pass_metrics(passing_df, team_1_name, team_2_name)
    chart9 = visualize_corner_kicks(passing_df, team_1_name, team_2_name)

    return chart1, chart2, chart3, chart4, chart5, chart6, chart7, chart8, chart9


if __name__ == "__main__":
    charts = main()
