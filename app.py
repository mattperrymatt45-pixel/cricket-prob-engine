import streamlit as st
import time
import pandas as pd
from loader import load_data
from state import init_state, update_state, balls_remaining, runs_required
from features import build_features
from predictor import predict_probs, OUTCOMES
from commentary_signals import get_over_signals
from monte_carlo import simulate_innings
from markets import compute_markets

st.set_page_config(page_title="Cricket Probability Engine", layout="wide")
st.title("🏏 Cricket Match Probability Engine")

@st.cache_data
def get_match_ids():
    try:
        matches = pd.read_csv("matches.csv")
        return matches["match_id"].tolist()
    except:
        return [1, 2, 3]

match_ids = get_match_ids()
match_id = st.sidebar.selectbox("Select Match ID", match_ids)
n_sims = st.sidebar.slider("Monte Carlo Simulations", 100, 1000, 300, step=100)
sleep_time = st.sidebar.slider("Replay Speed (seconds/ball)", 0.1, 3.0, 0.5, step=0.1)
start = st.sidebar.button("▶ Start Replay")

score_placeholder = st.empty()
col1, col2, col3 = st.columns(3)
win_prob_ph = col1.empty()
next_over_ph = col2.empty()
wicket_prob_ph = col3.empty()
probs_ph = st.empty()
signals_ph = st.empty()
log_ph = st.empty()

if start:
    ball_events, match_info, player_stats, matchup_data, commentary_data = load_data(match_id)

    if ball_events.empty:
        st.error(f"No data found for match_id={match_id}")
    else:
        st.sidebar.success(f"Venue: {match_info.get('venue','?')} | {match_info.get('team1','?')} vs {match_info.get('team2','?')}")

        state = init_state(ball_events)
        state["venue"] = match_info.get("venue", "Unknown")
        log_entries = []

        innings_groups = ball_events.groupby("inning")

        for inning_num, inning_balls in innings_groups:
            state["inning"] = int(inning_num)
            state["balls_bowled"] = 0
            state["runs"] = 0
            state["wickets"] = 0
            state["over"] = 0
            state["ball"] = 0

            if inning_num == 2:
                prev = ball_events[ball_events["inning"] == 1]
                state["target"] = int(prev["batsman_runs"].sum()) + 1 if not prev.empty else None

            st.markdown(f"### Inning {inning_num}")

            for idx, row in inning_balls.iterrows():
                ball_event = row.to_dict()
                signals = get_over_signals(commentary_data, ball_event.get("over", 0))
                features = build_features(state, player_stats, matchup_data, signals, ball_events)
                probs = predict_probs(features)
                sim_results = simulate_innings(state, features, n_sims=n_sims)
                markets = compute_markets(sim_results, state)

                score_placeholder.markdown(
                    f"## 🏏 Score: **{state['runs']}/{state['wickets']}** | "
                    f"Over: {ball_event.get('over',0)}.{ball_event.get('ball',0)} | "
                    f"Balls Rem: {balls_remaining(state)}"
                )

                win_prob_ph.metric("🏆 Win Probability", f"{markets['batting_team_win_prob']*100:.1f}%")
                next_over_ph.metric("📈 Expected Runs Next Over", f"{markets['expected_runs_next_over']:.1f}")
                wicket_prob_ph.metric("🎯 Wicket Probability", f"{markets['wicket_probability_next_over']*100:.1f}%")

                prob_df = pd.DataFrame({
                    "Outcome": [str(o) for o in OUTCOMES],
                    "Probability": [round(float(p)*100, 2) for p in probs]
                })
                probs_ph.bar_chart(prob_df.set_index("Outcome"))
                signals_ph.json(signals)

                rr = runs_required(state)
                log_entry = {
                    "Over": f"{ball_event.get('over',0)}.{ball_event.get('ball',0)}",
                    "Striker": ball_event.get("batsman", ""),
                    "Bowler": ball_event.get("bowler", ""),
                    "Score": f"{state['runs']}/{state['wickets']}",
                    "Win%": f"{markets['batting_team_win_prob']*100:.1f}%",
                    "Req": rr if rr else "-"
                }
                log_entries.append(log_entry)
                log_ph.dataframe(pd.DataFrame(log_entries).tail(10), use_container_width=True)

                update_state(state, ball_event)
                time.sleep(sleep_time)

        st.success("✅ Replay Complete!")
