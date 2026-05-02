import numpy as np

OUTCOMES = [0, 1, 2, 3, 4, 6, "W"]

def base_probs():
    return np.array([0.30, 0.25, 0.12, 0.04, 0.12, 0.08, 0.09])

def run_rate_from_features(features):
    return features[3] if features[3] > 0 else 6.0

def predict_probs(features):
    probs = base_probs().copy()

    bat_sr = features[5]
    bat_avg = features[6]
    bowl_eco = features[7]
    bowl_avg = features[8]
    mu_sr = features[9]
    mu_dismiss = features[10]
    pitch_slow = features[14]
    dew = features[15]
    swing = features[16]
    bat_friendly = features[17]
    bat_form = features[12]
    bowl_form = features[13]
    wickets = features[1]
    balls_rem = features[2]
    req_rate = features[4]

    sr_factor = bat_sr / 120.0
    probs[4] *= max(0.5, min(2.0, sr_factor))
    probs[5] *= max(0.5, min(2.0, sr_factor * 0.9))
    probs[0] *= max(0.5, min(1.5, 1.0 / max(sr_factor, 0.5)))

    avg_factor = bat_avg / 30.0
    probs[6] *= max(0.5, min(1.5, 1.0 / max(avg_factor, 0.5)))

    eco_factor = 7.5 / max(bowl_eco, 4.0)
    probs[6] *= max(0.5, min(2.0, 30.0 / max(bowl_avg, 15.0)))
    probs[0] *= max(0.5, min(1.5, eco_factor))
    probs[4] *= max(0.5, min(1.5, 1.0 / max(eco_factor, 0.5)))

    mu_factor = mu_sr / 120.0
    probs[4] *= max(0.6, min(1.8, mu_factor))
    probs[6] *= max(0.6, min(1.8, mu_factor * 0.85))
    probs[6] *= max(0.5, min(2.0, mu_dismiss / max(0.05, 0.05)))

    if pitch_slow:
        probs[4] *= 0.75
        probs[5] *= 0.70
        probs[0] *= 1.20
        probs[6] *= 1.15

    if dew:
        probs[4] *= 1.10
        probs[5] *= 1.10
        probs[6] *= 0.85

    if swing:
        probs[6] *= 1.25
        probs[0] *= 1.10
        probs[4] *= 0.85

    if bat_friendly:
        probs[4] *= 1.15
        probs[5] *= 1.15
        probs[6] *= 0.80

    form_bat = min(2.0, max(0.5, bat_form / 30.0))
    form_bowl = min(2.0, max(0.5, 7.0 / max(bowl_form, 4.0)))
    probs[4] *= 1 + 0.1 * (form_bat - 1)
    probs[5] *= 1 + 0.1 * (form_bat - 1)
    probs[6] *= 1 + 0.1 * (form_bowl - 1)

    if balls_rem > 0 and req_rate > 0:
        pressure = req_rate / max(run_rate_from_features(features), 1.0)
        if pressure > 1.5:
            probs[5] *= 1.2
            probs[6] *= 1.15
            probs[0] *= 0.85

    if wickets >= 7:
        probs[4] *= 0.80
        probs[5] *= 0.70
        probs[6] *= 1.20

    probs = np.clip(probs, 1e-6, None)
    probs /= probs.sum()
    return probs
