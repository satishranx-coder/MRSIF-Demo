"""MRSIF Paradip ROV-USV chain inspection assurance demonstration.

Run the logic regression checks without Streamlit:
    python paradip_chain_mrsif_demo.py --self-test

Run the interactive demonstration:
    python -m pip install streamlit
    streamlit run paradip_chain_mrsif_demo.py

Assurance boundary
------------------
This application is an offline-capable planning and decision-discipline
demonstration. All scenarios, thresholds, weather values and inspection results
are simulated or configured examples. The application does not control marine
equipment, replace the Harbour Master, IMD/INCOIS advisories, an approved risk
assessment, OEM operating limits, engineering judgement or client acceptance.
It is not a compliance certificate or a prediction of future conditions.
"""

from __future__ import annotations

import copy
import html
import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


APP_TITLE = "MRSIF | Paradip Chain Inspection"
APP_VERSION = "Demonstration Release 1.0"


GATE_SEQUENCE: list[dict[str, str]] = [
    {
        "code": "G1",
        "name": "Scope, asset and port readiness",
        "phase": "Plan",
        "purpose": "Confirm the inspection basis, asset identity, permits, SIMOPS and exclusion controls.",
    },
    {
        "code": "G2",
        "name": "Weather, sea state and tide window",
        "phase": "Plan",
        "purpose": "Release mobilisation only when official warnings are clear and the forecast window is inside configured limits.",
    },
    {
        "code": "G3",
        "name": "USV reconnaissance readiness",
        "phase": "Acquire",
        "purpose": "Validate USV command, navigation, payload, geofence and common frame before acquiring reference data.",
    },
    {
        "code": "G4",
        "name": "ROV and launch system readiness",
        "phase": "Acquire",
        "purpose": "Confirm ROV pre-dive, LARS, tether management and emergency recovery controls.",
    },
    {
        "code": "G5",
        "name": "Positioning and environmental reference",
        "phase": "Acquire",
        "purpose": "Validate coordinate frame, time sync, acoustic positioning, sound velocity and current evidence.",
    },
    {
        "code": "G6",
        "name": "Chain localisation and approach",
        "phase": "Execute",
        "purpose": "Use sonar-led localisation and controlled approach without treating poor optical visibility as confirmed visual evidence.",
    },
    {
        "code": "G7",
        "name": "Detailed chain inspection",
        "phase": "Execute",
        "purpose": "Verify inspection coverage, video quality, measurement validity and anomaly disposition.",
    },
    {
        "code": "G8",
        "name": "Evidence and closeout",
        "phase": "Deliver",
        "purpose": "Release the report only when traceable records, media indexes, positioning and backups are complete.",
    },
]


# Configured demonstration limits only. A real job must load the approved
# equipment limits and project acceptance criteria.
DEMO_LIMITS: dict[str, float] = {
    "weather_window_hold_h": 6.0,
    "weather_window_watch_h": 9.0,
    "hs_watch_m": 0.80,
    "hs_hold_m": 1.20,
    "wind_watch_kn": 15.0,
    "wind_hold_kn": 18.0,
    "gust_hold_kn": 25.0,
    "surface_current_watch_mps": 0.60,
    "surface_current_hold_mps": 0.90,
    "rain_free_watch_h": 48.0,
    "battery_watch_pct": 60.0,
    "position_uncertainty_watch_m": 0.50,
    "position_uncertainty_hold_m": 1.00,
    "svp_age_watch_h": 3.0,
    "svp_age_hold_h": 6.0,
    "visibility_watch_m": 0.75,
    "visibility_hold_visual_m": 0.25,
    "coverage_watch_pct": 95.0,
    "coverage_hold_pct": 90.0,
}


BASE_DATA: dict[str, Any] = {
    "campaign_label": "Configured chain inspection example",
    "season": "February-March dry-season planning window",
    "tide_basis": "Neap-tide block; work around locally verified slack water",
    "asset_register_valid": True,
    "inspection_scope_approved": True,
    "port_clearance": True,
    "simops_approved": True,
    "exclusion_zone_approved": True,
    "imd_warning_clear": True,
    "incois_warning_clear": True,
    "port_signal_clear": True,
    "lightning_clear": True,
    "weather_window_h": 12.0,
    "significant_wave_height_m": 0.55,
    "wind_kn": 10.0,
    "gust_kn": 14.0,
    "surface_current_mps": 0.42,
    "rain_free_h": 84.0,
    "usv_prelaunch_pass": True,
    "usv_command_link_valid": True,
    "usv_gnss_valid": True,
    "usv_geofence_valid": True,
    "usv_collision_control_valid": True,
    "usv_payload_valid": True,
    "usv_battery_pct": 86.0,
    "rov_pre_dive_pass": True,
    "lars_valid": True,
    "tether_management_approved": True,
    "emergency_recovery_ready": True,
    "frame_valid": True,
    "time_sync_valid": True,
    "acoustic_positioning_valid": True,
    "position_uncertainty_m": 0.24,
    "sound_velocity_valid": True,
    "svp_age_h": 1.2,
    "current_profile_valid": True,
    "imaging_sonar_online": True,
    "chain_detected": True,
    "controlled_approach_valid": True,
    "visibility_m": 1.10,
    "visual_confirmation_required": True,
    "video_recording_valid": True,
    "laser_scaler_valid": True,
    "measurement_scope_included": True,
    "measurement_tools_valid": True,
    "inspection_coverage_pct": 98.6,
    "connections_observed": True,
    "critical_anomaly": False,
    "engineering_disposition_available": True,
    "evidence_records": 7,
    "video_index_complete": True,
    "position_log_complete": True,
    "defect_register_complete": True,
    "two_copies_verified": True,
    "chain_bearing_deg": 32.0,
    "water_depth_m": 18.0,
    "chain_length_inspected_m": 145.0,
}


SCENARIOS: dict[str, dict[str, Any]] = {
    "Preferred dry-season window (Feb-Mar)": {},
    "Conditional September neap window": {
        "campaign_label": "Tentative 19-23 September forecast-selected window",
        "season": "Southwest monsoon transition - conditional window",
        "weather_window_h": 8.0,
        "significant_wave_height_m": 0.86,
        "wind_kn": 14.5,
        "gust_kn": 21.0,
        "surface_current_mps": 0.64,
        "rain_free_h": 54.0,
        "usv_battery_pct": 69.0,
        "position_uncertainty_m": 0.42,
        "svp_age_h": 2.7,
        "visibility_m": 0.45,
        "inspection_coverage_pct": 96.2,
        "chain_bearing_deg": 58.0,
    },
    "Monsoon low-pressure disturbance": {
        "campaign_label": "Disturbed-weather hold example",
        "season": "Active southwest monsoon / low-pressure system",
        "imd_warning_clear": False,
        "incois_warning_clear": False,
        "port_signal_clear": False,
        "lightning_clear": False,
        "weather_window_h": 2.0,
        "significant_wave_height_m": 2.40,
        "wind_kn": 28.0,
        "gust_kn": 38.0,
        "surface_current_mps": 0.98,
        "rain_free_h": 4.0,
        "visibility_m": 0.12,
        "inspection_coverage_pct": 72.0,
        "connections_observed": False,
        "evidence_records": 2,
    },
    "Poor optical visibility / sonar available": {
        "campaign_label": "Sonar localisation with visual-evidence limitation",
        "visibility_m": 0.18,
        "inspection_coverage_pct": 91.0,
        "connections_observed": False,
    },
    "Positioning frame or clock invalid": {
        "campaign_label": "Common reference invalid",
        "time_sync_valid": False,
        "position_uncertainty_m": 1.35,
    },
    "USV command-link degradation": {
        "campaign_label": "USV link-loss contingency",
        "usv_command_link_valid": False,
    },
    "ROV tether entanglement risk": {
        "campaign_label": "Tether route not accepted",
        "tether_management_approved": False,
        "controlled_approach_valid": False,
    },
    "Critical chain anomaly identified": {
        "campaign_label": "Inspection complete; engineering disposition required",
        "critical_anomaly": True,
        "engineering_disposition_available": False,
        "inspection_coverage_pct": 97.0,
    },
    "Closeout evidence gap": {
        "campaign_label": "Acquisition complete; deliverable hold",
        "evidence_records": 5,
        "video_index_complete": False,
        "two_copies_verified": False,
    },
}


@dataclass(frozen=True)
class GateResult:
    code: str
    name: str
    phase: str
    status: str
    detail: str
    evidence: tuple[str, ...]
    action: str


def scenario_data(name: str) -> dict[str, Any]:
    """Return an independent scenario dictionary."""
    if name not in SCENARIOS:
        raise KeyError(f"Unknown scenario: {name}")
    data = copy.deepcopy(BASE_DATA)
    data.update(copy.deepcopy(SCENARIOS[name]))
    data["scenario_name"] = name
    return data


def _result(
    index: int,
    status: str,
    detail: str,
    evidence: Iterable[str],
    action: str,
) -> GateResult:
    meta = GATE_SEQUENCE[index]
    return GateResult(
        code=meta["code"],
        name=meta["name"],
        phase=meta["phase"],
        status=status,
        detail=detail,
        evidence=tuple(evidence),
        action=action,
    )


def _state_rank(status: str) -> int:
    return {"GO": 0, "WATCH": 1, "HOLD": 2}.get(status, 2)


def overall_state(gates: Iterable[GateResult]) -> str:
    states = [g.status for g in gates]
    return max(states, key=_state_rank) if states else "HOLD"


def evaluate_gates(data: dict[str, Any]) -> list[GateResult]:
    """Evaluate the eight MRSIF assurance gates.

    The dependency checks are deliberately repeated where required. This avoids
    a later phase appearing to be released when its coordinate, time, weather or
    equipment prerequisite is invalid.
    """
    gates: list[GateResult] = []

    # G1 - scope and port readiness
    g1_checks = {
        "Asset register": bool(data["asset_register_valid"]),
        "Approved inspection scope": bool(data["inspection_scope_approved"]),
        "Port clearance": bool(data["port_clearance"]),
        "SIMOPS plan": bool(data["simops_approved"]),
        "Exclusion zone": bool(data["exclusion_zone_approved"]),
    }
    g1_failed = [label for label, valid in g1_checks.items() if not valid]
    if g1_failed:
        gates.append(_result(0, "HOLD", f"Missing prerequisite: {', '.join(g1_failed)}.", g1_checks, "Close the scope or port-control gap before mobilisation."))
    else:
        gates.append(_result(0, "GO", "Scope, asset reference and port-control prerequisites are configured as accepted.", g1_checks, "Proceed to the forecast and tide release gate."))

    # G2 - weather, tide and official warning status
    official_clear = bool(data["imd_warning_clear"] and data["incois_warning_clear"] and data["port_signal_clear"])
    weather_hold_reasons: list[str] = []
    if not official_clear:
        weather_hold_reasons.append("official marine or port warning is active")
    if not data["lightning_clear"]:
        weather_hold_reasons.append("lightning/squall condition is not clear")
    if data["weather_window_h"] < DEMO_LIMITS["weather_window_hold_h"]:
        weather_hold_reasons.append(f"usable window {data['weather_window_h']:.1f} h is too short")
    if data["significant_wave_height_m"] > DEMO_LIMITS["hs_hold_m"]:
        weather_hold_reasons.append(f"Hs {data['significant_wave_height_m']:.2f} m exceeds configured hold limit")
    if data["wind_kn"] > DEMO_LIMITS["wind_hold_kn"] or data["gust_kn"] > DEMO_LIMITS["gust_hold_kn"]:
        weather_hold_reasons.append(f"wind/gust {data['wind_kn']:.1f}/{data['gust_kn']:.1f} kn exceeds configured limit")
    if data["surface_current_mps"] > DEMO_LIMITS["surface_current_hold_mps"]:
        weather_hold_reasons.append(f"surface current {data['surface_current_mps']:.2f} m/s exceeds configured hold limit")

    weather_evidence = (
        f"Warnings clear: {'yes' if official_clear else 'no'}",
        f"Forecast window: {data['weather_window_h']:.1f} h",
        f"Hs: {data['significant_wave_height_m']:.2f} m",
        f"Wind/gust: {data['wind_kn']:.1f}/{data['gust_kn']:.1f} kn",
        f"Surface current: {data['surface_current_mps']:.2f} m/s",
        f"Rain-free settling: {data['rain_free_h']:.0f} h",
        str(data["tide_basis"]),
    )
    if weather_hold_reasons:
        gates.append(_result(1, "HOLD", "; ".join(weather_hold_reasons).capitalize() + ".", weather_evidence, "Do not launch. Reassess after official advisories clear and a new forecast window is accepted."))
    else:
        watch_reasons: list[str] = []
        if data["weather_window_h"] < DEMO_LIMITS["weather_window_watch_h"]:
            watch_reasons.append("limited forecast window")
        if data["significant_wave_height_m"] > DEMO_LIMITS["hs_watch_m"]:
            watch_reasons.append("wave height near the conservative planning boundary")
        if data["wind_kn"] > DEMO_LIMITS["wind_watch_kn"]:
            watch_reasons.append("wind near the planning boundary")
        if data["surface_current_mps"] > DEMO_LIMITS["surface_current_watch_mps"]:
            watch_reasons.append("current near the planning boundary")
        if data["rain_free_h"] < DEMO_LIMITS["rain_free_watch_h"]:
            watch_reasons.append("insufficient post-rain settling time")
        if watch_reasons:
            gates.append(_result(1, "WATCH", "; ".join(watch_reasons).capitalize() + ".", weather_evidence, "Use a restricted window, continuous monitoring and a defined abort trigger."))
        else:
            gates.append(_result(1, "GO", "Official warnings are clear and the configured forecast window is inside the demonstration limits.", weather_evidence, "Release mobilisation subject to the final D-1 and day-of-operation checks."))

    # G3 - USV readiness, including common reference prerequisites
    g3_checks = {
        "USV pre-launch": bool(data["usv_prelaunch_pass"]),
        "Command link": bool(data["usv_command_link_valid"]),
        "GNSS": bool(data["usv_gnss_valid"]),
        "Geofence": bool(data["usv_geofence_valid"]),
        "Collision controls": bool(data["usv_collision_control_valid"]),
        "Survey payload": bool(data["usv_payload_valid"]),
        "Coordinate frame": bool(data["frame_valid"]),
        "Time sync": bool(data["time_sync_valid"]),
    }
    g3_failed = [label for label, valid in g3_checks.items() if not valid]
    if g3_failed:
        gates.append(_result(2, "HOLD", f"USV prerequisite invalid: {', '.join(g3_failed)}.", (*g3_checks.keys(), f"Battery: {data['usv_battery_pct']:.0f}%"), "Recover or retain the USV safe state; restore the failed prerequisite and repeat the pre-launch checklist."))
    elif data["usv_battery_pct"] < DEMO_LIMITS["battery_watch_pct"]:
        gates.append(_result(2, "WATCH", f"USV battery {data['usv_battery_pct']:.0f}% provides limited mission reserve.", (*g3_checks.keys(), f"Battery: {data['usv_battery_pct']:.0f}%"), "Shorten the reconnaissance plan or recharge before launch."))
    else:
        gates.append(_result(2, "GO", "USV command, navigation, payload and common-reference checks are accepted.", (*g3_checks.keys(), f"Battery: {data['usv_battery_pct']:.0f}%"), "Run the approved reconnaissance lines and current observations."))

    # G4 - ROV and launch system
    g4_checks = {
        "ROV pre-dive": bool(data["rov_pre_dive_pass"]),
        "LARS": bool(data["lars_valid"]),
        "Tether plan": bool(data["tether_management_approved"]),
        "Emergency recovery": bool(data["emergency_recovery_ready"]),
    }
    g4_failed = [label for label, valid in g4_checks.items() if not valid]
    if g4_failed:
        gates.append(_result(3, "HOLD", f"ROV/LARS prerequisite invalid: {', '.join(g4_failed)}.", g4_checks, "Do not deploy the ROV until the failed control is accepted."))
    else:
        gates.append(_result(3, "GO", "ROV, launch/recovery, tether and contingency controls are configured as ready.", g4_checks, "Proceed to the environmental and positioning reference gate."))

    # G5 - positioning and environmental reference
    g5_hold: list[str] = []
    if not data["frame_valid"]:
        g5_hold.append("coordinate frame invalid")
    if not data["time_sync_valid"]:
        g5_hold.append("time synchronisation invalid")
    if not data["acoustic_positioning_valid"]:
        g5_hold.append("acoustic positioning invalid")
    if data["position_uncertainty_m"] > DEMO_LIMITS["position_uncertainty_hold_m"]:
        g5_hold.append(f"position uncertainty {data['position_uncertainty_m']:.2f} m exceeds limit")
    if not data["sound_velocity_valid"] or data["svp_age_h"] > DEMO_LIMITS["svp_age_hold_h"]:
        g5_hold.append("sound-velocity reference invalid or stale")
    if not data["current_profile_valid"]:
        g5_hold.append("current profile unavailable")
    g5_evidence = (
        f"Frame valid: {'yes' if data['frame_valid'] else 'no'}",
        f"Time sync valid: {'yes' if data['time_sync_valid'] else 'no'}",
        f"Position uncertainty: {data['position_uncertainty_m']:.2f} m",
        f"SVP valid/age: {'yes' if data['sound_velocity_valid'] else 'no'} / {data['svp_age_h']:.1f} h",
        f"Current profile: {'valid' if data['current_profile_valid'] else 'invalid'}",
    )
    if g5_hold:
        gates.append(_result(4, "HOLD", "; ".join(g5_hold).capitalize() + ".", g5_evidence, "Re-establish the common reference before combining USV, acoustic and ROV evidence."))
    elif data["position_uncertainty_m"] > DEMO_LIMITS["position_uncertainty_watch_m"] or data["svp_age_h"] > DEMO_LIMITS["svp_age_watch_h"]:
        gates.append(_result(4, "WATCH", "Reference quality is valid but near the configured watch boundary.", g5_evidence, "Refresh the reference or apply the approved restricted-use condition."))
    else:
        gates.append(_result(4, "GO", "Positioning, frame, clock, sound velocity and current references are accepted.", g5_evidence, "Release sonar-led chain localisation."))

    # G6 - localisation, explicitly dependent on G5
    reference_valid = gates[4].status != "HOLD"
    g6_hold: list[str] = []
    if not reference_valid:
        g6_hold.append("positioning/environmental reference not released")
    if not data["imaging_sonar_online"]:
        g6_hold.append("imaging sonar unavailable")
    if not data["chain_detected"]:
        g6_hold.append("chain not positively localised")
    if not data["controlled_approach_valid"]:
        g6_hold.append("controlled approach or tether route invalid")
    g6_evidence = (
        f"Imaging sonar: {'online' if data['imaging_sonar_online'] else 'offline'}",
        f"Chain detected: {'yes' if data['chain_detected'] else 'no'}",
        f"Controlled approach: {'valid' if data['controlled_approach_valid'] else 'invalid'}",
        f"Estimated optical visibility: {data['visibility_m']:.2f} m",
        f"Chain bearing example: {data['chain_bearing_deg']:.0f} deg",
    )
    if g6_hold:
        gates.append(_result(5, "HOLD", "; ".join(g6_hold).capitalize() + ".", g6_evidence, "Stop the approach, regain reference or sonar coverage, and re-plan the tether route."))
    elif data["visibility_m"] < DEMO_LIMITS["visibility_watch_m"]:
        gates.append(_result(5, "WATCH", "Sonar supports localisation, but optical visibility is below the configured watch level.", g6_evidence, "Continue only for sonar-led localisation; do not claim visual condition evidence until imagery is adequate."))
    else:
        gates.append(_result(5, "GO", "Sonar localisation, positioning and controlled approach evidence are accepted.", g6_evidence, "Commence the approved chain-by-chain inspection route."))

    # G7 - detailed inspection, dependent on localisation and visual scope
    g7_hold: list[str] = []
    if gates[5].status == "HOLD":
        g7_hold.append("localisation/approach gate not released")
    if data["visual_confirmation_required"] and data["visibility_m"] < DEMO_LIMITS["visibility_hold_visual_m"]:
        g7_hold.append("visibility is inadequate for the required visual confirmation")
    if not data["video_recording_valid"]:
        g7_hold.append("inspection video recording invalid")
    if not data["laser_scaler_valid"]:
        g7_hold.append("laser scale invalid")
    if data["measurement_scope_included"] and not data["measurement_tools_valid"]:
        g7_hold.append("configured measurement tool invalid")
    if data["inspection_coverage_pct"] < DEMO_LIMITS["coverage_hold_pct"]:
        g7_hold.append(f"coverage {data['inspection_coverage_pct']:.1f}% below hold criterion")
    if not data["connections_observed"]:
        g7_hold.append("required connection points not observed")
    if data["critical_anomaly"] and not data["engineering_disposition_available"]:
        g7_hold.append("critical anomaly awaits engineering disposition")
    g7_evidence = (
        f"Coverage: {data['inspection_coverage_pct']:.1f}%",
        f"Video: {'valid' if data['video_recording_valid'] else 'invalid'}",
        f"Laser scale: {'valid' if data['laser_scaler_valid'] else 'invalid'}",
        f"Connections observed: {'yes' if data['connections_observed'] else 'no'}",
        f"Critical anomaly: {'yes' if data['critical_anomaly'] else 'no'}",
        f"Example length inspected: {data['chain_length_inspected_m']:.0f} m",
    )
    if g7_hold:
        gates.append(_result(6, "HOLD", "; ".join(g7_hold).capitalize() + ".", g7_evidence, "Suspend completion claim; reacquire missing evidence or obtain the required engineering disposition."))
    elif data["inspection_coverage_pct"] < DEMO_LIMITS["coverage_watch_pct"] or data["visibility_m"] < DEMO_LIMITS["visibility_watch_m"]:
        gates.append(_result(6, "WATCH", "Inspection evidence is usable with a documented visibility or coverage limitation.", g7_evidence, "Record the limitation and obtain client acceptance before closeout."))
    else:
        gates.append(_result(6, "GO", "Configured coverage, recording, scaling and connection-point evidence are accepted.", g7_evidence, "Compile the traceable inspection evidence package."))

    # G8 - dynamic prior-phase evidence requirement
    required_records = len(GATE_SEQUENCE) - 1
    g8_hold: list[str] = []
    if data["evidence_records"] < required_records:
        g8_hold.append(f"only {data['evidence_records']}/{required_records} prior-gate records are logged")
    if not data["video_index_complete"]:
        g8_hold.append("video index incomplete")
    if not data["position_log_complete"]:
        g8_hold.append("position log incomplete")
    if not data["defect_register_complete"]:
        g8_hold.append("defect register incomplete")
    if not data["two_copies_verified"]:
        g8_hold.append("two verified data copies not confirmed")
    g8_evidence = (
        f"Prior-gate records: {data['evidence_records']}/{required_records}",
        f"Video index: {'complete' if data['video_index_complete'] else 'incomplete'}",
        f"Position log: {'complete' if data['position_log_complete'] else 'incomplete'}",
        f"Defect register: {'complete' if data['defect_register_complete'] else 'incomplete'}",
        f"Two copies: {'verified' if data['two_copies_verified'] else 'not verified'}",
    )
    prior_holds = [gate.code for gate in gates[:7] if gate.status == "HOLD"]
    prior_watches = [gate.code for gate in gates[:7] if gate.status == "WATCH"]
    if g8_hold:
        gates.append(_result(7, "HOLD", "; ".join(g8_hold).capitalize() + ".", g8_evidence, "Complete and verify the evidence package before report release."))
    elif prior_holds:
        gates.append(_result(7, "HOLD", f"Closeout blocked by unresolved hold gates: {', '.join(prior_holds)}.", g8_evidence, "Resolve or formally disposition every hold before issuing the final report."))
    elif prior_watches:
        gates.append(_result(7, "WATCH", f"Evidence package is complete, but limitations remain at {', '.join(prior_watches)}.", g8_evidence, "Record client acceptance of every limitation before final issue."))
    else:
        gates.append(_result(7, "GO", "Traceable records, indexes, logs and verified copies are complete.", g8_evidence, "Release the configured demonstration report for formal review."))

    return gates


def evidence_package(data: dict[str, Any], gates: list[GateResult]) -> dict[str, Any]:
    """Build a downloadable, human-readable JSON evidence snapshot."""
    return {
        "mrsif_demo": APP_TITLE,
        "version": APP_VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "assurance_boundary": "Simulated/configured example; not live control, certification or future-weather prediction.",
        "scenario": data["scenario_name"],
        "campaign_label": data["campaign_label"],
        "overall_state": overall_state(gates),
        "inputs": data,
        "gate_results": [asdict(gate) for gate in gates],
    }


def run_gate_regression_tests() -> dict[str, str]:
    """Run embedded regression tests as a lightweight subroutine."""
    results: dict[str, str] = {}

    nominal = evaluate_gates(scenario_data("Preferred dry-season window (Feb-Mar)"))
    assert [g.status for g in nominal] == ["GO"] * len(GATE_SEQUENCE)
    results["Preferred dry-season scenario"] = "PASS"

    september = evaluate_gates(scenario_data("Conditional September neap window"))
    assert overall_state(september) == "WATCH"
    assert september[1].status == "WATCH"
    assert september[5].status == "WATCH"
    results["Conditional September watch discipline"] = "PASS"

    disturbed = evaluate_gates(scenario_data("Monsoon low-pressure disturbance"))
    assert disturbed[1].status == "HOLD"
    results["Official warning/weather hold"] = "PASS"

    frame_fault = evaluate_gates(scenario_data("Positioning frame or clock invalid"))
    for gate_index in (2, 4, 5, 6, 7):
        assert frame_fault[gate_index].status == "HOLD"
    results["Frame/clock prerequisite propagation"] = "PASS"

    poor_visibility = evaluate_gates(scenario_data("Poor optical visibility / sonar available"))
    assert poor_visibility[5].status == "WATCH"
    assert poor_visibility[6].status == "HOLD"
    results["Sonar does not overclaim visual evidence"] = "PASS"

    critical = evaluate_gates(scenario_data("Critical chain anomaly identified"))
    assert critical[6].status == "HOLD"
    assert "engineering disposition" in critical[6].detail.lower()
    results["Critical anomaly disposition"] = "PASS"

    closeout_data = scenario_data("Preferred dry-season window (Feb-Mar)")
    closeout_data["evidence_records"] = len(GATE_SEQUENCE) - 2
    closeout = evaluate_gates(closeout_data)
    assert closeout[-1].status == "HOLD"
    assert f"/{len(GATE_SEQUENCE) - 1}" in closeout[-1].detail
    results["Dynamic closeout record count"] = "PASS"

    package_text = json.dumps(evidence_package(scenario_data("Preferred dry-season window (Feb-Mar)"), nominal))
    assert "not live control" in package_text.lower()
    assert "compliance certificate: verified" not in package_text.lower()
    results["Assurance-boundary wording"] = "PASS"

    return results


def _status_color(status: str) -> str:
    return {"GO": "#16876f", "WATCH": "#d49a1f", "HOLD": "#c64b47"}.get(status, "#6f7c82")


def _render_scene(data: dict[str, Any], selected_gate: GateResult) -> str:
    """Return a compact inline SVG mission schematic without token substitution."""
    width = 980
    height = 430
    depth = max(1.0, float(data["water_depth_m"]))
    rov_y = min(330.0, 130.0 + depth * 7.5)
    bearing_rad = math.radians(float(data["chain_bearing_deg"]))
    chain_dx = 170.0 * math.cos(bearing_rad)
    chain_end_x = max(610.0, min(920.0, 750.0 + chain_dx))
    status = html.escape(selected_gate.status)
    status_color = _status_color(status)
    gate_label = html.escape(f"{selected_gate.code} | {selected_gate.name}")
    vis = html.escape(f"Estimated visibility {data['visibility_m']:.2f} m")
    current = html.escape(f"Surface current {data['surface_current_mps']:.2f} m/s")
    return f"""
    <svg viewBox="0 0 {width} {height}" role="img" aria-label="Simulated USV and ROV chain inspection schematic" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e6b7a"/><stop offset="1" stop-color="#082d43"/></linearGradient>
        <linearGradient id="bed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8d7453"/><stop offset="1" stop-color="#b19768"/></linearGradient>
        <filter id="soft"><feGaussianBlur stdDeviation="5"/></filter>
      </defs>
      <rect width="980" height="430" fill="#071f2d" rx="10"/>
      <rect y="52" width="980" height="318" fill="url(#water)"/>
      <path d="M0 52 C120 44, 220 61, 340 52 S570 44, 710 53 S870 63, 980 50" fill="none" stroke="#8de0e5" stroke-width="5"/>
      <path d="M0 366 C160 346, 320 374, 470 358 S760 345, 980 365 L980 430 L0 430 Z" fill="url(#bed)"/>
      <path d="M605 352 C670 315, 714 325, 758 357 C805 392, {chain_end_x:.0f} 370, 932 383" fill="none" stroke="#d6d6cf" stroke-width="13" stroke-linecap="round" stroke-dasharray="2 19"/>
      <path d="M605 352 C670 315, 714 325, 758 357 C805 392, {chain_end_x:.0f} 370, 932 383" fill="none" stroke="#3e4548" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 19"/>
      <g transform="translate(185 31)">
        <path d="M0 20 L104 20 L84 43 L18 43 Z" fill="#f3b632" stroke="#eaf7f8" stroke-width="2"/>
        <rect x="34" y="6" width="36" height="16" rx="3" fill="#d8f4f4"/>
        <circle cx="26" cy="46" r="4" fill="#78d6df"/><circle cx="79" cy="46" r="4" fill="#78d6df"/>
        <text x="52" y="2" fill="#ffffff" text-anchor="middle" font-size="12" font-family="Arial" font-weight="700">USV RECONNAISSANCE</text>
      </g>
      <path d="M237 77 C260 150, 352 182, 425 {rov_y:.0f}" fill="none" stroke="#f6c65a" stroke-width="2" stroke-dasharray="7 5"/>
      <g transform="translate(390 {rov_y - 24:.0f})">
        <rect width="72" height="42" rx="9" fill="#24b8c5" stroke="#dff8f8" stroke-width="2"/>
        <circle cx="10" cy="21" r="8" fill="#081f2c"/><circle cx="62" cy="21" r="8" fill="#081f2c"/>
        <path d="M72 20 L108 10 L108 32 Z" fill="#45d5df" fill-opacity="0.35"/>
        <text x="36" y="-8" fill="#ffffff" text-anchor="middle" font-size="12" font-family="Arial" font-weight="700">ROV + IMAGING SONAR</text>
      </g>
      <path d="M498 {rov_y:.0f} L610 350" stroke="#42e2ef" stroke-width="2" stroke-dasharray="6 5"/>
      <circle cx="610" cy="350" r="12" fill="none" stroke="#42e2ef" stroke-width="3"/>
      <text x="654" y="335" fill="#ffffff" font-size="12" font-family="Arial" font-weight="700">MOORING CHAIN</text>
      <text x="654" y="352" fill="#cbe8eb" font-size="11" font-family="Arial">Sonar-led localisation; visual confirmation conditional</text>
      <text x="24" y="88" fill="#cbe8eb" font-size="12" font-family="Arial">{current}</text>
      <text x="24" y="108" fill="#cbe8eb" font-size="12" font-family="Arial">{vis}</text>
      <rect x="22" y="18" width="740" height="24" rx="4" fill="#0b2634"/>
      <text x="34" y="35" fill="#e8f7f8" font-size="13" font-family="Arial" font-weight="700">{gate_label}</text>
      <rect x="856" y="16" width="100" height="30" rx="4" fill="{status_color}"/>
      <text x="906" y="36" fill="#ffffff" font-size="14" font-family="Arial" font-weight="800" text-anchor="middle">{status}</text>
      <text x="24" y="407" fill="#f7e3b0" font-size="11" font-family="Arial">SIMULATED SCHEMATIC - NOT TO SCALE - NOT LIVE EQUIPMENT CONTROL</text>
    </svg>
    """


def _safe_dataframe(st: Any, rows: list[dict[str, Any]]) -> None:
    try:
        st.dataframe(rows, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(rows, use_container_width=True, hide_index=True)


def _manual_inputs(st: Any, data: dict[str, Any]) -> dict[str, Any]:
    st.sidebar.markdown("### Manual sandbox")
    data["significant_wave_height_m"] = st.sidebar.slider("Significant wave height (m)", 0.0, 3.0, float(data["significant_wave_height_m"]), 0.05)
    data["wind_kn"] = st.sidebar.slider("Sustained wind (kn)", 0.0, 40.0, float(data["wind_kn"]), 0.5)
    data["gust_kn"] = st.sidebar.slider("Wind gust (kn)", 0.0, 55.0, float(data["gust_kn"]), 0.5)
    data["surface_current_mps"] = st.sidebar.slider("Surface current (m/s)", 0.0, 1.5, float(data["surface_current_mps"]), 0.02)
    data["visibility_m"] = st.sidebar.slider("Estimated visibility (m)", 0.0, 3.0, float(data["visibility_m"]), 0.05)
    data["weather_window_h"] = st.sidebar.slider("Forecast operating window (h)", 0.0, 24.0, float(data["weather_window_h"]), 0.5)
    data["imd_warning_clear"] = st.sidebar.checkbox("IMD warning clear", bool(data["imd_warning_clear"]))
    data["incois_warning_clear"] = st.sidebar.checkbox("INCOIS warning clear", bool(data["incois_warning_clear"]))
    data["port_signal_clear"] = st.sidebar.checkbox("Port signal clear", bool(data["port_signal_clear"]))
    data["frame_valid"] = st.sidebar.checkbox("Coordinate frame valid", bool(data["frame_valid"]))
    data["time_sync_valid"] = st.sidebar.checkbox("Time sync valid", bool(data["time_sync_valid"]))
    data["imaging_sonar_online"] = st.sidebar.checkbox("Imaging sonar online", bool(data["imaging_sonar_online"]))
    data["tether_management_approved"] = st.sidebar.checkbox("Tether plan approved", bool(data["tether_management_approved"]))
    data["inspection_coverage_pct"] = st.sidebar.slider("Inspection coverage (%)", 0.0, 100.0, float(data["inspection_coverage_pct"]), 0.5)
    data["critical_anomaly"] = st.sidebar.checkbox("Critical anomaly identified", bool(data["critical_anomaly"]))
    data["engineering_disposition_available"] = st.sidebar.checkbox("Engineering disposition available", bool(data["engineering_disposition_available"]))
    return data


def main() -> None:
    try:
        import streamlit as st
        import streamlit.components.v1 as components
    except ImportError as exc:
        raise SystemExit("Streamlit is required for the UI. Run: python -m pip install streamlit") from exc

    st.set_page_config(page_title=APP_TITLE, page_icon="C", layout="wide", initial_sidebar_state="expanded")
    st.markdown(
        """
        <style>
        .stApp {background:#edf1ef;color:#15232a;}
        .block-container {max-width:1500px;padding-top:1.2rem;padding-bottom:3rem;}
        .mrsif-head {background:#102934;color:#f5f1e8;padding:22px 26px;border-top:7px solid #d6a72b;}
        .mrsif-kicker {font:700 12px Arial;letter-spacing:2px;color:#8ddce1;margin-bottom:8px;}
        .mrsif-title {font:800 31px Arial;margin:0 0 6px 0;}
        .mrsif-sub {font:400 14px Arial;color:#c8d7da;max-width:1000px;line-height:1.5;}
        .boundary {background:#fff7df;border-left:5px solid #d6a72b;padding:12px 15px;margin:12px 0;font:600 13px Arial;color:#493b17;}
        .state-card {padding:16px 18px;border-radius:6px;background:white;border:1px solid #d5dcda;min-height:104px;}
        .state-label {font:700 11px Arial;letter-spacing:1.4px;color:#617077;}
        .state-value {font:800 28px Arial;margin-top:7px;}
        .gate-card {background:#ffffff;border:1px solid #d5dcda;border-left-width:6px;padding:15px 17px;margin:8px 0;border-radius:4px;}
        .gate-code {font:800 12px Arial;letter-spacing:1.3px;color:#66747a;}
        .gate-name {font:800 18px Arial;margin:3px 0 6px 0;color:#13242c;}
        .gate-detail {font:400 13px Arial;color:#435158;line-height:1.45;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    tests = run_gate_regression_tests()
    st.sidebar.success(f"Embedded regression tests: {len(tests)}/{len(tests)} PASS")
    scenario_name = st.sidebar.selectbox("Demonstration scenario", list(SCENARIOS))
    manual_mode = st.sidebar.toggle("Enable manual sandbox", value=False)
    data = scenario_data(scenario_name)
    if manual_mode:
        data = _manual_inputs(st, data)

    gates = evaluate_gates(data)
    mission_state = overall_state(gates)
    state_color = _status_color(mission_state)

    st.markdown(
        f"""
        <div class="mrsif-head">
          <div class="mrsif-kicker">MARINE ROBOTICS AND SUBSEA INTELLIGENCE FRAMEWORK</div>
          <div class="mrsif-title">PARADIP ROV-USV CHAIN INSPECTION</div>
          <div class="mrsif-sub">A gate-based planning and assurance demonstration for weather-window selection, USV reconnaissance, ROV inspection and evidence closeout.</div>
        </div>
        <div class="boundary">SIMULATED / CONFIGURED EXAMPLE. This screen does not control equipment, certify compliance or predict future weather. Official advisories, port authority clearance, approved RAMS and OEM limits govern the work.</div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "MISSION STATE", mission_state, state_color),
        (c2, "CAMPAIGN BASIS", data["season"], "#16697a"),
        (c3, "SEA STATE EXAMPLE", f"Hs {data['significant_wave_height_m']:.2f} m | {data['surface_current_mps']:.2f} m/s", "#2b5968"),
        (c4, "VISIBILITY EXAMPLE", f"{data['visibility_m']:.2f} m | sonar {'online' if data['imaging_sonar_online'] else 'offline'}", "#2b5968"),
    ]
    for column, label, value, color in cards:
        with column:
            st.markdown(f'<div class="state-card"><div class="state-label">{html.escape(label)}</div><div class="state-value" style="color:{color};font-size:{"28px" if label == "MISSION STATE" else "17px"}">{html.escape(str(value))}</div></div>', unsafe_allow_html=True)

    tab_mission, tab_gates, tab_evidence, tab_boundary = st.tabs(["Mission view", "Gate logic", "Evidence package", "Assurance boundary"])

    with tab_mission:
        selected_index = st.select_slider("Mission gate", options=list(range(len(gates))), value=0, format_func=lambda i: f"{gates[i].code} - {gates[i].name}")
        selected_gate = gates[selected_index]
        left, right = st.columns([1.65, 1.0])
        with left:
            components.html(_render_scene(data, selected_gate), height=450, scrolling=False)
        with right:
            color = _status_color(selected_gate.status)
            st.markdown(f'<div class="gate-card" style="border-left-color:{color}"><div class="gate-code">{selected_gate.code} | {selected_gate.phase.upper()} | {selected_gate.status}</div><div class="gate-name">{html.escape(selected_gate.name)}</div><div class="gate-detail">{html.escape(selected_gate.detail)}</div></div>', unsafe_allow_html=True)
            st.markdown("**Required action**")
            st.write(selected_gate.action)
            st.markdown("**Evidence snapshot**")
            for item in selected_gate.evidence:
                st.write(f"- {item}")

        st.markdown("### Recommended planning windows")
        _safe_dataframe(st, [
            {"Priority": "Primary", "Window": "20 February-20 March", "Basis": "Best balance of low rainfall, lower cyclone exposure and reduced runoff risk", "Decision": "Preferred campaign basis"},
            {"Priority": "Secondary", "Window": "15 January-15 February", "Basis": "Generally dry; verify local turbidity, dredging and winter sea state", "Decision": "Good alternative"},
            {"Priority": "Conditional", "Window": "19-23 September", "Basis": "Forecast-selected neap-tide opportunity only", "Decision": "WATCH; mobilise only after D-7/D-3/D-1 release"},
        ])

    with tab_gates:
        rows = []
        for gate in gates:
            rows.append({"Gate": gate.code, "Lifecycle": gate.phase, "Decision": gate.status, "Gate name": gate.name, "Reason": gate.detail, "Next action": gate.action})
        _safe_dataframe(st, rows)
        for gate in gates:
            with st.expander(f"{gate.code} | {gate.status} | {gate.name}"):
                st.write(gate.detail)
                st.write("Evidence:")
                for item in gate.evidence:
                    st.write(f"- {item}")
                st.write(f"Action: {gate.action}")

    with tab_evidence:
        package = evidence_package(data, gates)
        st.markdown("### Demonstration evidence snapshot")
        st.json(package, expanded=False)
        st.download_button(
            "Download JSON evidence snapshot",
            data=json.dumps(package, indent=2),
            file_name="mrsif_paradip_chain_inspection_evidence.json",
            mime="application/json",
        )
        st.caption("The JSON is a demonstration record, not a client certificate or regulatory submission.")

    with tab_boundary:
        st.markdown("### What this demonstration does")
        st.write("- Makes prerequisites explicit and traceable across planning, acquisition, execution and delivery.")
        st.write("- Propagates invalid coordinate-frame and time-sync conditions into dependent gates.")
        st.write("- Separates sonar localisation from optical evidence quality.")
        st.write("- Blocks closeout when evidence records or engineering dispositions are incomplete.")
        st.markdown("### What it does not do")
        st.write("- It does not ingest live IMD, INCOIS, tide, AIS, USV, ROV or port data.")
        st.write("- It does not approve weather, launch, navigation, diving, lifting or inspection operations.")
        st.write("- It does not define OEM limits, acceptance criteria, remaining strength or fitness for service.")
        st.write("- It is not a compliance certificate, class approval or client acceptance record.")
        st.markdown("### Embedded regression checks")
        _safe_dataframe(st, [{"Check": name, "Result": result} for name, result in tests.items()])

    st.caption(f"{APP_VERSION} | Offline demonstration | Values are simulated/configured examples")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        completed = run_gate_regression_tests()
        for test_name, result in completed.items():
            print(f"{result}: {test_name}")
        print(f"All {len(completed)} embedded MRSIF gate tests passed.")
    else:
        main()
