"""POC-008 explainable land/corridor feasibility rules.

No route optimizer should consume a single unexplained scalar from this module.
Each observation retains its source class, role, weight and rationale. A later
solver may combine them, but the evidence remains inspectable per segment.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable

ROLE_HARD_EXCLUSION = "hard_exclusion"
ROLE_VERY_HIGH_PENALTY = "very_high_penalty"
ROLE_SOFT_PENALTY = "soft_penalty"
ROLE_NEUTRAL = "neutral_evidence"
ROLE_POSITIVE = "positive_preference"


@dataclass(frozen=True)
class FeasibilityRule:
    factor_class: str
    role: str
    weight: float
    rationale: str


# Weights are deliberately dimensionless POC levers, not dollar costs.
# Positive preference is represented by a negative weight.
RULES = {
    "transport_reservation_or_corridor": FeasibilityRule(
        "transport_reservation_or_corridor", ROLE_POSITIVE, -2.0,
        "Existing transport reservation/corridor can reduce acquisition and corridor-creation friction; compatibility must still be tested."
    ),
    "government_road": FeasibilityRule(
        "government_road", ROLE_POSITIVE, -1.0,
        "Existing government-road land is useful corridor evidence but does not imply HST geometric compatibility."
    ),
    "other_government_land": FeasibilityRule(
        "other_government_land", ROLE_NEUTRAL, 0.0,
        "Government ownership is recorded as evidence only until purpose, tenure and disposal constraints are known."
    ),
    "crown_leasehold": FeasibilityRule(
        "crown_leasehold", ROLE_SOFT_PENALTY, 1.0,
        "Crown leasehold is not equivalent to vacant government land and may carry occupancy/use rights."
    ),
    "crown_other": FeasibilityRule(
        "crown_other", ROLE_NEUTRAL, 0.25,
        "Crown tenure is heterogeneous; preserve the subtype and avoid treating it as automatically available."
    ),
    "private_land": FeasibilityRule(
        "private_land", ROLE_SOFT_PENALTY, 2.0,
        "Private land implies acquisition/compensation and fragmentation burden but is not infeasible."
    ),
    "indigenous_owned": FeasibilityRule(
        "indigenous_owned", ROLE_VERY_HIGH_PENALTY, 8.0,
        "Ownership and cultural/legal context require explicit engagement and should not be treated as ordinary acquisition land in a screening model."
    ),
    "state_forest": FeasibilityRule(
        "state_forest", ROLE_VERY_HIGH_PENALTY, 6.0,
        "State forest is public land with active management/environmental constraints, not spare corridor land."
    ),
    "national_park_or_conservation": FeasibilityRule(
        "national_park_or_conservation", ROLE_HARD_EXCLUSION, 1e6,
        "Protected/conservation estate is treated as a near-hard exclusion in POC-008 unless a later policy scenario explicitly tests otherwise."
    ),
    "dense_residential": FeasibilityRule(
        "dense_residential", ROLE_VERY_HIGH_PENALTY, 12.0,
        "Dense residential fabric implies displacement, severance, noise and acquisition impacts; tunnelling may later alter the surface penalty."
    ),
    "commercial_or_cbd": FeasibilityRule(
        "commercial_or_cbd", ROLE_VERY_HIGH_PENALTY, 10.0,
        "Dense commercial/CBD land has major acquisition and disruption consequences; underground solutions require separate treatment."
    ),
    "industrial": FeasibilityRule(
        "industrial", ROLE_SOFT_PENALTY, 4.0,
        "Industrial land is developed and operationally constrained but can be more corridor-compatible than dense residential land."
    ),
    "low_density_or_greenfield_urban": FeasibilityRule(
        "low_density_or_greenfield_urban", ROLE_SOFT_PENALTY, 3.0,
        "Urban fringe/developable land still carries future land-use conflict and acquisition burden."
    ),
    "major_interchange_conflict": FeasibilityRule(
        "major_interchange_conflict", ROLE_VERY_HIGH_PENALTY, 10.0,
        "Running through a major road/rail interchange footprint is materially different from making a controlled crossing."
    ),
    "major_infrastructure_crossing": FeasibilityRule(
        "major_infrastructure_crossing", ROLE_SOFT_PENALTY, 2.0,
        "A discrete crossing is normal engineering work; repeated or longitudinal conflict should score separately."
    ),
    "unresolved_tenure": FeasibilityRule(
        "unresolved_tenure", ROLE_SOFT_PENALTY, 3.0,
        "Unknown tenure should increase uncertainty rather than being silently treated as available."
    ),
}


def classify_nsw_tenure(tenure_class: str | None, tenure_type: str | None = None) -> FeasibilityRule:
    c = (tenure_class or "").strip().lower()
    t = (tenure_type or "").strip().lower()
    if "national park" in c or any(x in t for x in ("nature reserve", "conservation reserve", "regional park", "state conservation")):
        return RULES["national_park_or_conservation"]
    if "indigenous" in c or "aboriginal" in t:
        return RULES["indigenous_owned"]
    if "state forest" in c:
        return RULES["state_forest"]
    if "private" in c:
        return RULES["private_land"]
    if "leasehold" in c:
        return RULES["crown_leasehold"]
    if "crown" in c:
        if "road" in t:
            return RULES["government_road"]
        return RULES["crown_other"]
    return RULES["unresolved_tenure"]


def classify_abs_meshblock(land_use: str | None) -> FeasibilityRule:
    v = (land_use or "").strip().lower()
    if "residential" in v:
        return RULES["dense_residential"]
    if "commercial" in v:
        return RULES["commercial_or_cbd"]
    if "industrial" in v:
        return RULES["industrial"]
    return FeasibilityRule("other_meshblock_land_use", ROLE_NEUTRAL, 0.0, "Recorded for context; no v1 penalty assigned.")


def explain_rules() -> list[dict]:
    return [asdict(v) for v in RULES.values()]


def combine_observations(rules: Iterable[FeasibilityRule]) -> dict:
    """Return an explainable aggregate for diagnostics, not an opaque route score."""
    items = list(rules)
    hard = any(r.role == ROLE_HARD_EXCLUSION for r in items)
    return {
        "hard_exclusion": hard,
        "diagnostic_weight_sum": sum(r.weight for r in items),
        "roles": [r.role for r in items],
        "factors": [asdict(r) for r in items],
    }
