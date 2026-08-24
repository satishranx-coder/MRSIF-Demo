"""MRSIF CALM-buoy USV multibeam + Gemini fusion demonstrator.

Run the deterministic regression checks:
    python mrsif_calm_buoy_sonar_fusion.py --self-test

Run the interactive application:
    python -m pip install streamlit numpy plotly pillow
    streamlit run mrsif_calm_buoy_sonar_fusion.py

What this demonstrator does
---------------------------
* Plans a support-vessel stand-off and a surface-USV survey around a CALM buoy.
* Models a hull-centreline, downward-looking multibeam and a lateral/inboard-
  facing Tritech Gemini-style imaging sonar mounted below the turbulent
  waterline on one surveyed rigid reference frame.
* Generates deterministic synthetic seabed, chain, multibeam and imaging-sonar
  evidence for intact, suspended, discontinuous, terminated and displaced
  chain scenarios.
* Projects both acoustic sources into a common GNSS/IMU/time/offset frame,
  performs confidence fusion, identifies coverage gaps and renders a 3D
  evidence twin.
* Applies MRSIF G1-G8 GO/WATCH/HOLD gates and exports an auditable JSON record.

Assurance boundary
------------------
All geometry, signals, thresholds, classifications and operating limits in this
file are simulated/configured examples. They are not NORBIT or Tritech OEM
limits, do not represent live telemetry and are not a field release, survey
certificate, fitness-for-service decision or substitute for the approved CALM
buoy drawing, vessel RAMS, HIRA/JSA, OEM manuals, Vessel Master or IOCL approval.
The original client drawing is intentionally not reconstructed from memory. A
PNG/JPEG plan can be loaded in the application and must be independently
calibrated and accepted before a real line plan is released.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np


APP_TITLE = "MRSIF | CALM Buoy Sonar Fusion"
APP_VERSION = "Demonstration Release 1.0.1"


DEMO_LIMITS: dict[str, float] = {
    "minimum_vessel_standoff_m": 80.0,
    "minimum_usv_buoy_clearance_m": 22.0,
    "current_watch_mps": 0.60,
    "current_hold_mps": 0.90,
    "time_sync_watch_ms": 50.0,
    "time_sync_hold_ms": 100.0,
    "svp_age_watch_h": 3.0,
    "svp_age_hold_h": 6.0,
    "coreg_watch_m": 0.75,
    "coreg_hold_m": 1.25,
    "source_coverage_watch_pct": 75.0,
    "source_coverage_hold_pct": 55.0,
    "fused_confidence_watch": 0.55,
    "fused_confidence_hold": 0.35,
    "required_evidence_records": 7.0,
}


GATE_SEQUENCE: list[dict[str, str]] = [
    {
        "code": "G1",
        "name": "Approved drawing and asset basis",
        "phase": "Plan",
        "purpose": "Confirm drawing revision, chain identity, coordinates, datum and configured geometry.",
    },
    {
        "code": "G2",
        "name": "Vessel stand-off and launch corridor",
        "phase": "Plan",
        "purpose": "Keep the support vessel on the safer side and release a controlled USV corridor.",
    },
    {
        "code": "G3",
        "name": "Common reference and sensor alignment",
        "phase": "Mobilise",
        "purpose": "Validate GNSS/IMU, offsets, time, sound velocity and both below-waterline sonar mounts.",
    },
    {
        "code": "G4",
        "name": "USV and environmental readiness",
        "phase": "Acquire",
        "purpose": "Release acquisition only within the approved command, recovery and current envelope.",
    },
    {
        "code": "G5",
        "name": "Dual-sonar acquisition completeness",
        "phase": "Acquire",
        "purpose": "Confirm usable multibeam and Gemini evidence over the suspected chain corridor.",
    },
    {
        "code": "G6",
        "name": "Co-registration and fusion quality",
        "phase": "Fuse",
        "purpose": "Prevent fusion when coordinate, time or sensor-to-sensor residuals are unacceptable.",
    },
    {
        "code": "G7",
        "name": "Chain interpretation and escalation",
        "phase": "Decide",
        "purpose": "Classify the chain evidence without converting a sonar gap into an unsupported certainty.",
    },
    {
        "code": "G8",
        "name": "Evidence twin and closeout",
        "phase": "Deliver",
        "purpose": "Release only a traceable twin, source indexes, QC record and limitations statement.",
    },
]


@dataclass
class MissionConfig:
    scenario: str = "Apparent discontinuity"
    water_depth_m: float = 22.0
    buoy_radius_m: float = 8.0
    buoy_draft_m: float = 4.0
    anchor_radius_m: float = 110.0
    chain_count: int = 6
    suspect_bearing_deg: float = 225.0
    chain_diameter_m: float = 0.12
    vessel_standoff_m: float = 125.0
    usv_buoy_clearance_m: float = 28.0
    usv_cross_track_m: float = 13.0
    gemini_side: str = "Starboard"
    gemini_range_m: float = 45.0
    gemini_half_angle_deg: float = 55.0
    gemini_down_tilt_deg: float = 18.0
    mbes_half_swath_deg: float = 65.0
    grid_resolution_m: float = 1.5
    random_seed: int = 27


@dataclass
class GateResult:
    code: str
    name: str
    phase: str
    status: str
    reason: str
    required_action: str
    evidence: str


SCENARIOS = [
    "Intact / localised",
    "Suspended segment",
    "Apparent discontinuity",
    "Terminated / free-end pattern",
    "Displaced from design corridor",
]


def _clip_probability(value: np.ndarray | float) -> np.ndarray | float:
    return np.clip(value, 0.001, 0.999)


def bearing_vector(bearing_deg: float) -> np.ndarray:
    """Return East/North unit vector for a navigation bearing."""
    rad = math.radians(bearing_deg)
    return np.array([math.sin(rad), math.cos(rad)], dtype=float)


def bearing_from_vector(dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    return (np.degrees(np.arctan2(dx, dy)) + 360.0) % 360.0


def angle_difference_deg(a: np.ndarray, b: np.ndarray | float) -> np.ndarray:
    return (a - b + 180.0) % 360.0 - 180.0


def seabed_z(x: np.ndarray, y: np.ndarray, cfg: MissionConfig) -> np.ndarray:
    return (
        -cfg.water_depth_m
        + 0.28 * np.sin(x / 19.0)
        + 0.20 * np.cos(y / 23.0)
        + 0.08 * np.sin((x + y) / 9.0)
    )


def generate_chain(
    cfg: MissionConfig,
    bearing_deg: float | None = None,
    scenario: str | None = None,
    samples: int = 320,
) -> dict[str, np.ndarray]:
    """Generate expected and physical chain geometry in a local ENU frame."""
    bearing = cfg.suspect_bearing_deg if bearing_deg is None else bearing_deg
    scenario_name = cfg.scenario if scenario is None else scenario
    t = np.linspace(0.0, 1.0, samples)
    radial = cfg.buoy_radius_m + (cfg.anchor_radius_m - cfg.buoy_radius_m) * t
    direction = bearing_vector(bearing)
    right = bearing_vector(bearing + 90.0)
    xy = radial[:, None] * direction[None, :]

    touchdown = 0.69
    upper = np.clip(t / touchdown, 0.0, 1.0)
    smooth = 3.0 * upper**2 - 2.0 * upper**3
    target_bottom = -cfg.water_depth_m + 0.28
    z = -cfg.buoy_draft_m + (target_bottom + cfg.buoy_draft_m) * smooth
    bottom_mask = t > touchdown
    z[bottom_mask] = seabed_z(xy[bottom_mask, 0], xy[bottom_mask, 1], cfg) + 0.18

    physical = np.ones_like(t, dtype=bool)
    if scenario_name == "Suspended segment":
        lift = 4.2 * np.exp(-((t - 0.69) / 0.105) ** 2)
        z = z + lift
    elif scenario_name == "Apparent discontinuity":
        physical &= ~((t >= 0.48) & (t <= 0.565))
    elif scenario_name == "Terminated / free-end pattern":
        physical &= t <= 0.57
    elif scenario_name == "Displaced from design corridor":
        active = np.clip((t - 0.20) / 0.62, 0.0, 1.0)
        lateral = 7.0 * np.sin(np.pi * active) * (t < 0.88)
        xy = xy + lateral[:, None] * right[None, :]

    xyz = np.column_stack((xy, z))
    return {"t": t, "xyz": xyz, "physical": physical}


def generate_other_chains(cfg: MissionConfig) -> list[dict[str, Any]]:
    chains: list[dict[str, Any]] = []
    spacing = 360.0 / max(cfg.chain_count, 1)
    for index in range(cfg.chain_count):
        bearing = (cfg.suspect_bearing_deg + index * spacing) % 360.0
        scenario = cfg.scenario if index == 0 else "Intact / localised"
        chains.append({"bearing": bearing, "suspect": index == 0, **generate_chain(cfg, bearing, scenario)})
    return chains


def build_usv_path(cfg: MissionConfig) -> dict[str, np.ndarray]:
    """Create an offset radial line plus an inner orbit for complementary insonification."""
    bearing = cfg.suspect_bearing_deg
    direction = bearing_vector(bearing)
    right = bearing_vector(bearing + 90.0)
    side_sign = -1.0 if cfg.gemini_side == "Starboard" else 1.0

    radial = np.linspace(cfg.usv_buoy_clearance_m, cfg.anchor_radius_m - 4.0, 30)
    radial_xy = radial[:, None] * direction[None, :] + side_sign * cfg.usv_cross_track_m * right[None, :]
    radial_heading = np.full(radial.shape, bearing)

    orbit_bearings = np.linspace(bearing - 64.0, bearing + 64.0, 19)
    orbit_xy = np.vstack([cfg.usv_buoy_clearance_m * bearing_vector(value) for value in orbit_bearings])
    mount_azimuth = 90.0 if cfg.gemini_side == "Starboard" else -90.0
    orbit_heading = (orbit_bearings + 180.0 - mount_azimuth) % 360.0

    xy = np.vstack((orbit_xy, radial_xy))
    heading = np.concatenate((orbit_heading, radial_heading))
    return {"xy": xy, "heading_deg": heading, "orbit_count": np.array([len(orbit_xy)])}


def _nearest_distances(query: np.ndarray, reference: np.ndarray, chunk: int = 256) -> np.ndarray:
    if len(reference) == 0:
        return np.full(len(query), np.inf)
    output = np.empty(len(query), dtype=float)
    for start in range(0, len(query), chunk):
        block = query[start : start + chunk]
        delta = block[:, None, :] - reference[None, :, :]
        output[start : start + chunk] = np.sqrt(np.min(np.sum(delta * delta, axis=2), axis=1))
    return output


def simulate_mbes(
    cfg: MissionConfig,
    chain: dict[str, np.ndarray],
    path: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    truth = chain["xyz"]
    physical = chain["physical"]
    pose_xy = path["xy"]
    delta = truth[:, None, :2] - pose_xy[None, :, :]
    horizontal = np.sqrt(np.sum(delta * delta, axis=2))
    nearest = np.argmin(horizontal, axis=1)
    min_horizontal = horizontal[np.arange(len(truth)), nearest]
    vertical = np.maximum(np.abs(truth[:, 2] + 0.45), 1.0)
    swath_half_width = vertical * math.tan(math.radians(cfg.mbes_half_swath_deg))
    geometry_visible = min_horizontal <= np.maximum(swath_half_width, 6.0)

    t = chain["t"]
    steep_penalty = np.where(t < 0.20, 0.36, 0.0)
    suspended_penalty = np.where(truth[:, 2] > (-cfg.water_depth_m + 3.0), 0.12, 0.0)
    detection_probability = np.clip(0.91 - steep_penalty - suspended_penalty, 0.18, 0.94)
    detected = physical & geometry_visible & (rng.random(len(truth)) < detection_probability)
    xyz = truth[detected] + rng.normal(0.0, [0.16, 0.16, 0.09], size=(int(np.sum(detected)), 3))
    probability = np.clip(detection_probability[detected] + rng.normal(0.0, 0.035, int(np.sum(detected))), 0.20, 0.98)
    intensity = np.clip(0.45 + 0.50 * probability + rng.normal(0.0, 0.05, len(probability)), 0.05, 1.0)
    return {
        "xyz": xyz,
        "probability": probability,
        "intensity": intensity,
        "truth_index": np.flatnonzero(detected),
        "pose_index": nearest[detected],
    }


def simulate_gemini(
    cfg: MissionConfig,
    chain: dict[str, np.ndarray],
    path: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    truth = chain["xyz"]
    physical = chain["physical"]
    pose_xy = path["xy"]
    heading = path["heading_deg"]
    mount_azimuth = 90.0 if cfg.gemini_side == "Starboard" else -90.0
    sonar_bearing = (heading + mount_azimuth) % 360.0

    dx = truth[:, None, 0] - pose_xy[None, :, 0]
    dy = truth[:, None, 1] - pose_xy[None, :, 1]
    horizontal = np.sqrt(dx * dx + dy * dy)
    slant = np.sqrt(horizontal * horizontal + (truth[:, None, 2] + 0.45) ** 2)
    target_bearing = bearing_from_vector(dx, dy)
    angular_error = np.abs(angle_difference_deg(target_bearing, sonar_bearing[None, :]))
    vertical_depression = np.degrees(np.arctan2(np.abs(truth[:, None, 2] + 0.45), np.maximum(horizontal, 0.1)))
    vertical_error = np.abs(vertical_depression - cfg.gemini_down_tilt_deg)
    valid = (
        (slant <= cfg.gemini_range_m)
        & (angular_error <= cfg.gemini_half_angle_deg)
        & (vertical_error <= 48.0)
    )
    score = angular_error / max(cfg.gemini_half_angle_deg, 1.0) + slant / max(cfg.gemini_range_m, 1.0)
    score = np.where(valid, score, np.inf)
    best_pose = np.argmin(score, axis=1)
    geometry_visible = np.isfinite(score[np.arange(len(truth)), best_pose])

    t = chain["t"]
    base_probability = np.where(t < 0.32, 0.91, 0.82)
    bottom_penalty = np.where(truth[:, 2] < (-cfg.water_depth_m + 0.9), 0.10, 0.0)
    detection_probability = np.clip(base_probability - bottom_penalty, 0.30, 0.96)
    detected = physical & geometry_visible & (rng.random(len(truth)) < detection_probability)
    count = int(np.sum(detected))
    xyz = truth[detected] + rng.normal(0.0, [0.24, 0.24, 0.18], size=(count, 3))
    probability = np.clip(detection_probability[detected] + rng.normal(0.0, 0.04, count), 0.20, 0.99)
    intensity = np.clip(0.42 + 0.54 * probability + rng.normal(0.0, 0.06, count), 0.04, 1.0)
    return {
        "xyz": xyz,
        "probability": probability,
        "intensity": intensity,
        "truth_index": np.flatnonzero(detected),
        "pose_index": best_pose[detected],
    }


def _paint_probability_map(
    axis: np.ndarray,
    detections: dict[str, np.ndarray],
    sigma_m: float,
) -> np.ndarray:
    output = np.zeros((len(axis), len(axis)), dtype=float)
    if len(detections["xyz"]) == 0:
        return output
    resolution = float(axis[1] - axis[0])
    radius = max(1, int(math.ceil(3.0 * sigma_m / resolution)))
    for point, probability in zip(detections["xyz"], detections["probability"]):
        ix = int(round((point[0] - axis[0]) / resolution))
        iy = int(round((point[1] - axis[0]) / resolution))
        for oy in range(-radius, radius + 1):
            gy = iy + oy
            if gy < 0 or gy >= len(axis):
                continue
            for ox in range(-radius, radius + 1):
                gx = ix + ox
                if gx < 0 or gx >= len(axis):
                    continue
                distance_sq = (ox * resolution) ** 2 + (oy * resolution) ** 2
                value = float(probability) * math.exp(-distance_sq / (2.0 * sigma_m**2))
                if value > output[gy, gx]:
                    output[gy, gx] = value
    return output


def fuse_evidence(
    cfg: MissionConfig,
    expected_chain: dict[str, np.ndarray],
    mbes: dict[str, np.ndarray],
    gemini: dict[str, np.ndarray],
) -> dict[str, Any]:
    extent = cfg.anchor_radius_m + 18.0
    axis = np.arange(-extent, extent + cfg.grid_resolution_m, cfg.grid_resolution_m)
    mbes_map = _paint_probability_map(axis, mbes, sigma_m=1.25)
    gemini_map = _paint_probability_map(axis, gemini, sigma_m=1.60)
    fused = 1.0 - (1.0 - 0.88 * mbes_map) * (1.0 - 0.92 * gemini_map)
    fused += 0.13 * np.minimum(mbes_map, gemini_map)
    fused = np.clip(fused, 0.0, 0.999)

    expected_xyz = expected_chain["xyz"]
    ix = np.clip(np.round((expected_xyz[:, 0] - axis[0]) / cfg.grid_resolution_m).astype(int), 0, len(axis) - 1)
    iy = np.clip(np.round((expected_xyz[:, 1] - axis[0]) / cfg.grid_resolution_m).astype(int), 0, len(axis) - 1)
    confidence_along = fused[iy, ix]

    bin_count = 48
    bin_edges = np.linspace(0.0, 1.0, bin_count + 1)
    bin_confidence = np.zeros(bin_count)
    for index in range(bin_count):
        mask = (expected_chain["t"] >= bin_edges[index]) & (expected_chain["t"] < bin_edges[index + 1])
        if np.any(mask):
            bin_confidence[index] = float(np.max(confidence_along[mask]))
    detected_bins = bin_confidence >= 0.34
    coverage_pct = 100.0 * float(np.mean(detected_bins))

    longest_gap = 0
    current_gap = 0
    longest_start = 0
    current_start = 0
    for index, detected in enumerate(detected_bins):
        if detected:
            current_gap = 0
        else:
            if current_gap == 0:
                current_start = index
            current_gap += 1
            if current_gap > longest_gap:
                longest_gap = current_gap
                longest_start = current_start
    gap_start_fraction = longest_start / bin_count
    gap_end_fraction = (longest_start + longest_gap) / bin_count

    overlap_pairs = 0
    coreg_rmse = float("inf")
    if len(mbes["xyz"]) and len(gemini["xyz"]):
        distances = _nearest_distances(mbes["xyz"], gemini["xyz"])
        matched = distances <= 2.5
        overlap_pairs = int(np.sum(matched))
        if overlap_pairs:
            coreg_rmse = float(np.sqrt(np.mean(distances[matched] ** 2)))

    return {
        "axis": axis,
        "mbes_map": mbes_map,
        "gemini_map": gemini_map,
        "fused_map": fused,
        "confidence_along": confidence_along,
        "bin_confidence": bin_confidence,
        "coverage_pct": coverage_pct,
        "mean_confidence": float(np.mean(confidence_along)),
        "longest_gap_pct": 100.0 * longest_gap / bin_count,
        "gap_start_fraction": gap_start_fraction,
        "gap_end_fraction": gap_end_fraction,
        "overlap_pairs": overlap_pairs,
        "coreg_rmse_m": coreg_rmse,
    }


def build_gemini_image(
    cfg: MissionConfig,
    chain: dict[str, np.ndarray],
    path: dict[str, np.ndarray],
    gemini: dict[str, np.ndarray],
    rng: np.random.Generator,
) -> dict[str, np.ndarray | int]:
    angle_axis = np.linspace(-cfg.gemini_half_angle_deg, cfg.gemini_half_angle_deg, 300)
    range_axis = np.linspace(0.0, cfg.gemini_range_m, 360)
    image = rng.gamma(shape=1.2, scale=0.018, size=(len(range_axis), len(angle_axis)))

    if len(gemini["pose_index"]):
        counts = np.bincount(gemini["pose_index"], minlength=len(path["xy"]))
        focus_pose = int(np.argmax(counts))
    else:
        focus_pose = 0
    pose_xy = path["xy"][focus_pose]
    heading = float(path["heading_deg"][focus_pose])
    mount_azimuth = 90.0 if cfg.gemini_side == "Starboard" else -90.0
    sonar_bearing = (heading + mount_azimuth) % 360.0

    points = chain["xyz"][chain["physical"]]
    dx = points[:, 0] - pose_xy[0]
    dy = points[:, 1] - pose_xy[1]
    horizontal = np.sqrt(dx * dx + dy * dy)
    slant = np.sqrt(horizontal * horizontal + (points[:, 2] + 0.45) ** 2)
    bearings = bearing_from_vector(dx, dy)
    angles = angle_difference_deg(bearings, sonar_bearing)
    valid = (slant <= cfg.gemini_range_m) & (np.abs(angles) <= cfg.gemini_half_angle_deg)

    def add_spot(angle_deg: float, range_m: float, amplitude: float, angle_sigma: float = 0.75, range_sigma: float = 0.28) -> None:
        ai = int(np.argmin(np.abs(angle_axis - angle_deg)))
        ri = int(np.argmin(np.abs(range_axis - range_m)))
        aw = max(2, int(math.ceil(3.0 * angle_sigma / max(angle_axis[1] - angle_axis[0], 0.01))))
        rw = max(2, int(math.ceil(3.0 * range_sigma / max(range_axis[1] - range_axis[0], 0.01))))
        a0, a1 = max(0, ai - aw), min(len(angle_axis), ai + aw + 1)
        r0, r1 = max(0, ri - rw), min(len(range_axis), ri + rw + 1)
        aa = angle_axis[a0:a1][None, :]
        rr = range_axis[r0:r1][:, None]
        spot = amplitude * np.exp(-0.5 * ((aa - angle_deg) / angle_sigma) ** 2 - 0.5 * ((rr - range_m) / range_sigma) ** 2)
        image[r0:r1, a0:a1] += spot

    for angle, distance in zip(angles[valid][::2], slant[valid][::2]):
        add_spot(float(angle), float(distance), amplitude=float(rng.uniform(0.52, 0.96)))

    buoy_dx, buoy_dy = -pose_xy[0], -pose_xy[1]
    buoy_range = math.sqrt(buoy_dx**2 + buoy_dy**2 + cfg.buoy_draft_m**2)
    buoy_bearing = float(angle_difference_deg(np.array([bearing_from_vector(np.array([buoy_dx]), np.array([buoy_dy]))[0]]), sonar_bearing)[0])
    if abs(buoy_bearing) <= cfg.gemini_half_angle_deg and buoy_range <= cfg.gemini_range_m:
        for delta in np.linspace(-4.0, 4.0, 17):
            add_spot(buoy_bearing + delta, buoy_range + 0.04 * delta**2, 0.35, angle_sigma=1.1, range_sigma=0.42)

    image = np.clip(image, 0.0, 1.0)
    return {"angles_deg": angle_axis, "range_m": range_axis, "intensity": image, "focus_pose": focus_pose}


def classify_evidence(
    cfg: MissionConfig,
    expected_chain: dict[str, np.ndarray],
    mbes: dict[str, np.ndarray],
    gemini: dict[str, np.ndarray],
    fusion: dict[str, Any],
) -> str:
    if fusion["mean_confidence"] < DEMO_LIMITS["fused_confidence_hold"]:
        return "Inconclusive - fused evidence below configured demonstration confidence"

    combined = np.vstack([mbes["xyz"], gemini["xyz"]]) if len(mbes["xyz"]) + len(gemini["xyz"]) else np.empty((0, 3))
    if len(combined):
        # Compare observations with the configured intact catenary. Absolute
        # clearance cannot identify an anomaly because the healthy catenary is
        # naturally suspended from the buoy to its touchdown point.
        expected_xyz = expected_chain["xyz"]
        horizontal_delta = combined[:, None, :2] - expected_xyz[None, :, :2]
        horizontal_distance_sq = np.sum(horizontal_delta * horizontal_delta, axis=2)
        nearest_expected = np.argmin(horizontal_distance_sq, axis=1)
        corridor_offset = np.sqrt(horizontal_distance_sq[np.arange(len(combined)), nearest_expected])
        vertical_residual = combined[:, 2] - expected_xyz[nearest_expected, 2]

        if float(np.mean(corridor_offset > 3.5)) > 0.35:
            return "Displaced from configured design corridor pattern"
        if float(np.mean(vertical_residual > 2.0)) > 0.12:
            return "Observed suspended / unsupported segment pattern"

    if fusion["longest_gap_pct"] >= 20.0 and fusion["gap_start_fraction"] >= 0.48:
        return "Apparent termination / free-end pattern - engineering confirmation required"
    if fusion["longest_gap_pct"] >= 4.0 and 0.18 < fusion["gap_start_fraction"] < 0.82:
        return "Apparent internal discontinuity - targeted reacquisition or ROV verification required"

    return "Chain localised with no configured discontinuity threshold exceeded"


def simulate_mission(cfg: MissionConfig) -> dict[str, Any]:
    rng = np.random.default_rng(cfg.random_seed)
    chain = generate_chain(cfg)
    expected = generate_chain(cfg, scenario="Intact / localised")
    path = build_usv_path(cfg)
    mbes = simulate_mbes(cfg, chain, path, rng)
    gemini = simulate_gemini(cfg, chain, path, rng)
    fusion = fuse_evidence(cfg, expected, mbes, gemini)
    gemini_image = build_gemini_image(cfg, chain, path, gemini, rng)
    classification = classify_evidence(cfg, expected, mbes, gemini, fusion)

    extent = cfg.anchor_radius_m + 12.0
    ground_axis = np.linspace(-extent, extent, 48)
    xx, yy = np.meshgrid(ground_axis, ground_axis)
    zz = seabed_z(xx, yy, cfg)
    return {
        "chain": chain,
        "expected_chain": expected,
        "all_chains": generate_other_chains(cfg),
        "path": path,
        "mbes": mbes,
        "gemini": gemini,
        "fusion": fusion,
        "gemini_image": gemini_image,
        "classification": classification,
        "seabed": {"x": xx, "y": yy, "z": zz},
    }


def evaluate_gates(
    cfg: MissionConfig,
    simulation: dict[str, Any],
    controls: dict[str, Any],
) -> list[GateResult]:
    metrics = simulation["fusion"]
    results: list[GateResult] = []

    def add(index: int, status: str, reason: str, action: str, evidence: str) -> None:
        spec = GATE_SEQUENCE[index]
        results.append(GateResult(spec["code"], spec["name"], spec["phase"], status, reason, action, evidence))

    if controls["field_release_mode"] and not controls["approved_drawing_valid"]:
        add(0, "HOLD", "Approved CALM buoy drawing, revision or datum is not accepted.", "Do not release the field line plan; load and verify the approved drawing and chain identity.", "Drawing/datum: invalid")
    elif not controls["approved_drawing_valid"]:
        add(0, "WATCH", "Configured schematic is being used for demonstration only.", "Upload and calibrate the approved drawing before changing to field-release mode.", "Drawing: demonstration schematic")
    else:
        add(0, "GO", "Drawing basis, revision, datum and suspected-chain identity are recorded.", "Freeze the approved geometry and revision in the mission evidence package.", "Drawing/datum: accepted")

    minimum_standoff = max(DEMO_LIMITS["minimum_vessel_standoff_m"], 4.0 * cfg.buoy_radius_m)
    if cfg.vessel_standoff_m < minimum_standoff or cfg.usv_buoy_clearance_m < DEMO_LIMITS["minimum_usv_buoy_clearance_m"]:
        add(1, "HOLD", "Configured vessel stand-off or USV clearance is inside the demonstration abort boundary.", "Move the vessel to the safer approved side and reissue the geofence/launch corridor.", f"Vessel {cfg.vessel_standoff_m:.0f} m; USV {cfg.usv_buoy_clearance_m:.0f} m")
    elif not controls["simops_approved"] or not controls["launch_corridor_clear"]:
        add(1, "HOLD", "SIMOPS or launch/recovery corridor control is not accepted.", "Obtain bridge/client release and clear the corridor before deployment.", "SIMOPS/corridor: failed")
    else:
        add(1, "GO", "Support vessel and USV corridor remain outside the configured abort boundary.", "Maintain bridge link, lookout and stop-work authority.", f"Vessel {cfg.vessel_standoff_m:.0f} m; USV {cfg.usv_buoy_clearance_m:.0f} m")

    reference_failures = [
        label
        for label, valid in {
            "GNSS/IMU": controls["gnss_imu_valid"],
            "surveyed offsets": controls["offsets_valid"],
            "MBES mount": controls["mbes_mount_valid"],
            "Gemini mount": controls["gemini_mount_valid"],
            "sound velocity": controls["sound_velocity_valid"],
        }.items()
        if not valid
    ]
    if reference_failures or controls["time_sync_ms"] > DEMO_LIMITS["time_sync_hold_ms"] or controls["svp_age_h"] > DEMO_LIMITS["svp_age_hold_h"]:
        add(2, "HOLD", "Common reference invalid: " + ", ".join(reference_failures or ["time/SVP limit exceeded"]), "Do not fuse; restore the coordinate/time/offset/SVP basis and repeat verification.", f"Clock {controls['time_sync_ms']:.0f} ms; SVP {controls['svp_age_h']:.1f} h")
    elif controls["time_sync_ms"] > DEMO_LIMITS["time_sync_watch_ms"] or controls["svp_age_h"] > DEMO_LIMITS["svp_age_watch_h"]:
        add(2, "WATCH", "Reference remains usable only under the configured caution threshold.", "Refresh SVP/time checks and document the effect on co-registration.", f"Clock {controls['time_sync_ms']:.0f} ms; SVP {controls['svp_age_h']:.1f} h")
    else:
        add(2, "GO", "Both sonars share an accepted GNSS/IMU/time/offset/SVP reference.", "Lock the mounting and configuration record before acquisition.", f"Clock {controls['time_sync_ms']:.0f} ms; SVP {controls['svp_age_h']:.1f} h")

    if not controls["usv_ready"] or not controls["command_link_valid"] or not controls["recovery_ready"] or controls["surface_current_mps"] >= DEMO_LIMITS["current_hold_mps"]:
        add(3, "HOLD", "USV, command/recovery control or current limit is unacceptable.", "Retain/recover the USV and restore readiness before acquisition.", f"Current {controls['surface_current_mps']:.2f} m/s")
    elif controls["surface_current_mps"] >= DEMO_LIMITS["current_watch_mps"]:
        add(3, "WATCH", "Current is inside the configured caution band.", "Use a reduced line plan and earlier recovery trigger.", f"Current {controls['surface_current_mps']:.2f} m/s")
    else:
        add(3, "GO", "USV, command, recovery and environmental readiness are accepted.", "Run the approved outer-to-inner acquisition sequence.", f"Current {controls['surface_current_mps']:.2f} m/s")

    mbes_count = len(simulation["mbes"]["xyz"])
    gemini_count = len(simulation["gemini"]["xyz"])
    source_coverage = float(metrics["coverage_pct"])
    if not controls["mbes_online"] or not controls["gemini_online"] or source_coverage < DEMO_LIMITS["source_coverage_hold_pct"]:
        add(4, "HOLD", "A required sonar source is offline or corridor evidence is materially incomplete.", "Restore both sources or re-run the missing sector before fusion.", f"MBES {mbes_count}; Gemini {gemini_count}; coverage {source_coverage:.1f}%")
    elif source_coverage < DEMO_LIMITS["source_coverage_watch_pct"]:
        add(4, "WATCH", "Dual-source evidence is usable but has a material coverage gap.", "Acquire targeted cross-lines/side-looking passes before final classification.", f"MBES {mbes_count}; Gemini {gemini_count}; coverage {source_coverage:.1f}%")
    else:
        add(4, "GO", "Multibeam and Gemini evidence cover the configured corridor.", "Freeze raw source indexes and proceed to co-registration QC.", f"MBES {mbes_count}; Gemini {gemini_count}; coverage {source_coverage:.1f}%")

    coreg = float(metrics["coreg_rmse_m"])
    if not math.isfinite(coreg) or coreg > DEMO_LIMITS["coreg_hold_m"] or results[2].status == "HOLD":
        add(5, "HOLD", "Co-registration residual or upstream common-reference gate is unacceptable.", "Do not publish a fused output; correct offsets/time/reference and reprocess.", f"Matched pairs {metrics['overlap_pairs']}; RMSE {coreg:.2f} m")
    elif coreg > DEMO_LIMITS["coreg_watch_m"]:
        add(5, "WATCH", "Fusion residual is inside the configured caution band.", "Retain source separation and label positional uncertainty in the twin.", f"Matched pairs {metrics['overlap_pairs']}; RMSE {coreg:.2f} m")
    else:
        add(5, "GO", "Source overlap and co-registration residual support fusion.", "Generate the confidence layer without deleting either raw source.", f"Matched pairs {metrics['overlap_pairs']}; RMSE {coreg:.2f} m")

    confidence = float(metrics["mean_confidence"])
    classification = simulation["classification"]
    if confidence < DEMO_LIMITS["fused_confidence_hold"] or "Inconclusive" in classification:
        add(6, "HOLD", "Evidence is insufficient for a field classification.", "Reacquire or escalate to positioned ROV verification; report the result as inconclusive.", f"Confidence {confidence:.2f}; {classification}")
    elif confidence < DEMO_LIMITS["fused_confidence_watch"] or "Apparent" in classification:
        add(6, "WATCH", "The acoustic pattern requires cautious wording and independent verification.", "Issue an apparent-condition statement and target the confidence gap for ROV/engineering review.", f"Confidence {confidence:.2f}; {classification}")
    else:
        add(6, "GO", "Configured evidence supports the stated acoustic classification.", "Retain uncertainty and observation boundaries in the report.", f"Confidence {confidence:.2f}; {classification}")

    closeout_ok = all(
        [
            controls["raw_data_indexed"],
            controls["qc_log_complete"],
            controls["provenance_complete"],
            controls["two_copies_verified"],
            controls["evidence_records"] >= DEMO_LIMITS["required_evidence_records"],
        ]
    )
    if not closeout_ok:
        add(7, "HOLD", "Evidence index, QC, provenance, backups or minimum record count is incomplete.", "Complete the traceable evidence package before releasing the twin/report.", f"Evidence records {controls['evidence_records']}")
    elif any(result.status == "HOLD" for result in results[:7]):
        add(7, "HOLD", "An upstream non-bypassable gate remains on HOLD.", "Resolve the upstream gate; do not close out by administrative override.", f"Evidence records {controls['evidence_records']}")
    elif any(result.status == "WATCH" for result in results[:7]):
        add(7, "WATCH", "Closeout evidence is complete but upstream qualifications remain.", "Release only a qualified demonstration/inspection record with limitations.", f"Evidence records {controls['evidence_records']}")
    else:
        add(7, "GO", "Traceable evidence, QC, provenance and backups are complete.", "Release the controlled evidence twin and report package.", f"Evidence records {controls['evidence_records']}")

    return results


def overall_status(gates: list[GateResult]) -> str:
    if any(gate.status == "HOLD" for gate in gates):
        return "HOLD"
    if any(gate.status == "WATCH" for gate in gates):
        return "WATCH"
    return "GO"


def evidence_report(
    cfg: MissionConfig,
    simulation: dict[str, Any],
    controls: dict[str, Any],
    gates: list[GateResult],
) -> dict[str, Any]:
    fusion = simulation["fusion"]
    return {
        "application": APP_TITLE,
        "version": APP_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "boundary": "Simulated/configured demonstration; not live telemetry, field release or certification.",
        "mission_config": asdict(cfg),
        "classification": simulation["classification"],
        "fusion_metrics": {
            "mbes_returns": len(simulation["mbes"]["xyz"]),
            "gemini_returns": len(simulation["gemini"]["xyz"]),
            "coverage_pct": round(float(fusion["coverage_pct"]), 2),
            "mean_confidence": round(float(fusion["mean_confidence"]), 3),
            "longest_gap_pct": round(float(fusion["longest_gap_pct"]), 2),
            "coreg_rmse_m": round(float(fusion["coreg_rmse_m"]), 3),
            "matched_source_pairs": int(fusion["overlap_pairs"]),
        },
        "controls": controls,
        "overall_status": overall_status(gates),
        "gates": [asdict(gate) for gate in gates],
    }


def _plotly_imports() -> tuple[Any, Any]:
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError as exc:
        raise SystemExit("Plotly is required. Install with: python -m pip install plotly") from exc
    return go, make_subplots


def make_plan_figure(cfg: MissionConfig, simulation: dict[str, Any], drawing_image: Any | None = None, drawing_opacity: float = 0.35) -> Any:
    go, _ = _plotly_imports()
    fig = go.Figure()
    extent = cfg.anchor_radius_m + 30.0
    if drawing_image is not None:
        fig.add_layout_image(
            dict(
                source=drawing_image,
                xref="x",
                yref="y",
                x=-extent,
                y=extent,
                sizex=2.0 * extent,
                sizey=2.0 * extent,
                sizing="stretch",
                opacity=drawing_opacity,
                layer="below",
            )
        )

    for item in simulation["all_chains"]:
        xyz = item["xyz"]
        physical = item["physical"]
        fig.add_trace(
            go.Scatter(
                x=xyz[:, 0],
                y=xyz[:, 1],
                mode="lines",
                line=dict(width=3.5 if item["suspect"] else 1.3, dash="solid" if item["suspect"] else "dot"),
                opacity=0.95 if item["suspect"] else 0.35,
                name="Suspected chain - physical" if item["suspect"] else "Other configured chain",
                showlegend=item["suspect"] or item is simulation["all_chains"][1],
            )
        )
        if item["suspect"] and not np.all(physical):
            fig.add_trace(
                go.Scatter(
                    x=xyz[~physical, 0],
                    y=xyz[~physical, 1],
                    mode="lines+markers",
                    line=dict(width=2, dash="dash"),
                    marker=dict(size=5, symbol="x"),
                    name="Expected but not returned",
                )
            )

    path = simulation["path"]
    fig.add_trace(go.Scatter(x=path["xy"][:, 0], y=path["xy"][:, 1], mode="lines", line=dict(width=3), name="USV acquisition path"))
    sample_indices = np.linspace(0, len(path["xy"]) - 1, 4, dtype=int)
    mount_azimuth = 90.0 if cfg.gemini_side == "Starboard" else -90.0
    for index in sample_indices:
        # Plotly 6.x validates Boolean properties strictly. Comparisons between
        # NumPy integer scalars return numpy.bool_, so normalise the value before
        # passing it to showlegend (required by newer Streamlit Cloud images).
        show_sample_legend = bool(int(index) == int(sample_indices[0]))
        position = path["xy"][index]
        heading = float(path["heading_deg"][index])
        sonar_bearing = heading + mount_azimuth
        left = bearing_vector(sonar_bearing - cfg.gemini_half_angle_deg)
        right = bearing_vector(sonar_bearing + cfg.gemini_half_angle_deg)
        fan = np.vstack([position, position + cfg.gemini_range_m * left, position + cfg.gemini_range_m * right, position])
        fig.add_trace(go.Scatter(x=fan[:, 0], y=fan[:, 1], mode="lines", fill="toself", opacity=0.08, line=dict(width=1), showlegend=show_sample_legend, name="Gemini lateral fan"))

        swath = cfg.water_depth_m * math.tan(math.radians(cfg.mbes_half_swath_deg))
        right_vec = bearing_vector(heading + 90.0)
        swath_line = np.vstack([position - swath * right_vec, position + swath * right_vec])
        fig.add_trace(go.Scatter(x=swath_line[:, 0], y=swath_line[:, 1], mode="lines", opacity=0.24, line=dict(width=2), showlegend=show_sample_legend, name="MBES seabed swath"))

    vessel_bearing = (cfg.suspect_bearing_deg + 150.0) % 360.0
    vessel_xy = cfg.vessel_standoff_m * bearing_vector(vessel_bearing)
    fig.add_trace(go.Scatter(x=[vessel_xy[0]], y=[vessel_xy[1]], mode="markers+text", marker=dict(size=18, symbol="diamond"), text=["Client vessel"], textposition="top center", name="Client vessel"))
    fig.add_trace(go.Scatter(x=[0.0], y=[0.0], mode="markers+text", marker=dict(size=28, symbol="circle"), text=["CALM buoy"], textposition="top center", name="CALM buoy"))
    fig.add_trace(go.Scatter(x=[path["xy"][0, 0]], y=[path["xy"][0, 1]], mode="markers+text", marker=dict(size=14, symbol="triangle-up"), text=["USV"], textposition="bottom center", name="USV"))
    fig.update_layout(
        title="Plan view - vessel stand-off, USV route and complementary acoustic coverage",
        xaxis_title="Easting from buoy (m)",
        yaxis_title="Northing from buoy (m)",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        xaxis=dict(range=[-extent, extent]),
        yaxis_range=[-extent, extent],
        margin=dict(l=20, r=20, t=55, b=20),
        height=680,
        legend=dict(orientation="h"),
    )
    return fig


def make_mbes_figure(cfg: MissionConfig, simulation: dict[str, Any], show_truth: bool) -> Any:
    go, _ = _plotly_imports()
    fig = go.Figure()
    seabed = simulation["seabed"]
    fig.add_trace(go.Surface(x=seabed["x"], y=seabed["y"], z=seabed["z"], opacity=0.52, colorscale="Earth", showscale=False, name="Seabed"))
    mbes = simulation["mbes"]
    fig.add_trace(go.Scatter3d(x=mbes["xyz"][:, 0], y=mbes["xyz"][:, 1], z=mbes["xyz"][:, 2], mode="markers", marker=dict(size=3, color=mbes["intensity"], colorscale="Turbo", colorbar=dict(title="Return")), name="MBES chain returns"))
    if show_truth:
        expected = simulation["expected_chain"]["xyz"]
        fig.add_trace(go.Scatter3d(x=expected[:, 0], y=expected[:, 1], z=expected[:, 2], mode="lines", line=dict(width=4, dash="dash"), name="Configured expected corridor"))
    fig.update_layout(title="Synthetic multibeam point cloud - seabed and chain relief", scene=dict(xaxis_title="E (m)", yaxis_title="N (m)", zaxis_title="Elevation (m)", aspectmode="data"), height=650, margin=dict(l=0, r=0, t=50, b=0))
    return fig


def make_gemini_figure(simulation: dict[str, Any]) -> Any:
    go, _ = _plotly_imports()
    image = simulation["gemini_image"]
    fig = go.Figure(go.Heatmap(x=image["angles_deg"], y=image["range_m"], z=image["intensity"], colorscale="Cividis", zmin=0.0, zmax=1.0, colorbar=dict(title="Echo")))
    fig.update_layout(title="Synthetic side-mounted Gemini image - chain and buoy echoes", xaxis_title="Bearing from sonar centreline (deg)", yaxis_title="Slant range (m)", yaxis_autorange="reversed", height=600, margin=dict(l=20, r=20, t=55, b=20))
    return fig


def make_fusion_figure(cfg: MissionConfig, simulation: dict[str, Any]) -> Any:
    go, _ = _plotly_imports()
    fusion = simulation["fusion"]
    axis = fusion["axis"]
    expected = simulation["expected_chain"]["xyz"]
    physical = simulation["chain"]
    fig = go.Figure()
    fig.add_trace(go.Heatmap(x=axis, y=axis, z=fusion["fused_map"], colorscale="Viridis", zmin=0.0, zmax=1.0, colorbar=dict(title="Fused P"), name="Fused confidence"))
    fig.add_trace(go.Scatter(x=expected[:, 0], y=expected[:, 1], mode="lines", line=dict(width=2, dash="dash"), name="Configured expected corridor"))
    fig.add_trace(go.Scatter(x=physical["xyz"][physical["physical"], 0], y=physical["xyz"][physical["physical"], 1], mode="lines", line=dict(width=3), name="Simulated physical chain"))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=18), name="CALM buoy"))
    extent = cfg.anchor_radius_m + 12.0
    fig.update_layout(title="Fused chain-confidence layer", xaxis_title="Easting (m)", yaxis_title="Northing (m)", yaxis=dict(scaleanchor="x", scaleratio=1), xaxis_range=[-extent, extent], yaxis_range=[-extent, extent], height=650, margin=dict(l=20, r=20, t=55, b=20))
    return fig


def make_twin_figure(cfg: MissionConfig, simulation: dict[str, Any], show_truth: bool) -> Any:
    go, _ = _plotly_imports()
    fig = go.Figure()
    seabed = simulation["seabed"]
    fig.add_trace(go.Surface(x=seabed["x"], y=seabed["y"], z=seabed["z"], opacity=0.40, colorscale="Earth", showscale=False, name="Seabed"))
    for key, name, symbol in [("mbes", "MBES evidence", "circle"), ("gemini", "Gemini evidence", "diamond")]:
        data = simulation[key]
        fig.add_trace(go.Scatter3d(x=data["xyz"][:, 0], y=data["xyz"][:, 1], z=data["xyz"][:, 2], mode="markers", marker=dict(size=3.4, color=data["probability"], colorscale="Viridis", cmin=0.0, cmax=1.0, symbol=symbol, showscale=key == "gemini", colorbar=dict(title="Evidence P") if key == "gemini" else None), name=name))
    if show_truth:
        expected = simulation["expected_chain"]["xyz"]
        fig.add_trace(go.Scatter3d(x=expected[:, 0], y=expected[:, 1], z=expected[:, 2], mode="lines", line=dict(width=5, dash="dash"), name="Configured expected chain"))
    theta = np.linspace(0, 2 * np.pi, 40)
    z = np.linspace(-cfg.buoy_draft_m, 1.5, 8)
    tt, zz = np.meshgrid(theta, z)
    bx = cfg.buoy_radius_m * np.cos(tt)
    by = cfg.buoy_radius_m * np.sin(tt)
    fig.add_trace(go.Surface(x=bx, y=by, z=zz, opacity=0.62, showscale=False, colorscale=[[0, "#d69e2e"], [1, "#f6e05e"]], name="CALM buoy"))
    fig.update_layout(title="3D evidence twin - raw-source identity retained", scene=dict(xaxis_title="E (m)", yaxis_title="N (m)", zaxis_title="Elevation (m)", aspectmode="data"), height=720, margin=dict(l=0, r=0, t=55, b=0))
    return fig


def run_app() -> None:
    try:
        import streamlit as st
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Streamlit and Pillow are required. Install with: python -m pip install streamlit pillow") from exc

    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(f"{APP_VERSION} | SIMULATED / CONFIGURED EXAMPLE - NOT FIELD RELEASE OR CERTIFICATION")

    with st.sidebar:
        st.header("Drawing and mission")
        field_release_mode = st.toggle("Field-release gate mode", value=False, help="When enabled, G1 is HOLD until the approved drawing/datum is confirmed.")
        drawing_file = st.file_uploader("Approved CALM buoy plan (PNG/JPEG)", type=["png", "jpg", "jpeg"])
        drawing_basis_valid = st.checkbox("Drawing revision, scale, north and datum independently verified", value=False)
        drawing_opacity = st.slider("Drawing overlay opacity", 0.05, 0.80, 0.32, 0.01)
        scenario = st.selectbox("Synthetic chain scenario", SCENARIOS, index=2)
        suspect_bearing = st.slider("Suspected chain bearing (deg true)", 0.0, 359.0, 225.0, 1.0)
        chain_count = st.slider("Configured chain count", 3, 12, 6, 1)
        water_depth = st.slider("Water depth (m)", 8.0, 50.0, 22.0, 0.5)
        anchor_radius = st.slider("Anchor radius from buoy (m)", 60.0, 220.0, 110.0, 5.0)

        st.header("Vessel and USV")
        vessel_standoff = st.slider("Support-vessel stand-off (m)", 40.0, 220.0, 125.0, 5.0)
        usv_clearance = st.slider("Closest USV buoy clearance (m)", 12.0, 60.0, 28.0, 1.0)
        cross_track = st.slider("USV line offset from chain (m)", 5.0, 25.0, 13.0, 1.0)
        gemini_side = st.radio("Gemini mount side", ["Starboard", "Port"], horizontal=True)

        st.header("Acoustic geometry")
        mbes_half_swath = st.slider("MBES half-swath angle (configured deg)", 35.0, 75.0, 65.0, 1.0)
        gemini_range = st.slider("Gemini range (configured m)", 15.0, 80.0, 45.0, 1.0)
        gemini_half_angle = st.slider("Gemini half fan angle (deg)", 25.0, 65.0, 55.0, 1.0)
        gemini_tilt = st.slider("Gemini downward cant (deg)", 0.0, 40.0, 18.0, 1.0)

        st.header("Readiness inputs")
        gnss_imu_valid = st.checkbox("GNSS/IMU common frame valid", True)
        offsets_valid = st.checkbox("Surveyed sensor offsets valid", True)
        mbes_mount_valid = st.checkbox("MBES centreline mount below turbulent waterline", True)
        gemini_mount_valid = st.checkbox("Gemini lateral mount below turbulent waterline", True)
        sound_velocity_valid = st.checkbox("Sound-velocity record valid", True)
        time_sync_ms = st.slider("Inter-sensor time difference (ms)", 0, 180, 20, 5)
        svp_age_h = st.slider("SVP age (h)", 0.0, 10.0, 1.0, 0.25)
        current_mps = st.slider("Surface current (m/s)", 0.0, 1.4, 0.40, 0.05)
        mbes_online = st.checkbox("MBES online and recording", True)
        gemini_online = st.checkbox("Gemini online and recording", True)

    cfg = MissionConfig(
        scenario=scenario,
        water_depth_m=water_depth,
        anchor_radius_m=anchor_radius,
        chain_count=chain_count,
        suspect_bearing_deg=suspect_bearing,
        vessel_standoff_m=vessel_standoff,
        usv_buoy_clearance_m=usv_clearance,
        usv_cross_track_m=cross_track,
        gemini_side=gemini_side,
        gemini_range_m=gemini_range,
        gemini_half_angle_deg=gemini_half_angle,
        gemini_down_tilt_deg=gemini_tilt,
        mbes_half_swath_deg=mbes_half_swath,
    )
    simulation = simulate_mission(cfg)
    controls = {
        "field_release_mode": field_release_mode,
        "approved_drawing_valid": bool(drawing_file is not None and drawing_basis_valid),
        "simops_approved": True,
        "launch_corridor_clear": True,
        "gnss_imu_valid": gnss_imu_valid,
        "offsets_valid": offsets_valid,
        "mbes_mount_valid": mbes_mount_valid,
        "gemini_mount_valid": gemini_mount_valid,
        "sound_velocity_valid": sound_velocity_valid,
        "time_sync_ms": float(time_sync_ms),
        "svp_age_h": float(svp_age_h),
        "usv_ready": True,
        "command_link_valid": True,
        "recovery_ready": True,
        "surface_current_mps": float(current_mps),
        "mbes_online": mbes_online,
        "gemini_online": gemini_online,
        "raw_data_indexed": True,
        "qc_log_complete": True,
        "provenance_complete": True,
        "two_copies_verified": True,
        "evidence_records": 7,
    }
    gates = evaluate_gates(cfg, simulation, controls)
    status = overall_status(gates)

    status_col, coverage_col, residual_col, finding_col = st.columns([1, 1, 1, 2])
    status_col.metric("MRSIF release", status)
    coverage_col.metric("Fused corridor coverage", f"{simulation['fusion']['coverage_pct']:.1f}%")
    residual_col.metric("Source co-registration", f"{simulation['fusion']['coreg_rmse_m']:.2f} m")
    finding_col.metric("Acoustic interpretation", simulation["classification"])

    st.info(
        "Mounting rule: the USV remains a surface vehicle. Mount the NORBIT wet end on the surveyed hull centreline, "
        "nadir-looking below the aerated boundary layer. Mount the Gemini laterally on the inboard side of the survey "
        "line, also below the turbulent waterline, with a controlled downward cant. Both heads, GNSS/IMU and time "
        "source must share one measured reference frame. Confirm acoustic interference and ping scheduling during trials."
    )
    if drawing_file is None:
        st.warning("The original client drawing is not available in this session. The plan below is a configurable schematic and G1 remains qualified/HOLD according to the selected mode.")

    drawing_image = None
    if drawing_file is not None:
        drawing_image = Image.open(drawing_file).convert("RGBA")

    tabs = st.tabs(["Mission geometry", "MBES point cloud", "Gemini image", "Fusion confidence", "3D evidence twin", "MRSIF gates", "Execution plan"])
    with tabs[0]:
        st.plotly_chart(make_plan_figure(cfg, simulation, drawing_image, drawing_opacity), use_container_width=True)
        st.caption("The offset radial pass places the suspected chain on the Gemini-facing side; the inner orbit looks beneath the buoy while the MBES provides seabed and chain-relief context.")
    with tabs[1]:
        show_truth_mbes = st.checkbox("Show configured expected corridor on MBES view", True, key="truth_mbes")
        st.plotly_chart(make_mbes_figure(cfg, simulation, show_truth_mbes), use_container_width=True)
    with tabs[2]:
        st.plotly_chart(make_gemini_figure(simulation), use_container_width=True)
        st.caption("Bright segmented responses represent synthetic chain/link echoes; a weak or absent run is evidence of a gap only after coverage and co-registration gates pass.")
    with tabs[3]:
        st.plotly_chart(make_fusion_figure(cfg, simulation), use_container_width=True)
        st.write({
            "mean_fused_confidence": round(simulation["fusion"]["mean_confidence"], 3),
            "longest_confidence_gap_pct": round(simulation["fusion"]["longest_gap_pct"], 2),
            "matched_source_pairs": simulation["fusion"]["overlap_pairs"],
        })
    with tabs[4]:
        show_truth_twin = st.checkbox("Show configured expected chain in twin", True, key="truth_twin")
        st.plotly_chart(make_twin_figure(cfg, simulation, show_truth_twin), use_container_width=True)
    with tabs[5]:
        st.dataframe([asdict(gate) for gate in gates], use_container_width=True, hide_index=True)
        report = evidence_report(cfg, simulation, controls, gates)
        st.download_button("Download MRSIF evidence JSON", data=json.dumps(report, indent=2), file_name="mrsif_calm_buoy_fusion_evidence.json", mime="application/json")
    with tabs[6]:
        st.markdown(
            """
            1. Confirm the approved CALM buoy drawing, suspected chain ID, datum, chain bearings, buoy excursion and safe exclusion boundary.
            2. Position the client vessel on the safer approved side. Complete bridge interface, SIMOPS release, launch corridor and recovery plan.
            3. Install and survey the common sensor frame: GNSS/IMU, centreline MBES and lateral Gemini. Verify offsets, time, SVP and acoustic interference.
            4. Deploy the USV and acquire the outer reconnaissance/radial passes first. Use MBES to build the seabed and mooring-corridor context.
            5. Run the offset chain-parallel pass with the Gemini facing the chain. Add the inner orbit only after the geofence and stand-off review.
            6. Preserve both raw sources. Transform them through the common frame, calculate co-registration residuals and build the fused confidence layer.
            7. Classify only observed evidence: suspended, seabed contact, displaced, apparent discontinuity/termination or inconclusive. Route confidence gaps for targeted reacquisition or positioned ROV verification.
            8. Close out with raw indexes, configuration/offset record, QC, target register, fused twin, limitations and two verified data copies.
            """
        )


def self_test() -> None:
    baseline_cfg = MissionConfig(scenario="Intact / localised")
    baseline_sim = simulate_mission(baseline_cfg)
    assert len(baseline_sim["mbes"]["xyz"]) > 80
    assert len(baseline_sim["gemini"]["xyz"]) > 60
    assert baseline_sim["fusion"]["overlap_pairs"] > 20
    assert math.isfinite(baseline_sim["fusion"]["coreg_rmse_m"])

    controls = {
        "field_release_mode": True,
        "approved_drawing_valid": True,
        "simops_approved": True,
        "launch_corridor_clear": True,
        "gnss_imu_valid": True,
        "offsets_valid": True,
        "mbes_mount_valid": True,
        "gemini_mount_valid": True,
        "sound_velocity_valid": True,
        "time_sync_ms": 20.0,
        "svp_age_h": 1.0,
        "usv_ready": True,
        "command_link_valid": True,
        "recovery_ready": True,
        "surface_current_mps": 0.40,
        "mbes_online": True,
        "gemini_online": True,
        "raw_data_indexed": True,
        "qc_log_complete": True,
        "provenance_complete": True,
        "two_copies_verified": True,
        "evidence_records": 7,
    }
    gates = evaluate_gates(baseline_cfg, baseline_sim, controls)
    assert len(gates) == 8
    assert all(gate.code == f"G{index}" for index, gate in enumerate(gates, start=1))
    assert gates[0].status == "GO"

    broken_reference = dict(controls)
    broken_reference["offsets_valid"] = False
    assert evaluate_gates(baseline_cfg, baseline_sim, broken_reference)[2].status == "HOLD"

    unsafe_cfg = MissionConfig(vessel_standoff_m=55.0)
    unsafe_sim = simulate_mission(unsafe_cfg)
    assert evaluate_gates(unsafe_cfg, unsafe_sim, controls)[1].status == "HOLD"

    gap_cfg = MissionConfig(scenario="Apparent discontinuity")
    gap_sim = simulate_mission(gap_cfg)
    assert "discontinuity" in gap_sim["classification"].lower() or "termination" in gap_sim["classification"].lower()

    termination_cfg = MissionConfig(scenario="Terminated / free-end pattern")
    termination_sim = simulate_mission(termination_cfg)
    assert "termination" in termination_sim["classification"].lower() or "discontinuity" in termination_sim["classification"].lower()

    report = evidence_report(baseline_cfg, baseline_sim, controls, gates)
    json.dumps(report)
    assert report["gates"][0]["code"] == "G1"

    # Exercise Plotly constructors when the optional UI dependency is present.
    # This catches strict-property-validation changes such as numpy.bool_ being
    # rejected for Boolean trace properties on newer Streamlit Cloud images.
    try:
        import plotly  # noqa: F401
    except ImportError:
        plotly = None
    if plotly is not None:
        figures = [
            make_plan_figure(baseline_cfg, baseline_sim),
            make_mbes_figure(baseline_cfg, baseline_sim, show_truth=True),
            make_gemini_figure(baseline_sim),
            make_fusion_figure(baseline_cfg, baseline_sim),
            make_twin_figure(baseline_cfg, baseline_sim, show_truth=True),
        ]
        for figure in figures:
            payload = figure.to_plotly_json()
            assert payload["data"]
            for trace in payload["data"]:
                if "showlegend" in trace:
                    assert isinstance(trace["showlegend"], bool)
    print("PASS: geometry, dual-sonar simulation, fusion, classification, G1-G8 gates and JSON evidence report")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        run_app()
