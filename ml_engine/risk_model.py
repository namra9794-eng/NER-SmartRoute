"""
Disruption-risk scoring for road segments (spec point b).

For the prototype this is a transparent, tunable rule-based model whose
inputs mirror exactly what a trained ML model (e.g. gradient-boosted trees
on historical landslide/flood/road-damage data) would use. Swap
`predict()` for `model.predict_proba(...)` once a trained model
(`trained_model.pkl`) is available — the API contract stays identical, so
nothing else in the backend needs to change.
"""
from dataclasses import dataclass


@dataclass
class RiskInput:
    rainfall_mm_24h: float = 0
    rainfall_mm_72h: float = 0
    road_condition_score: float = 5      # 1 (excellent) - 10 (very poor)
    previous_incidents_count: int = 0    # landslides/floods on this segment, last 12 months
    traffic_congestion_pct: float = 0    # 0-100
    landslide_prone: bool = False
    flood_prone: bool = False
    slope_gradient_deg: float = 0


WEIGHTS = {
    "rainfall_24h": 0.020,
    "rainfall_72h": 0.010,
    "road_condition": 0.07,
    "previous_incidents": 0.08,
    "traffic": 0.004,
    "slope": 0.015,
}


def predict(data: RiskInput) -> dict:
    score = 0.0
    score += WEIGHTS["rainfall_24h"] * data.rainfall_mm_24h
    score += WEIGHTS["rainfall_72h"] * data.rainfall_mm_72h
    score += WEIGHTS["road_condition"] * data.road_condition_score
    score += WEIGHTS["previous_incidents"] * data.previous_incidents_count
    score += WEIGHTS["traffic"] * data.traffic_congestion_pct
    score += WEIGHTS["slope"] * data.slope_gradient_deg

    if data.landslide_prone:
        score += 1.2
    if data.flood_prone:
        score += 0.8

    # squash to a 0-1 probability
    probability = 1 / (1 + pow(2.71828, -(score - 4)))
    probability = round(min(max(probability, 0.0), 0.99), 3)

    if probability >= 0.75:
        risk = "critical"
    elif probability >= 0.5:
        risk = "high"
    elif probability >= 0.25:
        risk = "medium"
    else:
        risk = "low"

    # multiplier consumed by the route-optimization graph to inflate the
    # effective travel cost of high-risk edges (spec point c)
    edge_cost_multiplier = round(1.0 + probability * 4.0, 2)

    return {
        "risk": risk,
        "probability": probability,
        "edge_cost_multiplier": edge_cost_multiplier,
    }
