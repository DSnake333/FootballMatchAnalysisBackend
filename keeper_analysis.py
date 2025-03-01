import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Step 1: Connect to SQLite Databases
def load_keeper_data():
    team_1_conn = sqlite3.connect("team_1_keeper_stats.db")
    team_2_conn = sqlite3.connect("team_2_keeper_stats.db")

    team_1_keeper_stats = pd.read_sql("SELECT * FROM keeper_stats", team_1_conn)
    team_2_keeper_stats = pd.read_sql("SELECT * FROM keeper_stats", team_2_conn)

    keeper_df = pd.concat([team_1_keeper_stats, team_2_keeper_stats], ignore_index=True)

    numeric_columns = [
        "Save %", "Saves", "Shots on Target Against", "Goals Against",
        "Post Shot Expected Goals", "Pass Completion %", "Passes Attempted",
        "Passes Attempted (GK)", "Launch %", "Goal Kicks Attempted",
        "% of Goal Kicks Launched", "Crosses Faced", "Crosses Stopped",
        "Def Actions outside Pen Area", "Average Distance of Def Actions"
    ]
    keeper_df[numeric_columns] = keeper_df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Derived metrics
    keeper_df["Save Efficiency"] = keeper_df["Save %"] / 100
    keeper_df["PSxG Difference"] = keeper_df["Saves"] - keeper_df["Post Shot Expected Goals"]
    keeper_df["Long Pass Effectiveness %"] = keeper_df["Launch %"]
    keeper_df["Save Success Rate"] = (
                                             keeper_df["Saves"] / keeper_df["Shots on Target Against"]
                                     ).fillna(0) * 100
    keeper_df["Defensive Workload Efficiency"] = (
            keeper_df["Def Actions outside Pen Area"] / keeper_df["Crosses Faced"]
    ).fillna(0)

    return keeper_df

# Visualization 1: Save Efficiency and PSxG Difference
def visualize_save_efficiency_psxg(keeper_df):
    # Create the bar chart using Plotly Express
    fig1 = px.bar(
        keeper_df,
        x="Player",
        y=["Save Efficiency", "PSxG Difference"],
        barmode="group",
        color="Team",
        title="Save Efficiency and PSxG Difference",
        labels={"value": "Metric Value", "variable": "Metric"}
    )
    fig1.update_layout(yaxis_title="Value", xaxis_title="Player")

    chart1 = fig1.to_json()

    return chart1


# Visualization 2: Cross Control Success
def visualize_cross_control_success(keeper_df):
    fig2 = px.bar(
        keeper_df,
        x="Player",
        y="Save Success Rate",
        color="Team",
        title="Save Success Rate",
        text="Save Success Rate"
    )
    fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig2.update_layout(yaxis_title="Percentage", xaxis_title="Player")
    chart2 = fig2.to_json()

    return chart2

# Visualization 3: Pass Effectiveness
def visualize_pass_effectiveness(keeper_df):
    fig3 = px.bar(
        keeper_df,
        x="Player",
        y=["Pass Completion %", "Long Pass Effectiveness %"],
        barmode="group",
        color="Team",
        title="Pass Effectiveness",
        labels={"value": "Percentage", "variable": "Metric"}
    )
    fig3.update_layout(yaxis_title="Percentage", xaxis_title="Player")
    chart3 = fig3.to_json()

    return chart3

# Visualization 4: Defensive Actions
def visualize_defensive_actions(keeper_df):
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=keeper_df["Player"],
        y=keeper_df["Def Actions outside Pen Area"],
        name="Def Actions outside Pen Area",
        marker_color="rgb(102, 197, 204)"
    ))
    fig4.add_trace(go.Bar(
        x=keeper_df["Player"],
        y=keeper_df["Average Distance of Def Actions"],
        name="Average Distance of Def Actions",
        marker_color="rgb(246, 78, 139)"
    ))
    fig4.update_layout(
        barmode="group",
        title="Defensive Actions Comparison",
        xaxis_title="Player",
        yaxis_title="Metric Value",
    )
    chart4 = fig4.to_json()

    return chart4

def visualize_defensive_workload_efficiency(keeper_df):

    fig5 = px.bar(
        keeper_df,
        x="Player",
        y="Defensive Workload Efficiency",
        color="Team",
        title="Defensive Workload Efficiency",
        text="Defensive Workload Efficiency"
    )
    fig5.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig5.update_layout(yaxis_title="Efficiency", xaxis_title="Player")
    chart5 = fig5.to_json()

    return chart5