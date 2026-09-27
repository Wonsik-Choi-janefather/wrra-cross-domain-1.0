#!/usr/bin/env python3
"""WRRA Cross-Domain 1.0 exact comparative validation.

The program combines a machine-readable re-analysis of the published WRRA Game
1.0 ledger with two new finite, exactly enumerable domains:

* a three-bus DC grid with thermal-memory residue; and
* two-machine scheduling with sequence-dependent setup residue.

The certified Renderer never guesses.  It partitions Law-permitted actions by
their complete future-relevant successor signature and retains one
minimum-cost representative per equivalence class.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, NamedTuple


INF = 10**12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def json_ready(value: Any) -> Any:
    if isinstance(value, Fraction):
        return fraction_text(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [json_ready(item) for item in value]
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    return value


# ---------------------------------------------------------------------------
# Domain 1: published Game 1.0 ledger adapter
# ---------------------------------------------------------------------------


def validate_game_ledger(path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    payload = json.loads(path.read_text(encoding="utf-8"))
    connect = payload["connect_k"]
    go = payload["go"]
    expected = {
        "reachable_full_states": 6_036_001,
        "directed_legal_edges": 23_453_344,
        "all_state_value_mismatches": 0,
        "baseline_nodes": 245_560,
        "renderer_nodes": 32,
        "go_reachable_full_states": 132_161,
        "residue_sensitive_classes": 752,
    }
    observed = {
        "reachable_full_states": connect["reachable_full_states"],
        "directed_legal_edges": connect["directed_legal_edges"],
        "all_state_value_mismatches": connect["all_state_value_mismatches"],
        "baseline_nodes": connect["root_alpha_beta"]["baseline"]["nodes"],
        "renderer_nodes": connect["root_alpha_beta"]["renderer_gate"]["nodes"],
        "go_reachable_full_states": go["reachable_full_states"],
        "residue_sensitive_classes": go[
            "classes_with_residue_dependent_legal_actions"
        ],
    }
    invariant_checks = {
        key: observed[key] == expected[key] for key in expected
    }
    full_work = observed["baseline_nodes"]
    reduced_work = observed["renderer_nodes"]
    return {
        "domain": "game",
        "status": "PASS" if all(invariant_checks.values()) else "FAIL",
        "source_status": "published_machine_readable_baseline",
        "source_file": str(path),
        "source_sha256": sha256_file(path),
        "exact_scope": "4x4 Connect-K (k=3), every reachable state",
        "residue_scope": "3x3 Go with simple ko, every reachable state",
        "minimal_sufficient_state": connect["minimal_sufficient_state"],
        "residue_state": go["minimal_sufficient_state"],
        "reachable_full_states": observed["reachable_full_states"],
        "directed_legal_edges": observed["directed_legal_edges"],
        "residue_system_full_states": observed["go_reachable_full_states"],
        "residue_sensitive_visible_classes": observed[
            "residue_sensitive_classes"
        ],
        "renderer_value_mismatches": observed["all_state_value_mismatches"],
        "work_unit": "root alpha-beta nodes",
        "full_work_units": full_work,
        "renderer_work_units": reduced_work,
        "work_reduction_fraction": 1.0 - reduced_work / full_work,
        "work_reduction_factor": full_work / reduced_work,
        "invariant_checks": invariant_checks,
        "witness": go["witness"],
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation": (
            "Game exactness and residue results are preserved from WRRA Game 1.0; "
            "this adapter validates its ledger invariants rather than relabelling "
            "the historical run as a new prospective experiment."
        ),
    }


def compare_game_ledgers(published_path: Path, reproduced_path: Path) -> dict[str, Any]:
    published = json.loads(published_path.read_text(encoding="utf-8"))
    reproduced = json.loads(reproduced_path.read_text(encoding="utf-8"))
    fields = {
        "connect_k.reachable_full_states": lambda value: value["connect_k"][
            "reachable_full_states"
        ],
        "connect_k.directed_legal_edges": lambda value: value["connect_k"][
            "directed_legal_edges"
        ],
        "connect_k.all_state_value_mismatches": lambda value: value["connect_k"][
            "all_state_value_mismatches"
        ],
        "connect_k.root_baseline_nodes": lambda value: value["connect_k"][
            "root_alpha_beta"
        ]["baseline"]["nodes"],
        "connect_k.root_renderer_nodes": lambda value: value["connect_k"][
            "root_alpha_beta"
        ]["renderer_gate"]["nodes"],
        "go.reachable_full_states": lambda value: value["go"][
            "reachable_full_states"
        ],
        "go.residue_sensitive_classes": lambda value: value["go"][
            "classes_with_residue_dependent_legal_actions"
        ],
    }
    comparisons = {
        field: {
            "published": getter(published),
            "reproduced": getter(reproduced),
            "match": getter(published) == getter(reproduced),
        }
        for field, getter in fields.items()
    }
    return {
        "published_file": str(published_path),
        "published_sha256": sha256_file(published_path),
        "reproduced_file": str(reproduced_path),
        "reproduced_sha256": sha256_file(reproduced_path),
        "all_declared_invariants_match": all(
            item["match"] for item in comparisons.values()
        ),
        "comparisons": comparisons,
        "excluded_from_identity_check": [
            "elapsed_seconds",
            "elapsed_seconds_total",
        ],
    }


# ---------------------------------------------------------------------------
# Domain 2: finite DC grid with thermal-memory residue
# ---------------------------------------------------------------------------


class GridAction(NamedTuple):
    peaker_a: int
    peaker_b: int
    shed_a: int
    shed_b: int


class GridState(NamedTuple):
    t: int
    heat_01: Fraction
    heat_12: Fraction
    heat_02: Fraction


GRID_DEMAND = (3, 4, 5, 4, 5, 3)
GRID_CAPACITY = (Fraction(2), Fraction(3, 2), Fraction(3, 2))
GRID_HEAT_LIMIT = Fraction(3, 2)
GRID_HEAT_DECAY = Fraction(1, 2)
GRID_ACTIONS = tuple(
    GridAction(pa, pb, sa, sb)
    for pa in (0, 1)
    for pb in (0, 1)
    for sa in (0, 1)
    for sb in (0, 1)
)


def grid_dc_flows(demand: int, action: GridAction) -> tuple[Fraction, ...] | None:
    peaker = action.peaker_a + action.peaker_b
    shed = action.shed_a + action.shed_b
    served = demand - shed
    slack = served - peaker
    if served < 0 or slack < 0 or slack > 4:
        return None
    p1 = Fraction(-served)
    p2 = Fraction(peaker)
    theta1 = (2 * p1 + p2) / 3
    theta2 = (p1 + 2 * p2) / 3
    return (-theta1, theta1 - theta2, -theta2)


def grid_transition(
    state: GridState, action: GridAction
) -> tuple[GridState, int, tuple[Fraction, ...]] | None:
    if state.t >= len(GRID_DEMAND):
        return None
    flows = grid_dc_flows(GRID_DEMAND[state.t], action)
    if flows is None:
        return None
    previous_heat = (state.heat_01, state.heat_12, state.heat_02)
    next_heat = tuple(
        GRID_HEAT_DECAY * old + max(Fraction(0), abs(flow) - capacity)
        for old, flow, capacity in zip(previous_heat, flows, GRID_CAPACITY)
    )
    if any(heat > GRID_HEAT_LIMIT for heat in next_heat):
        return None
    peaker = action.peaker_a + action.peaker_b
    shed = action.shed_a + action.shed_b
    served = GRID_DEMAND[state.t] - shed
    slack = served - peaker
    cost = 12 * shed + 3 * peaker + slack
    successor = GridState(state.t + 1, *next_heat)
    return successor, cost, flows


def grid_action_label(action: GridAction) -> str:
    return "P{}{}-S{}{}".format(*action)


def grid_legal_actions(state: GridState) -> list[GridAction]:
    return [action for action in GRID_ACTIONS if grid_transition(state, action)]


def grid_renderer_actions(state: GridState) -> list[GridAction]:
    representatives: dict[tuple[GridState, int], GridAction] = {}
    for action in GRID_ACTIONS:
        transition = grid_transition(state, action)
        if transition is None:
            continue
        successor, cost, _ = transition
        signature = (successor, cost)
        representatives.setdefault(signature, action)
    return list(representatives.values())


def enumerate_grid_states(root: GridState) -> set[GridState]:
    seen = {root}
    queue = deque([root])
    while queue:
        state = queue.popleft()
        for action in grid_legal_actions(state):
            successor, _, _ = grid_transition(state, action)  # type: ignore[misc]
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return seen


def run_grid_exact() -> dict[str, Any]:
    started = time.perf_counter()
    root = GridState(0, Fraction(0), Fraction(0), Fraction(0))
    reachable = enumerate_grid_states(root)

    @lru_cache(maxsize=None)
    def full_value(state: GridState) -> int:
        if state.t == len(GRID_DEMAND):
            return 0
        values = []
        for action in grid_legal_actions(state):
            successor, cost, _ = grid_transition(state, action)  # type: ignore[misc]
            values.append(cost + full_value(successor))
        return min(values, default=INF)

    @lru_cache(maxsize=None)
    def renderer_value(state: GridState) -> int:
        if state.t == len(GRID_DEMAND):
            return 0
        values = []
        for action in grid_renderer_actions(state):
            successor, cost, _ = grid_transition(state, action)  # type: ignore[misc]
            values.append(cost + renderer_value(successor))
        return min(values, default=INF)

    mismatch_states = []
    full_work = 0
    renderer_work = 0
    visible_groups: dict[tuple[int, int | None], list[GridState]] = defaultdict(list)
    for state in sorted(reachable):
        if state.t < len(GRID_DEMAND):
            full_work += len(grid_legal_actions(state))
            renderer_work += len(grid_renderer_actions(state))
        if full_value(state) != renderer_value(state):
            mismatch_states.append(state)
        demand = GRID_DEMAND[state.t] if state.t < len(GRID_DEMAND) else None
        visible_groups[(state.t, demand)].append(state)

    residue_sensitive = []
    witness = None
    value_sensitive_count = 0
    for visible, states in visible_groups.items():
        if len(states) < 2 or visible[1] is None:
            continue
        signatures: dict[GridState, tuple[str, ...]] = {}
        values: set[int] = set()
        for state in states:
            labels = tuple(sorted(grid_action_label(a) for a in grid_legal_actions(state)))
            signatures[state] = labels
            values.add(full_value(state))
        distinct_action_sets = {labels for labels in signatures.values()}
        if len(values) > 1:
            value_sensitive_count += 1
        if len(distinct_action_sets) > 1:
            residue_sensitive.append(visible)
            if witness is None:
                first = states[0]
                second = next(
                    state
                    for state in states[1:]
                    if signatures[state] != signatures[first]
                )
                witness = {
                    "visible_state": {"t": visible[0], "demand": visible[1]},
                    "state_a_heat": [fraction_text(v) for v in first[1:]],
                    "state_b_heat": [fraction_text(v) for v in second[1:]],
                    "state_a_legal_actions": list(signatures[first]),
                    "state_b_legal_actions": list(signatures[second]),
                    "state_a_exact_cost_to_go": full_value(first),
                    "state_b_exact_cost_to_go": full_value(second),
                }

    reduction_fraction = 1.0 - renderer_work / full_work
    return {
        "domain": "power_grid",
        "status": "PASS"
        if not mismatch_states and residue_sensitive and renderer_work < full_work
        else "FAIL",
        "model": "three-bus DC grid with two labelled identical peakers, two labelled identical curtailment blocks, and thermal-memory line constraints",
        "exact_scope": "all states reachable over a six-step deterministic demand trace",
        "law": {
            "demand_trace": list(GRID_DEMAND),
            "line_capacity": [fraction_text(v) for v in GRID_CAPACITY],
            "thermal_update": "h' = 1/2 h + max(0, |f|-capacity)",
            "thermal_limit": fraction_text(GRID_HEAT_LIMIT),
            "slack_generation_range": [0, 4],
            "objective": "minimize exact cumulative operating cost subject to balance and thermal survival"
        },
        "minimal_sufficient_state": "time index and three line thermal residues",
        "visible_state_ablation": "time index and demand only",
        "reachable_full_states": len(reachable),
        "directed_legal_edges": full_work,
        "residue_sensitive_visible_classes": len(residue_sensitive),
        "value_sensitive_visible_classes": value_sensitive_count,
        "renderer_value_mismatches": len(mismatch_states),
        "work_unit": "legal labelled action evaluations across reachable states",
        "full_work_units": full_work,
        "renderer_work_units": renderer_work,
        "work_reduction_fraction": reduction_fraction,
        "work_reduction_factor": full_work / renderer_work,
        "root_exact_cost": full_value(root),
        "root_renderer_cost": renderer_value(root),
        "witness": witness,
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation": (
            "Thermal residue is present constraint information: equal current demand "
            "does not imply equal safe action sets when line heat differs. The exact "
            "Renderer removes only actions with identical full successors and cost."
        ),
    }


# ---------------------------------------------------------------------------
# Domain 3: sequence-dependent scheduling
# ---------------------------------------------------------------------------


@dataclass(frozen=True, order=True)
class Job:
    identifier: str
    family: str
    duration: int


JOBS = (
    Job("A1", "A", 2),
    Job("A2", "A", 2),
    Job("A3", "A", 2),
    Job("B1", "B", 3),
    Job("B2", "B", 3),
    Job("B3", "B", 3),
)
JOB_BY_ID = {job.identifier: job for job in JOBS}


class MachineState(NamedTuple):
    available: int
    last_family: str


class ScheduleState(NamedTuple):
    remaining: tuple[str, ...]
    machine_0: MachineState
    machine_1: MachineState


class ScheduleAction(NamedTuple):
    job_id: str
    machine_index: int


def setup_time(last_family: str, next_family: str) -> int:
    if last_family == "-" or last_family == next_family:
        return 0
    return 2


def schedule_transition(
    state: ScheduleState, action: ScheduleAction
) -> ScheduleState | None:
    if action.job_id not in state.remaining or action.machine_index not in (0, 1):
        return None
    job = JOB_BY_ID[action.job_id]
    machines = [state.machine_0, state.machine_1]
    selected = machines[action.machine_index]
    finish = (
        selected.available
        + setup_time(selected.last_family, job.family)
        + job.duration
    )
    machines[action.machine_index] = MachineState(finish, job.family)
    remaining = tuple(item for item in state.remaining if item != action.job_id)
    return ScheduleState(remaining, machines[0], machines[1])


def schedule_actions(state: ScheduleState) -> list[ScheduleAction]:
    return [
        ScheduleAction(job_id, machine)
        for job_id in state.remaining
        for machine in (0, 1)
    ]


def schedule_canonical_signature(state: ScheduleState) -> tuple[Any, ...]:
    remaining_types = tuple(
        sorted(
            (JOB_BY_ID[job_id].family, JOB_BY_ID[job_id].duration)
            for job_id in state.remaining
        )
    )
    machines = tuple(sorted((state.machine_0, state.machine_1)))
    return remaining_types, machines


def schedule_visible_signature(state: ScheduleState) -> tuple[Any, ...]:
    remaining_types = tuple(
        sorted(
            (JOB_BY_ID[job_id].family, JOB_BY_ID[job_id].duration)
            for job_id in state.remaining
        )
    )
    availability = tuple(sorted((state.machine_0.available, state.machine_1.available)))
    return remaining_types, availability


def schedule_renderer_actions(state: ScheduleState) -> list[ScheduleAction]:
    representatives: dict[tuple[Any, ...], ScheduleAction] = {}
    for action in schedule_actions(state):
        successor = schedule_transition(state, action)
        assert successor is not None
        signature = schedule_canonical_signature(successor)
        representatives.setdefault(signature, action)
    return list(representatives.values())


def enumerate_schedule_states(root: ScheduleState) -> set[ScheduleState]:
    seen = {root}
    queue = deque([root])
    while queue:
        state = queue.popleft()
        for action in schedule_actions(state):
            successor = schedule_transition(state, action)
            assert successor is not None
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)
    return seen


def schedule_transition_profile(state: ScheduleState) -> tuple[Any, ...]:
    profile = []
    for action in schedule_actions(state):
        job = JOB_BY_ID[action.job_id]
        machine = (state.machine_0, state.machine_1)[action.machine_index]
        profile.append(
            (
                job.family,
                job.duration,
                machine.available,
                setup_time(machine.last_family, job.family),
            )
        )
    return tuple(sorted(set(profile)))


def run_scheduling_exact() -> dict[str, Any]:
    started = time.perf_counter()
    root = ScheduleState(
        tuple(job.identifier for job in JOBS),
        MachineState(0, "-"),
        MachineState(0, "-"),
    )
    reachable = enumerate_schedule_states(root)

    @lru_cache(maxsize=None)
    def full_value(state: ScheduleState) -> int:
        if not state.remaining:
            return max(state.machine_0.available, state.machine_1.available)
        return min(
            full_value(schedule_transition(state, action))  # type: ignore[arg-type]
            for action in schedule_actions(state)
        )

    @lru_cache(maxsize=None)
    def renderer_value(state: ScheduleState) -> int:
        if not state.remaining:
            return max(state.machine_0.available, state.machine_1.available)
        return min(
            renderer_value(schedule_transition(state, action))  # type: ignore[arg-type]
            for action in schedule_renderer_actions(state)
        )

    mismatches = []
    full_work = 0
    renderer_work = 0
    visible_groups: dict[tuple[Any, ...], list[ScheduleState]] = defaultdict(list)
    for state in sorted(reachable):
        if state.remaining:
            full_work += len(schedule_actions(state))
            renderer_work += len(schedule_renderer_actions(state))
        if full_value(state) != renderer_value(state):
            mismatches.append(state)
        visible_groups[schedule_visible_signature(state)].append(state)

    residue_sensitive = []
    value_sensitive_count = 0
    witness = None
    transition_only_witness = None
    for visible in sorted(visible_groups, key=repr):
        states = sorted(visible_groups[visible])
        if len(states) < 2:
            continue
        profiles = {state: schedule_transition_profile(state) for state in states}
        values = {full_value(state) for state in states}
        if len(values) > 1:
            value_sensitive_count += 1
        if len(set(profiles.values())) > 1:
            residue_sensitive.append(visible)
            if transition_only_witness is None:
                first = states[0]
                second = next(
                    state for state in states[1:] if profiles[state] != profiles[first]
                )
                transition_only_witness = {
                    "visible_state": {
                        "remaining_job_types": list(visible[0]),
                        "machine_availability": list(visible[1]),
                    },
                    "state_a_last_families": [
                        first.machine_0.last_family,
                        first.machine_1.last_family,
                    ],
                    "state_b_last_families": [
                        second.machine_0.last_family,
                        second.machine_1.last_family,
                    ],
                    "state_a_transition_profile": list(profiles[first]),
                    "state_b_transition_profile": list(profiles[second]),
                    "state_a_exact_makespan": full_value(first),
                    "state_b_exact_makespan": full_value(second),
                }
            if witness is None and len(values) > 1:
                # Choose the same witness deterministically on every Python run:
                # the lexicographically first state at the largest exact value,
                # followed by the first state at the smallest exact value.
                largest_value = max(values)
                smallest_value = min(values)
                first = next(
                    state for state in states if full_value(state) == largest_value
                )
                second = next(
                    state for state in states if full_value(state) == smallest_value
                )
                witness = {
                    "visible_state": {
                        "remaining_job_types": list(visible[0]),
                        "machine_availability": list(visible[1]),
                    },
                    "state_a_last_families": [
                        first.machine_0.last_family,
                        first.machine_1.last_family,
                    ],
                    "state_b_last_families": [
                        second.machine_0.last_family,
                        second.machine_1.last_family,
                    ],
                    "state_a_transition_profile": list(profiles[first]),
                    "state_b_transition_profile": list(profiles[second]),
                    "state_a_exact_makespan": full_value(first),
                    "state_b_exact_makespan": full_value(second),
                }

    if witness is None:
        witness = transition_only_witness

    return {
        "domain": "scheduling",
        "status": "PASS"
        if not mismatches and residue_sensitive and renderer_work < full_work
        else "FAIL",
        "model": "six labelled jobs, two identical machines, and family-dependent setup time",
        "exact_scope": "every state reachable from the declared six-job root",
        "law": {
            "jobs": [asdict(job) for job in JOBS],
            "machines": 2,
            "setup_time_same_family": 0,
            "setup_time_changed_family": 2,
            "objective": "minimize exact makespan"
        },
        "minimal_sufficient_state": "remaining labelled jobs plus each machine's availability and last-family residue",
        "visible_state_ablation": "remaining job types and machine availability only",
        "reachable_full_states": len(reachable),
        "directed_legal_edges": full_work,
        "residue_sensitive_visible_classes": len(residue_sensitive),
        "value_sensitive_visible_classes": value_sensitive_count,
        "renderer_value_mismatches": len(mismatches),
        "work_unit": "labelled job-machine action evaluations across reachable states",
        "full_work_units": full_work,
        "renderer_work_units": renderer_work,
        "work_reduction_fraction": 1.0 - renderer_work / full_work,
        "work_reduction_factor": full_work / renderer_work,
        "root_exact_makespan": full_value(root),
        "root_renderer_makespan": renderer_value(root),
        "witness": witness,
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation": (
            "The last processed family is present setup-state information. Equal "
            "machine availability and remaining job types can admit different next "
            "transition costs when this residue differs. The exact Renderer quotients "
            "only job-label and machine-permutation equivalents."
        ),
    }


def load_grid_scarcity_summary(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    by_key = {row["controller"]: row for row in payload["summary"]}
    return {
        "source_file": str(path),
        "source_sha256": sha256_file(path),
        "status": payload["status"],
        "episodes": payload["runs_per_point"]
        * len(payload["levels"])
        * len(payload["environments"])
        * len(payload["summary"]),
        "resource_constraint": payload["resource_constraint"],
        "g0_survival_curve_area": by_key["G0"]["survival_curve_area"],
        "g2_survival_curve_area": by_key["G2"]["survival_curve_area"],
        "g0_mean_active_compute": by_key["G0"]["mean_active_compute"],
        "g2_mean_active_compute": by_key["G2"]["mean_active_compute"],
        "interpretation": (
            "Preserved external-scale stochastic baseline. It is reported separately "
            "from the new exact finite-grid Renderer test."
        ),
    }


def write_csv(path: Path, domains: Iterable[dict[str, Any]]) -> None:
    fields = [
        "domain",
        "status",
        "exact_scope",
        "reachable_full_states",
        "residue_sensitive_visible_classes",
        "renderer_value_mismatches",
        "work_unit",
        "full_work_units",
        "renderer_work_units",
        "work_reduction_fraction",
        "work_reduction_factor",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for domain in domains:
            writer.writerow({field: domain.get(field, "") for field in fields})


def run_all(
    game_json: Path,
    output_dir: Path,
    grid_scarcity_json: Path | None,
    game_reproduced_json: Path | None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    game = validate_game_ledger(game_json)
    grid = run_grid_exact()
    scheduling = run_scheduling_exact()
    domains = [game, grid, scheduling]
    result = {
        "metadata": {
            "profile": "WRRA Cross-Domain 1.0",
            "architecture": "Wonsik Reality Renderer Architecture",
            "author": "Wonsik Choi",
            "email": "janefather@gmail.com",
            "date": "2026-09-27",
            "protocol": "protocol/preregistered_analysis_plan.json",
        },
        "common_execution_grammar": [
            "SOURCE",
            "RELATION/LAW",
            "STATE/RESIDUE",
            "BOUNDARY",
            "COMMON CARRIER",
            "UPDATE",
            "RENDERER",
            "PHENOTYPE",
            "OBSERVABLE/RECORD/LEDGER",
        ],
        "domains": domains,
        "game_reproduction": compare_game_ledgers(
            game_json, game_reproduced_json
        )
        if game_reproduced_json
        else None,
        "preserved_grid_scarcity_baseline": load_grid_scarcity_summary(
            grid_scarcity_json
        ),
        "cross_domain_conclusion": {
            "all_domains_passed": all(domain["status"] == "PASS" for domain in domains),
            "all_renderer_mismatches_zero": all(
                domain["renderer_value_mismatches"] == 0 for domain in domains
            ),
            "all_domains_show_residue_sensitivity": all(
                domain["residue_sensitive_visible_classes"] > 0
                for domain in domains
            ),
            "all_domains_reduce_work": all(
                domain["renderer_work_units"] < domain["full_work_units"]
                for domain in domains
            ),
            "claim": (
                "The fixed WRRA execution grammar was instantiated without structural "
                "change in three finite domains, and every certified reduction "
                "preserved the exact objective in its stated scope. This is evidence "
                "of cross-domain portability, not a proof of universal applicability."
            ),
        },
        "elapsed_seconds_total": time.perf_counter() - started,
    }
    result = json_ready(result)
    json_path = output_dir / "cross_domain_results.json"
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(output_dir / "cross_domain_summary.csv", domains)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-json", required=True, type=Path)
    parser.add_argument("--game-reproduced-json", type=Path)
    parser.add_argument("--grid-scarcity-json", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_all(
        args.game_json,
        args.output_dir,
        args.grid_scarcity_json,
        args.game_reproduced_json,
    )
    print(json.dumps(result["cross_domain_conclusion"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
