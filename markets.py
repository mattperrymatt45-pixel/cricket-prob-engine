def compute_markets(sim_results, state):
    win_prob = sim_results.get("win_probability", 0.5)
    lose_prob = round(1.0 - win_prob, 4)
    next_over = sim_results.get("expected_next_over_runs", 6.0)
    wicket_prob = sim_results.get("wicket_probability", 0.1)

    return {
        "batting_team_win_prob": win_prob,
        "bowling_team_win_prob": lose_prob,
        "expected_runs_next_over": next_over,
        "wicket_probability_next_over": wicket_prob,
    }
