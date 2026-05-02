def init_state(ball_events):
    state = {
        "runs": 0,
        "wickets": 0,
        "over": 0,
        "ball": 0,
        "balls_bowled": 0,
        "striker": "",
        "bowler": "",
        "total_overs": 20,
        "target": None,
        "inning": 1,
    }
    if not ball_events.empty:
        state["striker"] = ball_events.iloc[0].get("batsman", "")
        state["bowler"] = ball_events.iloc[0].get("bowler", "")
        state["inning"] = int(ball_events.iloc[0].get("inning", 1))
    return state

def update_state(state, ball_event):
    state["runs"] += int(ball_event.get("batsman_runs", 0))
    state["over"] = int(ball_event.get("over", state["over"]))
    state["ball"] = int(ball_event.get("ball", state["ball"]))
    state["balls_bowled"] += 1
    if int(ball_event.get("is_wicket", 0)) == 1:
        state["wickets"] += 1
    state["striker"] = ball_event.get("batsman", state["striker"])
    state["bowler"] = ball_event.get("bowler", state["bowler"])
    return state

def balls_remaining(state):
    total_balls = state["total_overs"] * 6
    return max(0, total_balls - state["balls_bowled"])

def runs_required(state):
    if state["target"] is None:
        return None
    return max(0, state["target"] - state["runs"])
