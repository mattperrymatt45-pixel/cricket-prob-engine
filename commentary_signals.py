def extract_signals(text):
    signals = {
        "pitch_slow": 0,
        "dew": 0,
        "swing": 0,
        "batting_friendly": 0,
    }
    if not isinstance(text, str):
        return signals
    t = text.lower()
    if any(w in t for w in ["slow", "turning", "spin", "grip", "rough"]):
        signals["pitch_slow"] = 1
    if any(w in t for w in ["dew", "wet outfield", "moisture"]):
        signals["dew"] = 1
    if any(w in t for w in ["swing", "seam", "movement", "nip"]):
        signals["swing"] = 1
    if any(w in t for w in ["flat", "batting paradise", "easy", "high scoring", "friendly"]):
        signals["batting_friendly"] = 1
    return signals

def get_over_signals(commentary_data, over_num):
    if commentary_data is None or commentary_data.empty:
        return {"pitch_slow": 0, "dew": 0, "swing": 0, "batting_friendly": 0}
    over_rows = commentary_data[commentary_data["over"] == over_num]
    combined = " ".join(over_rows["text"].dropna().tolist())
    return extract_signals(combined)
