import sqlite3
import pandas as pd
import plotly.express as px

# Step 1: Connect to SQLite Databases and Load Data
def load_misc_data():
    team_1_conn = sqlite3.connect("team_1_misc_stats.db")
    team_2_conn = sqlite3.connect("team_2_misc_stats.db")

    team_1_misc_stats = pd.read_sql("SELECT * FROM misc_stats", team_1_conn)
    team_2_misc_stats = pd.read_sql("SELECT * FROM misc_stats", team_2_conn)

    team_1_misc_stats = team_1_misc_stats.iloc[:-1]
    team_2_misc_stats = team_2_misc_stats.iloc[:-1]

    misc_df = pd.concat([team_1_misc_stats, team_2_misc_stats], ignore_index=True)

    numeric_columns = [
        "Min", "Yellow Cards", "Red Cards", "Fouls Committed", "Fouls Drawn",
        "Offsides", "Crosses", "Interceptions", "Tackles Won", "Penalty Kicks Won",
        "Penalty Kicks Conceded", "Own Goals", "Ball Recoveries", "Aerials Won",
        "Aerials Lost", "% of Aerials Won"
    ]
    misc_df[numeric_columns] = misc_df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    return misc_df

# Step 2: Derive Metrics
def process_misc_data(misc_df):
    misc_df["Tackle Efficiency"] = (misc_df["Tackles Won"] / (misc_df["Tackles Won"] + misc_df["Fouls Committed"])) * 100
    misc_df["Interception Efficiency"] = (misc_df["Interceptions"] / (misc_df["Interceptions"] + misc_df["Fouls Committed"])) * 100
    misc_df["Fouls Efficiency"] = misc_df["Fouls Drawn"] / misc_df["Fouls Committed"]
    misc_df["Aerial Effectiveness"] = misc_df["Aerials Won"] / (misc_df["Aerials Won"] + misc_df["Aerials Lost"])
    misc_df["Defensive Impact"] = misc_df["Ball Recoveries"] + misc_df["Interceptions"] + misc_df["Tackles Won"]

    misc_df[["Tackle Efficiency", "Interception Efficiency", "Fouls Efficiency", "Aerial Effectiveness", "Defensive Impact"]] = misc_df[
        ["Tackle Efficiency", "Interception Efficiency", "Fouls Efficiency", "Aerial Effectiveness", "Defensive Impact"]
    ].fillna(0)

    return misc_df

# Visualization 1: Tackle and Interception Efficiency
def visualize_tackle_interception_efficiency(misc_df):
    fig1 = px.bar(
        misc_df,
        x="Player",
        y=["Tackle Efficiency", "Interception Efficiency"],
        barmode="group",
        color="Team",
        title="Tackle and Interception Efficiency",
        labels={"value": "Efficiency (%)", "variable": "Metric"}
    )
    fig1.update_layout(yaxis_title="Efficiency (%)", xaxis_title="Player")
    return fig1.to_json()

# Visualization 2: Fouls Efficiency
def visualize_fouls_efficiency(misc_df):
    fig2 = px.bar(
        misc_df,
        x="Player",
        y="Fouls Efficiency",
        color="Team",
        title="Fouls Efficiency (Fouls Drawn vs Committed)",
        text="Fouls Efficiency",
        labels={"Fouls Efficiency": "Efficiency"}
    )
    fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig2.update_layout(yaxis_title="Efficiency", xaxis_title="Player")
    return fig2.to_json()

# Visualization 3: Aerial Effectiveness
def visualize_aerial_effectiveness(misc_df):
    fig3 = px.bar(
        misc_df,
        x="Player",
        y="Aerial Effectiveness",
        color="Team",
        title="Aerial Effectiveness (%)",
        text="Aerial Effectiveness",
        labels={"Aerial Effectiveness": "Percentage"}
    )
    fig3.update_traces(texttemplate="%{text:.1%}", textposition="outside")
    fig3.update_layout(yaxis_title="Effectiveness (%)", xaxis_title="Player")
    return fig3.to_json()

# Visualization 4: Defensive Impact
def visualize_defensive_impact(misc_df):
    fig4 = px.bar(
        misc_df,
        x="Player",
        y="Defensive Impact",
        color="Team",
        title="Defensive Impact Score",
        text="Defensive Impact",
        labels={"Defensive Impact": "Impact Score"}
    )
    fig4.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig4.update_layout(yaxis_title="Impact Score", xaxis_title="Player")
    return fig4.to_json()
