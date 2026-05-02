import pandas as pd

def load_data(match_id):
    try:
        deliveries = pd.read_csv("deliveries.csv")
    except:
        deliveries = pd.DataFrame(columns=["match_id","inning","over","ball","batsman","bowler","batsman_runs","total_runs","is_wicket"])
    try:
        matches = pd.read_csv("matches.csv")
    except:
        matches = pd.DataFrame(columns=["match_id","venue","team1","team2"])
    try:
        players = pd.read_csv("players.csv")
    except:
        players = pd.DataFrame(columns=["player","batting_avg","strike_rate","bowling_avg","economy"])
    try:
        matchups = pd.read_csv("matchups.csv")
    except:
        matchups = pd.DataFrame(columns=["batsman","bowler","balls","runs","dismissals"])
    try:
        commentary = pd.read_csv("commentary.csv")
    except:
        commentary = pd.DataFrame(columns=["match_id","over","text"])

    ball_events = deliveries[deliveries["match_id"] == match_id].reset_index(drop=True)
    match_info = matches[matches["match_id"] == match_id].to_dict("records")
    match_info = match_info[0] if match_info else {"match_id": match_id, "venue": "Unknown", "team1": "Team A", "team2": "Team B"}
    player_stats = players.set_index("player").to_dict("index") if not players.empty else {}
    matchup_data = matchups
    commentary_data = commentary[commentary["match_id"] == match_id].reset_index(drop=True)

    return ball_events, match_info, player_stats, matchup_data, commentary_data
