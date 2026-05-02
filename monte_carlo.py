import numpy as np
import random
from predictor import OUTCOMES, predict_probs

def simulate_innings(state, features, n_sims=500):
    win_count = 0
    next_over_runs_list = []
    wicket_sim_count = 0

    target = state.get("target")
    inning = state.get("inning", 1)

    for _ in range(n_sims):
        sim_runs = state["runs"]
        sim_wickets = state["wickets"]
        sim_balls = state["balls_bowled"]
        total_balls = state["total_overs"] * 6
        next_over_runs = 0
        current_over = state["over"]
        over_ball_count = 0
        wicket_this_sim = False

        while sim_balls < total_balls and sim_wickets < 10:
            probs = predict_probs(features)
            outcome = random.choices(OUTCOMES, weights=probs, k=1)[0]

            if outcome == "W":
                sim_wickets += 1
                if not wicket_this_sim:
                    wicket_this_sim = True
            else:
                sim_runs += int(outcome)

            sim_balls += 1

            if sim_balls <= current_over * 6 + 6:
                next_over_runs += (int(outcome) if outcome != "W" else 0)
                over_ball_count += 1

        next_over_runs_list.append(next_over_runs)
        if wicket_this_sim:
            wicket_sim_count += 1

        if inning == 2 and target is not None:
            if sim_runs >= target:
                win_count += 1
        else:
            win_count += 1 if sim_runs > 150 else 0

    win_prob = win_count / n_sims
    avg_next_over = np.mean(next_over_runs_list) if next_over_runs_list else 6.0
    wicket_prob = wicket_sim_count / n_sims

    return {
        "win_probability": round(win_prob, 4),
        "expected_next_over_runs": round(avg_next_over, 2),
        "wicket_probability": round(wicket_prob, 4),
    }
