import time
from loader import load_data
from state import init_state, update_state, balls_remaining, runs_required
from features import build_features
from predictor import predict_probs, OUTCOMES
from commentary_signals import get_over_signals
from monte_carlo import simulate_innings
from markets import compute_markets

def replay_match(match_id, sleep_time=1.0, n_sims=300, callback=None):
    ball_events, match_info, player_stats, matchup_data, commentary_data = load_data(match_id)

    if ball_events.empty:
        print(f"No ball events found for match_id={match_id}")
        return

    state = init_state(ball_events)
    state["venue"] = match_info.get("venue", "Unknown")

    innings_groups = ball_events.groupby("inning")

    for inning_num, inning_balls in innings_groups:
        state["inning"] = int(inning_num)
        state["balls_bowled"] = 0
        state["runs"] = 0
        state["wickets"] = 0
        state["over"] = 0
        state["ball"] = 0

        if inning_num == 2:
            prev_inning = ball_events[ball_events["inning"] == 1]
            state["target"] = int(prev_inning["batsman_runs"].sum()) + 1 if not prev_inning.empty else None

        for idx, row in inning_balls.iterrows():
            ball_event = row.to_dict()
            signals = get_over_signals(commentary_data, ball_event.get("over", 0))
            features = build_features(state, player_stats, matchup_data, signals, ball_events)
            probs = predict_probs(features)
            sim_results = simulate_innings(state, features, n_sims=n_sims)
            markets = compute_markets(sim_results, state)

            output = {
                "match_id": match_id,
                "inning": inning_num,
                "over": ball_event.get("over", 0),
                "ball": ball_event.get("ball", 0),
                "striker": ball_event.get("batsman", ""),
                "bowler": ball_event.get("bowler", ""),
                "score": f"{state['runs']}/{state['wickets']}",
                "balls_remaining": balls_remaining(state),
                "runs_required": runs_required(state),
                "probs": {str(o): round(float(p), 4) for o, p in zip(OUTCOMES, probs)},
                "markets": markets,
                "signals": signals,
            }

            if callback:
                callback(output)
            else:
                print(output)

            update_state(state, ball_event)
            time.sleep(sleep_time)

    return state
