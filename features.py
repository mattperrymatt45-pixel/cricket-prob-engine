import numpy as np
from state import balls_remaining, runs_required
from form import compute_batting_form, compute_bowling_form

VENUES = {}
_venue_counter = [0]

def encode_venue(venue):
    if venue not in VENUES:
        VENUES[venue] = _venue_counter[0]
        _venue_counter[0] += 1
    return VENUES[venue]

def build_features(state, player_stats, matchup_data, signals, all_deliveries):
    br = balls_remaining(state)
    rr = runs_required(state)
    run_rate = (state["runs"] / state["balls_bowled"] * 6) if state["balls_bowled"] > 0 else 0.0
    required_rate = ((rr / br * 6) if (rr is not None and br > 0) else 0.0)

    striker = state.get("striker", "")
    bowler = state.get("bowler", "")

    ps = player_stats.get(striker, {})
    bs = player_stats.get(bowler, {})

    bat_sr = float(ps.get("strike_rate", 120.0))
    bat_avg = float(ps.get("batting_avg", 30.0))
    bowl_eco = float(bs.get("economy", 7.5))
    bowl_avg = float(bs.get("bowling_avg", 28.0))

    mu_sr = 120.0
    mu_dismiss = 0.05
    if matchup_data is not None and not matchup_data.empty:
        row = matchup_data[
            (matchup_data["batsman"] == striker) & (matchup_data["bowler"] == bowler)
        ]
        if not row.empty:
            r = row.iloc[0]
            balls_f = float(r.get("balls", 1)) or 1
            runs_f = float(r.get("runs", 0))
            dis_f = float(r.get("dismissals", 0))
            mu_sr = (runs_f / balls_f * 100) if balls_f > 0 else 120.0
            mu_dismiss = dis_f / balls_f if balls_f > 0 else 0.05

    venue_enc = encode_venue(state.get("venue", "Unknown"))
    bat_form = compute_batting_form(striker, all_deliveries)
    bowl_form = compute_bowling_form(bowler, all_deliveries)

    pitch_slow = float(signals.get("pitch_slow", 0))
    dew = float(signals.get("dew", 0))
    swing = float(signals.get("swing", 0))
    bat_friendly = float(signals.get("batting_friendly", 0))

    feat = np.array([
        float(state["runs"]),
        float(state["wickets"]),
        float(br),
        run_rate,
        required_rate,
        bat_sr,
        bat_avg,
        bowl_eco,
        bowl_avg,
        mu_sr,
        mu_dismiss,
        float(venue_enc),
        bat_form,
        bowl_form,
        pitch_slow,
        dew,
        swing,
        bat_friendly,
    ], dtype=float)

    return feat
