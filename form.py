import pandas as pd

def compute_batting_form(player_name, deliveries, n_matches=5):
    try:
        pdf = deliveries[deliveries["batsman"] == player_name]
        if pdf.empty:
            return 30.0
        match_runs = pdf.groupby("match_id")["batsman_runs"].sum().reset_index()
        last_n = match_runs.tail(n_matches)
        return float(last_n["batsman_runs"].mean()) if not last_n.empty else 30.0
    except:
        return 30.0

def compute_bowling_form(player_name, deliveries, n_matches=5):
    try:
        pdf = deliveries[deliveries["bowler"] == player_name]
        if pdf.empty:
            return 7.0
        match_stats = pdf.groupby("match_id").agg(
            runs=("total_runs", "sum"),
            balls=("ball", "count"),
            wickets=("is_wicket", "sum")
        ).reset_index()
        match_stats["economy"] = match_stats.apply(
            lambda r: (r["runs"] / (r["balls"] / 6)) if r["balls"] > 0 else 7.0, axis=1
        )
        last_n = match_stats.tail(n_matches)
        return float(last_n["economy"].mean()) if not last_n.empty else 7.0
    except:
        return 7.0
