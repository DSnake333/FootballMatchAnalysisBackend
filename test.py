from fastapi import FastAPI
from fastapi.responses import JSONResponse
from keeper_analysis import (
    load_keeper_data,
    visualize_save_efficiency_psxg,
    visualize_cross_control_success,
    visualize_pass_effectiveness,
    visualize_defensive_actions,
    visualize_defensive_workload_efficiency
)
from possession_analysis import (
    load_possession_data,
    calculate_possession_metrics,
    visualize_carry_take_on,
    visualize_progressive_pass_reception,
    visualize_touch_distribution,
    visualize_miscontrols_dispossessions
)

from misc_analysis import (
    load_misc_data,
    process_misc_data,
    visualize_tackle_interception_efficiency,
    visualize_fouls_efficiency,
    visualize_aerial_effectiveness,
    visualize_defensive_impact
)

from defense_analysis import (
    load_defense_data,
    visualize_tackling_efficiency,
    visualize_top_defenders,
    visualize_dribbler_stop_rate,
    visualize_defensive_pressure,
    visualize_players_defensive_impact
)

from shots_analysis import (
    load_shots_data,
    visualize_shot_outcomes,
    visualize_xg_heatmap,
    visualize_shot_distance_analysis,
    visualize_shooting_efficiency,
    visualize_top_players_sca
)

from passing_analysis import (
    load_passing_data,
    visualize_team_passing_metrics,
    visualize_pass_type_distribution,
    visualize_top_passing_accuracy,
    visualize_long_pass_specialists,
    visualize_key_pass_contributors,
    visualize_advanced_pass_metrics,
    visualize_progressive_passers,
    visualize_corner_kicks,
    visualize_penetrative_passers
)

from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/visualizations/metrics", response_class=JSONResponse)
def get_metrics():
    # Load and generate keeper data
    keeper_df = load_keeper_data()
    save_efficiency_chart = visualize_save_efficiency_psxg(keeper_df)
    cross_control_success_chart = visualize_cross_control_success(keeper_df)
    pass_effectiveness_chart = visualize_pass_effectiveness(keeper_df)
    defensive_actions_chart = visualize_defensive_actions(keeper_df)
    defensive_workload_efficiency_chart = visualize_defensive_workload_efficiency(keeper_df)

    # Load and generate possession data
    possession_df = load_possession_data()
    possession_df = calculate_possession_metrics(possession_df)
    carry_take_on_chart = visualize_carry_take_on(possession_df)
    progressive_pass_reception_chart = visualize_progressive_pass_reception(possession_df)
    touch_distribution_chart = visualize_touch_distribution(possession_df)
    miscontrols_dispossessions_chart = visualize_miscontrols_dispossessions(possession_df)

    # Load and generate misc data
    misc_df = load_misc_data()
    misc_df = process_misc_data(misc_df)
    tackle_interception_efficiency_chart = visualize_tackle_interception_efficiency(misc_df)
    fouls_efficiency_chart = visualize_fouls_efficiency(misc_df)
    aerial_efficiency_chart = visualize_aerial_effectiveness(misc_df)
    defensive_impact_chart = visualize_defensive_impact(misc_df)

    defense_df, team_1_name, team_2_name = load_defense_data()
    tackling_efficiency_chart = visualize_tackling_efficiency(defense_df, team_1_name, team_2_name)
    top_defenders_chart = visualize_top_defenders(defense_df, team_1_name, team_2_name)
    dribbler_stop_rate_chart = visualize_dribbler_stop_rate(defense_df, team_1_name, team_2_name)
    defensive_pressure_chart = visualize_defensive_pressure(defense_df, team_1_name, team_2_name)
    players_defensive_impact_chart = visualize_players_defensive_impact(defense_df, team_1_name, team_2_name)

    shots_df, team_1_name, team_2_name, team_1_metrics, team_2_metrics = load_shots_data()
    shot_outcomes_chart = visualize_shot_outcomes(shots_df, team_1_name, team_2_name)
    xg_heatmap_chart = visualize_xg_heatmap(shots_df, team_1_name, team_2_name)
    shot_distance_chart = visualize_shot_distance_analysis(shots_df, team_1_name, team_2_name)
    shooting_efficiency_chart = visualize_shooting_efficiency(shots_df, team_1_name, team_2_name, team_1_metrics, team_2_metrics)
    top_players_sca_chart = visualize_top_players_sca(shots_df, team_1_name, team_2_name)

    passing_df, team_1_name, team_2_name = load_passing_data()
    team_passing_metrics_chart = visualize_team_passing_metrics(passing_df, team_1_name, team_2_name)
    pass_type_distribution_chart = visualize_pass_type_distribution(passing_df, team_1_name, team_2_name)
    top_passing_accuracy_chart = visualize_top_passing_accuracy(passing_df, team_1_name, team_2_name)
    progressive_passers_chart = visualize_progressive_passers(passing_df, team_1_name, team_2_name)
    key_passers_chart = visualize_key_pass_contributors(passing_df, team_1_name, team_2_name)
    penetrative_passers_chart = visualize_penetrative_passers(passing_df, team_1_name, team_2_name)
    long_pass_specialists_chart = visualize_long_pass_specialists(passing_df, team_1_name, team_2_name)
    advanced_pass_metrics_chart = visualize_advanced_pass_metrics(passing_df, team_1_name, team_2_name)
    corner_kicks_chart = visualize_corner_kicks(passing_df, team_1_name, team_2_name)



    # Parse JSON strings to dictionaries if needed
    if isinstance(save_efficiency_chart, str):
        save_efficiency_chart = json.loads(save_efficiency_chart)
    if isinstance(cross_control_success_chart, str):
        cross_control_success_chart = json.loads(cross_control_success_chart)
    if isinstance(pass_effectiveness_chart, str):
        pass_effectiveness_chart = json.loads(pass_effectiveness_chart)
    if isinstance(defensive_actions_chart, str):
        defensive_actions_chart = json.loads(defensive_actions_chart)
    if isinstance(defensive_workload_efficiency_chart, str):
        defensive_workload_efficiency_chart = json.loads(defensive_workload_efficiency_chart)
    if isinstance(carry_take_on_chart, str):
        carry_take_on_chart = json.loads(carry_take_on_chart)
    if isinstance(progressive_pass_reception_chart, str):
        progressive_pass_reception_chart = json.loads(progressive_pass_reception_chart)
    if isinstance(touch_distribution_chart, str):
        touch_distribution_chart = json.loads(touch_distribution_chart)
    if isinstance(miscontrols_dispossessions_chart, str):
        miscontrols_dispossessions_chart = json.loads(miscontrols_dispossessions_chart)
    if isinstance(tackle_interception_efficiency_chart, str):
        tackle_interception_efficiency_chart = json.loads(tackle_interception_efficiency_chart)
    if isinstance(fouls_efficiency_chart, str):
        fouls_efficiency_chart = json.loads(fouls_efficiency_chart)
    if isinstance(aerial_efficiency_chart, str):
        aerial_efficiency_chart = json.loads(aerial_efficiency_chart)
    if isinstance(defensive_impact_chart, str):
        defensive_impact_chart = json.loads(defensive_impact_chart)
    if isinstance(tackling_efficiency_chart, str):
        tackling_efficiency_chart = json.loads(tackling_efficiency_chart)
    if isinstance(top_defenders_chart, str):
        top_defenders_chart = json.loads(top_defenders_chart)
    if isinstance(dribbler_stop_rate_chart, str):
        dribbler_stop_rate_chart = json.loads(dribbler_stop_rate_chart)
    if isinstance(defensive_pressure_chart, str):
        defensive_pressure_chart = json.loads(defensive_pressure_chart)
    if isinstance(players_defensive_impact_chart, str):
        players_defensive_impact_chart = json.loads(players_defensive_impact_chart)
    if isinstance(shot_outcomes_chart, str):
        shot_outcomes_chart = json.loads(shot_outcomes_chart)
    if isinstance(xg_heatmap_chart, str):
        xg_heatmap_chart = json.loads(xg_heatmap_chart)
    if isinstance(shot_distance_chart, str):
        shot_distance_chart = json.loads(shot_distance_chart)
    if isinstance(shooting_efficiency_chart, str):
        shooting_efficiency_chart = json.loads(shooting_efficiency_chart)
    if isinstance(top_players_sca_chart, str):
        top_players_sca_chart = json.loads(top_players_sca_chart)
    if isinstance(team_passing_metrics_chart, str):
        team_passing_metrics_chart = json.loads(team_passing_metrics_chart)
    if isinstance(pass_type_distribution_chart, str):
        pass_type_distribution_chart = json.loads(pass_type_distribution_chart)
    if isinstance(top_passing_accuracy_chart, str):
        top_passing_accuracy_chart = json.loads(top_passing_accuracy_chart)
    if isinstance(progressive_passers_chart, str):
        progressive_passers_chart = json.loads(progressive_passers_chart)
    if isinstance(key_passers_chart, str):
        key_passers_chart = json.loads(key_passers_chart)
    if isinstance(penetrative_passers_chart, str):
        penetrative_passers_chart = json.loads(penetrative_passers_chart)
    if isinstance(long_pass_specialists_chart, str):
        long_pass_specialists_chart = json.loads(long_pass_specialists_chart)
    if isinstance(advanced_pass_metrics_chart, str):
        advanced_pass_metrics_chart = json.loads(advanced_pass_metrics_chart)
    if isinstance(corner_kicks_chart, str):
        corner_kicks_chart = json.loads(corner_kicks_chart)


    # Combine keeper and possession charts into one response
    return {
        "save_efficiency": save_efficiency_chart,
        "cross_control_success": cross_control_success_chart,
        "pass_effectiveness": pass_effectiveness_chart,
        "defensive_actions": defensive_actions_chart,
        "defensive_workload": defensive_workload_efficiency_chart,
        "carry_take_on": carry_take_on_chart,
        "progressive_pass_reception": progressive_pass_reception_chart,
        "touch_distribution": touch_distribution_chart,
        "miscontrols_dispossessions": miscontrols_dispossessions_chart,
        "tackle_interception": tackle_interception_efficiency_chart,
        "fouls_efficiency": fouls_efficiency_chart,
        "aerial_efficiency": aerial_efficiency_chart,
        "defensive_impact": defensive_impact_chart,
        "tackling_efficiency": tackling_efficiency_chart,
        "top_defenders": top_defenders_chart,
        "dribbler_stop_rate": dribbler_stop_rate_chart,
        "defensive_pressure": defensive_pressure_chart,
        "players_defensive_impact": players_defensive_impact_chart,
        "shot_outcomes": shot_outcomes_chart,
        "xg_heatmap": xg_heatmap_chart,
        "shot_distance": shot_distance_chart,
        "shooting_efficiency": shooting_efficiency_chart,
        "top_players_sca": top_players_sca_chart,

        "team_passing_metrics": team_passing_metrics_chart,
        "pass_type_distribution": pass_type_distribution_chart,
        "top_passing_accuracy": top_passing_accuracy_chart,
        "progressive_passers": progressive_passers_chart,
        "key_passers": key_passers_chart,
        "penetrative_passers": penetrative_passers_chart,
        "long_pass_specialists": long_pass_specialists_chart,
        "advanced_pass_metrics": advanced_pass_metrics_chart,
        "corner_kicks": corner_kicks_chart,
    }