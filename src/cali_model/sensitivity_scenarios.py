from __future__ import annotations

from copy import deepcopy


# Parameter naming convention
# ----------------------------
# The allocation formula weights are stored internally as:
#   tsac_beta    — the TSAC (Terrestrial Stewardship Allocation Component) weight
#   sosac_gamma  — the SOSAC (SIDS Ocean Stewardship Allocation Component) weight
# These names follow the convention used in the academic specification of the formula
# (Final_share = (1-β-γ)·IUSAF + β·TSAC + γ·SOSAC).
# Display labels in user-facing surfaces use “TSAC weight” and “SOSAC weight” for clarity.


DEFAULT_BASELINE = {
    "scenario_id": "gini_optimal_point",
    "fund_size": 1_000_000_000,
    "un_scale_mode": "band_inversion",
    "exclude_high_income": True,
    "iplc_share_pct": 50,
    "tsac_beta": 0.05,
    "sosac_gamma": 0.03,
    "floor_pct": 0.0,
    "ceiling_pct": None,
    "equality_mode": False,
}


def _scenario(**kwargs):
    scenario = deepcopy(DEFAULT_BASELINE)
    scenario.update(kwargs)
    return scenario


def get_scenario_library() -> dict[str, dict]:
    return {
        "pure_equality": _scenario(
            scenario_id="pure_equality",
            equality_mode=True,
            tsac_beta=0.0,
            sosac_gamma=0.0,
        ),
        "pure_iusaf_raw": _scenario(
            scenario_id="pure_iusaf_raw",
            un_scale_mode="raw_inversion",
            tsac_beta=0.0,
            sosac_gamma=0.0,
        ),
        "pure_iusaf_band": _scenario(
            scenario_id="pure_iusaf_band",
            un_scale_mode="band_inversion",
            tsac_beta=0.0,
            sosac_gamma=0.0,
        ),
        "gini_optimal_point": _scenario(
            scenario_id="gini_optimal_point",
            description=(
                "Gini-optimal point: minimises Gini coefficient while keeping "
                "Spearman vs pure IUSAF > 0.85. TSAC=5%, SOSAC=3%."
            ),
        ),
        "tsac_strict_balance": {
            **DEFAULT_BASELINE,
            "tsac_beta": 0.015,
            "sosac_gamma": 0.03,
            "scenario_id": "tsac_strict_balance",
        },
        "tsac_modified_balance": {
            **DEFAULT_BASELINE,
            "tsac_beta": 0.035,
            "sosac_gamma": 0.03,
            "scenario_id": "tsac_modified_balance",
        },
        "terrestrial_max": _scenario(scenario_id="terrestrial_max", tsac_beta=0.15, sosac_gamma=0.0),
        "ocean_max": _scenario(scenario_id="ocean_max", tsac_beta=0.0, sosac_gamma=0.10),
        "gini_optimal_floor_005": _scenario(
            scenario_id="gini_optimal_floor_005",
            floor_pct=0.05,
            description="Floor sensitivity at the gini-optimal point (0.05% floor).",
        ),
        "gini_optimal_ceiling_1": _scenario(
            scenario_id="gini_optimal_ceiling_1",
            ceiling_pct=1.0,
            description="Ceiling sensitivity at the gini-optimal point (1.0% ceiling).",
        ),
        "gini_optimal_floor_005_ceiling_1": _scenario(
            scenario_id="gini_optimal_floor_005_ceiling_1",
            floor_pct=0.05,
            ceiling_pct=1.0,
            description="Combined floor/ceiling sensitivity at the gini-optimal point.",
        ),
        "exclude_hi_off_compare": _scenario(scenario_id="exclude_hi_off_compare", exclude_high_income=False),
        "exclude_hi_on_compare": _scenario(scenario_id="exclude_hi_on_compare", exclude_high_income=True),
        "raw_vs_band_compare": _scenario(scenario_id="raw_vs_band_compare", un_scale_mode="raw_inversion"),
    }


def one_way_sweep(base_scenario: dict, parameter: str, values: list, scenario_prefix: str | None = None) -> list[dict]:
    scenarios = []
    prefix = scenario_prefix or f"{parameter}_sweep"
    for value in values:
        s = deepcopy(base_scenario)
        s[parameter] = value
        s["scenario_id"] = f"{prefix}_{value}"
        scenarios.append(s)
    return scenarios


def two_way_grid(base_scenario: dict, parameter_x: str, values_x: list, parameter_y: str, values_y: list, scenario_prefix: str | None = None) -> list[dict]:
    scenarios = []
    prefix = scenario_prefix or f"{parameter_x}_{parameter_y}_grid"
    for x in values_x:
        for y in values_y:
            s = deepcopy(base_scenario)
            s[parameter_x] = x
            s[parameter_y] = y
            s["scenario_id"] = f"{prefix}_{parameter_x}-{x}_{parameter_y}-{y}"
            scenarios.append(s)
    return scenarios


def get_default_ranges() -> dict[str, list]:
    return {
        "fund_size": [50_000_000, 200_000_000, 500_000_000, 1_000_000_000],
        "un_scale_mode": ["raw_inversion", "band_inversion"],
        "exclude_high_income": [True, False],
        "tsac_beta": [i / 100 for i in range(0, 16)],
        "tsac_beta_fine": [round(x * 0.005, 3) for x in range(21)],
        "sosac_gamma": [i / 100 for i in range(0, 11)],
        "sosac_gamma_fine": [round(x * 0.005, 3) for x in range(21)],
        "iplc_share_pct": [50, 60, 70, 80],
        "floor_pct": [0.0, 0.05, 0.10, 0.25],
        "ceiling_pct": [None, 1.0, 2.0, 5.0],
    }


def adjacent_values(values: list, current) -> list:
    if current not in values:
        return []
    idx = values.index(current)
    out = []
    if idx > 0:
        out.append(values[idx - 1])
    if idx < len(values) - 1:
        out.append(values[idx + 1])
    return out


def generate_local_neighbor_scenarios(base_scenario: dict, ranges: dict[str, list] | None = None) -> list[dict]:
    scenario = deepcopy(base_scenario)
    all_ranges = ranges or get_default_ranges()
    neighbors = []

    for param in ["tsac_beta", "sosac_gamma", "iplc_share_pct", "floor_pct", "ceiling_pct"]:
        for val in adjacent_values(all_ranges[param], scenario.get(param)):
            s = deepcopy(scenario)
            s[param] = val
            s["scenario_id"] = f"local_{param}_{val}"
            neighbors.append(s)

    # Deduplicate by full parameter signature in case adjacent settings collide
    seen = set()
    uniq = []
    for s in neighbors:
        sig = (
            s.get("fund_size"),
            s.get("un_scale_mode"),
            s.get("exclude_high_income"),
            s.get("iplc_share_pct"),
            s.get("tsac_beta"),
            s.get("sosac_gamma"),
            s.get("floor_pct"),
            s.get("ceiling_pct"),
            s.get("equality_mode"),
        )
        if sig in seen:
            continue
        seen.add(sig)
        uniq.append(s)

    return uniq
