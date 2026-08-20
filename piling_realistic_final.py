"""MRSIF - realistic pile foundation installation mission demonstration.

Run locally:
    python -m pip install streamlit
    streamlit run mrsif_piling_realistic.py

Keep this file together with the assets/mrsif_piling folder. All mission values
and project limits are labelled as simulated/configured examples. Replace them
with approved engineering data before any project use.
"""

from __future__ import annotations

import base64
import html
import json
import mimetypes
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


ASSET_DIR = Path(__file__).with_name("assets") / "mrsif_piling"
_ASSET_CACHE: dict[str, str] = {}


def asset_data_uri(filename: str) -> str:
    """Return a local mission image as a data URI; never uses a network URL."""
    if filename in _ASSET_CACHE:
        return _ASSET_CACHE[filename]
    path = ASSET_DIR / filename
    if not path.exists():
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    value = f"data:{mime};base64,{encoded}"
    _ASSET_CACHE[filename] = value
    return value


st.set_page_config(
    page_title="MRSIF | SST & Pile Installation Mission",
    page_icon="âš“",
    layout="wide",
    initial_sidebar_state="collapsed",
)


PHASES: list[dict[str, str]] = [
    {
        "code": "01",
        "name": "Pre-install reference survey",
        "short": "USV baseline",
        "drawing": "Before SST deployment",
        "instruction": "Wavebot runs an autonomous survey line outside the installation exclusion zone. NORBIT iWBMS establishes the pre-install seabed surface while the SV probe and current sensor provide acoustic-correction and operating-context inputs.",
        "next": "Accept the survey reference and release the approved lift plan for SST rigging.",
    },
    {
        "code": "02",
        "name": "Hanging frame & SST rigging",
        "short": "Rig & connect",
        "drawing": "Drawing 1 - SST suspended below drill deck",
        "instruction": "Connect the SST to the hanging frame, HM drill pipe and levelling slings. Confirm the load path while Wavebot-mounted LiDAR observes the exposed rod and hanging-frame geometry above the waterline.",
        "next": "Authorize controlled lowering when the rigging, load evidence and above-water reference are accepted.",
    },
    {
        "code": "03",
        "name": "Controlled SST lowering",
        "short": "Lower template",
        "drawing": "Drawing 1 - controlled descent to seabed",
        "instruction": "Lower the SST through the water column while monitoring four-point tension, hoist payout and DEP-01 depth. The template-mounted inclinometer measures pitch/roll; it does not measure lowering distance. Gemini and acoustic positioning take over below the waterline.",
        "next": "Continue to the set-down window under the approved lowering procedure.",
    },
    {
        "code": "04",
        "name": "Touchdown & template levelling",
        "short": "Set down & level",
        "drawing": "Drawing 1 - SST at mudline",
        "instruction": "Confirm mudline contact using depth/load evidence, unload the lifting system in a controlled manner and use the template-mounted inclinometer to verify pitch/roll and movement after set-down.",
        "next": "Hold the template stable for the configured observation period and accept the levelling evidence.",
    },
    {
        "code": "05",
        "name": "Release frame & localize SST",
        "short": "Localize template",
        "drawing": "Drawing 2 - hanging frame recovered, SST retained",
        "instruction": "Recover the hanging frame while the SST remains on the seabed. Localize B1/B2 from the selected USBL host, apply the valid sound-speed correction and retain template attitude/movement monitoring.",
        "next": "Box in or otherwise validate the beacon geometry, then release the pile deployment phase.",
    },
    {
        "code": "06",
        "name": "Pile lowering & stabbing",
        "short": "Stab pile",
        "drawing": "Pile introduced through the SST guide",
        "instruction": "Lower the pile through the SST guide. Use the side-mounted Gemini image, B1/B2 template position and pile inclination/offset evidence. LiDAR observes only the exposed rod; acoustic sensors provide the submerged view.",
        "next": "Confirm guide entry and pile alignment before landing the MENCK hammer on the pile.",
    },
    {
        "code": "07",
        "name": "MENCK MHU 150S driving",
        "short": "Hammer & trend",
        "drawing": "Drawing 3 - MHU-150S above SST",
        "instruction": "Drive the pile with the MENCK MHU 150S while preserving hammer energy, blow rate and penetration trend. Wavebot LiDAR follows exposed rod/hammer motion to the waterline; acoustic positioning and imaging provide the underwater reference.",
        "next": "Apply the project-approved stop/review criterion and obtain the authorized engineering disposition.",
    },
    {
        "code": "08",
        "name": "Post-install verification",
        "short": "Survey & close",
        "drawing": "As-built evidence after pile driving",
        "instruction": "Run the post-install autonomous Wavebot/NORBIT survey, confirm final template attitude and consolidate MBES, Gemini, LiDAR, beacon, current/SV and driving records into the MRSIF work reference.",
        "next": "Issue the evidence package to Survey, Installation, QA/QC and the Client for formal acceptance.",
    },
]


SCENARIOS: dict[str, dict[str, Any]] = {
    "Nominal controlled installation": {
        "survey_coverage": 99.2,
        "post_coverage": 98.7,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.8, 125.6, 125.1, 124.9],
        "descent_rate": 0.34,
        "pitch": 0.18,
        "roll": 0.22,
        "movement": 0.04,
        "beacons": 2,
        "fix_uncertainty": 0.22,
        "gemini_confidence": 91,
        "pile_offset": 0.08,
        "pile_verticality": 0.23,
        "hammer_energy": 110,
        "hammer_flow": 350,
        "hammer_pressure": 248,
        "blow_rate": 35,
        "penetration": 36,
        "hammer_log": True,
        "records": 7,
    },
    "SST tilt after touchdown": {
        "survey_coverage": 99.2,
        "post_coverage": 97.8,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.5, 126.0, 125.2, 124.7],
        "descent_rate": 0.34,
        "pitch": 0.48,
        "roll": 1.34,
        "movement": 0.29,
        "beacons": 2,
        "fix_uncertainty": 0.29,
        "gemini_confidence": 88,
        "pile_offset": 0.24,
        "pile_verticality": 0.46,
        "hammer_energy": 90,
        "hammer_flow": 330,
        "hammer_pressure": 241,
        "blow_rate": 32,
        "penetration": 31,
        "hammer_log": True,
        "records": 6,
    },
    "Acoustic beacon geometry degraded": {
        "survey_coverage": 99.0,
        "post_coverage": 98.1,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.9, 125.4, 125.1, 125.0],
        "descent_rate": 0.31,
        "pitch": 0.20,
        "roll": 0.24,
        "movement": 0.05,
        "beacons": 1,
        "fix_uncertainty": 0.94,
        "gemini_confidence": 86,
        "pile_offset": 0.19,
        "pile_verticality": 0.31,
        "hammer_energy": 105,
        "hammer_flow": 345,
        "hammer_pressure": 246,
        "blow_rate": 34,
        "penetration": 34,
        "hammer_log": True,
        "records": 6,
    },
    "Levelling sling tension imbalance": {
        "survey_coverage": 99.1,
        "post_coverage": 97.9,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [96.0, 151.0, 124.0, 126.0],
        "descent_rate": 0.29,
        "pitch": 0.72,
        "roll": 0.84,
        "movement": 0.13,
        "beacons": 2,
        "fix_uncertainty": 0.34,
        "gemini_confidence": 87,
        "pile_offset": 0.17,
        "pile_verticality": 0.35,
        "hammer_energy": 100,
        "hammer_flow": 340,
        "hammer_pressure": 244,
        "blow_rate": 33,
        "penetration": 33,
        "hammer_log": True,
        "records": 6,
    },
    "Gemini acoustic view unavailable": {
        "survey_coverage": 99.0,
        "post_coverage": 97.5,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.8, 125.6, 125.1, 124.9],
        "descent_rate": 0.34,
        "pitch": 0.21,
        "roll": 0.25,
        "movement": 0.05,
        "beacons": 2,
        "fix_uncertainty": 0.25,
        "gemini_confidence": 18,
        "pile_offset": 0.16,
        "pile_verticality": 0.34,
        "hammer_energy": 105,
        "hammer_flow": 345,
        "hammer_pressure": 246,
        "blow_rate": 34,
        "penetration": 34,
        "hammer_log": True,
        "records": 6,
    },
    "Low penetration trend / engineering review": {
        "survey_coverage": 99.2,
        "post_coverage": 98.0,
        "obstruction_clear": True,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.8, 125.6, 125.1, 124.9],
        "descent_rate": 0.34,
        "pitch": 0.19,
        "roll": 0.24,
        "movement": 0.05,
        "beacons": 2,
        "fix_uncertainty": 0.24,
        "gemini_confidence": 90,
        "pile_offset": 0.09,
        "pile_verticality": 0.25,
        "hammer_energy": 145,
        "hammer_flow": 375,
        "hammer_pressure": 258,
        "blow_rate": 37,
        "penetration": 5,
        "hammer_log": True,
        "records": 6,
    },
    "NORBIT survey coverage gap": {
        "survey_coverage": 82.0,
        "post_coverage": 84.0,
        "obstruction_clear": False,
        "lidar_reference": True,
        "rigging_confirmed": True,
        "tensions": [124.8, 125.6, 125.1, 124.9],
        "descent_rate": 0.34,
        "pitch": 0.20,
        "roll": 0.23,
        "movement": 0.05,
        "beacons": 2,
        "fix_uncertainty": 0.25,
        "gemini_confidence": 89,
        "pile_offset": 0.09,
        "pile_verticality": 0.25,
        "hammer_energy": 105,
        "hammer_flow": 345,
        "hammer_pressure": 246,
        "blow_rate": 34,
        "penetration": 34,
        "hammer_log": True,
        "records": 5,
    },
    "Surface current exceeds installation limit": {
        "surface_current": 1.34,
        "current_direction": 247,
    },
    "Sound velocity profile invalid / stale": {
        "svp_valid": False,
        "sound_speed": 0.0,
    },
    "USV telemetry timeout / no input": {
        "telemetry_link": False,
    },
}


BASE_CONTEXT: dict[str, Any] = {
    "telemetry_link": True,
    "svp_valid": True,
    "sound_speed": 1_497.4,
    "surface_current": 0.62,
    "current_direction": 238,
}


def scenario_data(name: str) -> dict[str, Any]:
    """Merge a scenario with the nominal equipment and environmental context."""
    return {
        **SCENARIOS["Nominal controlled installation"],
        **BASE_CONTEXT,
        **SCENARIOS[name],
    }


STATUS_RANK = {"PENDING": 0, "GO": 1, "WATCH": 2, "HOLD": 3}
STATUS_COLOR = {"PENDING": "#778187", "GO": "#168366", "WATCH": "#c47d18", "HOLD": "#b43a32"}


def worst_status(*statuses: str) -> str:
    """Return the most restrictive MRSIF state."""
    return max(statuses, key=lambda item: STATUS_RANK[item])


def high_bad(value: float, watch: float, hold: float) -> str:
    if value > hold:
        return "HOLD"
    if value > watch:
        return "WATCH"
    return "GO"


def low_bad(value: float, hold: float, watch: float) -> str:
    if value < hold:
        return "HOLD"
    if value < watch:
        return "WATCH"
    return "GO"


def tension_spread(values: list[float]) -> float:
    average = sum(values) / len(values)
    return (max(values) - min(values)) / average * 100


def evaluate_gates(data: dict[str, Any]) -> list[dict[str, str]]:
    """Evaluate visible demonstration gates against configured example limits."""
    spread = tension_spread(data["tensions"])

    survey_state = low_bad(data["survey_coverage"], 95.0, 98.0)
    if not data["obstruction_clear"] or not data["svp_valid"] or not data["telemetry_link"]:
        survey_state = "HOLD"

    lift_state = high_bad(spread, 7.0, 10.0)
    if not data["rigging_confirmed"] or not data["lidar_reference"]:
        lift_state = "HOLD"

    lowering_state = worst_status(
        high_bad(spread, 7.0, 10.0),
        high_bad(data["descent_rate"], 0.50, 0.65),
        high_bad(max(abs(data["pitch"]), abs(data["roll"])), 0.80, 1.50),
        high_bad(data["surface_current"], 0.80, 1.20),
        "GO" if data["telemetry_link"] else "HOLD",
    )

    touchdown_state = worst_status(
        high_bad(max(abs(data["pitch"]), abs(data["roll"])), 0.70, 1.00),
        high_bad(data["movement"], 0.15, 0.25),
    )

    localization_state = "GO"
    if data["beacons"] < 2 or data["fix_uncertainty"] > 0.50 or not data["svp_valid"]:
        localization_state = "HOLD"
    elif data["fix_uncertainty"] > 0.35:
        localization_state = "WATCH"

    pile_state = worst_status(
        low_bad(data["gemini_confidence"], 60.0, 75.0),
        high_bad(data["pile_offset"], 0.22, 0.30),
        high_bad(data["pile_verticality"], 0.40, 0.50),
        "GO" if data["telemetry_link"] and data["svp_valid"] else "HOLD",
    )

    hammer_state = low_bad(data["penetration"], 12.0, 20.0)
    if not (15 <= data["hammer_energy"] <= 150) or not data["hammer_log"]:
        hammer_state = "HOLD"

    close_state = worst_status(
        low_bad(data["post_coverage"], 95.0, 98.0),
        "GO" if data["records"] >= 7 else "HOLD",
        "GO" if data["telemetry_link"] else "HOLD",
    )

    return [
        {
            "name": "Reference survey",
            "status": survey_state,
            "detail": f'{data["survey_coverage"]:.1f}% MBES; SV profile {"valid" if data["svp_valid"] else "invalid"}; telemetry {"online" if data["telemetry_link"] else "timeout"}',
            "action": "Restore the USV data link and valid sound-velocity profile, then complete the target-area multibeam/obstruction review.",
        },
        {
            "name": "Lift & hanging frame",
            "status": lift_state,
            "detail": f"{spread:.1f}% four-point tension spread; LiDAR surface reference {'valid' if data['lidar_reference'] else 'invalid'}",
            "action": "Correct the rigging/load evidence and revalidate the surface reference.",
        },
        {
            "name": "Controlled lowering",
            "status": lowering_state,
            "detail": f'{data["descent_rate"]:.2f} m/s descent; pitch/roll {data["pitch"]:.2f}Â°/{data["roll"]:.2f}Â°; current {data["surface_current"]:.2f} m/s',
            "action": "Stop descent at a controlled hold point and correct the load/attitude condition.",
        },
        {
            "name": "Touchdown & levelling",
            "status": touchdown_state,
            "detail": f'pitch/roll {data["pitch"]:.2f}Â°/{data["roll"]:.2f}Â°; movement {data["movement"]:.2f} m',
            "action": "Maintain the SST on controlled support and obtain the levelling/settlement disposition.",
        },
        {
            "name": "Template localization",
            "status": localization_state,
            "detail": f'{data["beacons"]} beacon observations; Â±{data["fix_uncertainty"]:.2f} m; SVP {"valid" if data["svp_valid"] else "invalid"}',
            "action": "Restore independent acoustic observations, valid sound-speed correction and calibrated beacon geometry.",
        },
        {
            "name": "Pile stab & alignment",
            "status": pile_state,
            "detail": f'Gemini confidence {data["gemini_confidence"]}%; pile offset {data["pile_offset"]:.2f} m; verticality {data["pile_verticality"]:.2f}Â°',
            "action": "Hold the pile clear of a damaging interface until alignment evidence is restored.",
        },
        {
            "name": "MENCK driving response",
            "status": hammer_state,
            "detail": f'{data["hammer_energy"]} kJ setting; {data["blow_rate"]}/min; {data["penetration"]} mm/10 blows',
            "action": "Preserve the driving log and request the approved installation/geotechnical review; do not infer refusal or capacity from the demo.",
        },
        {
            "name": "As-built closeout",
            "status": close_state,
            "detail": f'{data["post_coverage"]:.1f}% post-survey coverage; {data["records"]}/7 evidence records present',
            "action": "Keep the work reference open and obtain the missing survey or installation record.",
        },
    ]


def mission_recommendation(gates: list[dict[str, str]], phase_index: int) -> tuple[str, dict[str, str]]:
    active = gates[: phase_index + 1]
    worst = max(active, key=lambda gate: STATUS_RANK[gate["status"]])
    return worst["status"], worst


def phase_geometry(phase_index: int, data: dict[str, Any], usbl_host: str) -> dict[str, str]:
    """Translate the reference drawings into simple cross-section geometry."""
    if phase_index == 0:
        template_y = 194
        template_depth = 0.0
    elif phase_index == 1:
        template_y = 230
        template_depth = 2.5
    elif phase_index == 2:
        template_y = 342
        template_depth = 18.4
    else:
        template_y = 438
        template_depth = 30.8

    frame_y = template_y - 50 if phase_index <= 3 else 150
    frame_x = 0 if phase_index <= 3 else -110
    frame_center_x = 635 + frame_x
    sling_opacity = "1" if 1 <= phase_index <= 3 else "0"
    pile_opacity = "1" if phase_index >= 5 else "0"
    hammer_opacity = "1" if phase_index == 6 else "0"
    acoustic_opacity = "1" if phase_index >= 2 else "0.18"
    gemini_opacity = "1" if 2 <= phase_index <= 6 else "0.15"
    mbes_opacity = "1" if phase_index in (0, 7) else "0.08"
    lidar_opacity = "1" if phase_index in (0, 1, 5, 6) else "0.24"
    tilt_angle = max(-3.2, min(3.2, data["roll"] * 1.8)) if phase_index >= 3 else data["roll"] * 0.4
    template_opacity = "0.28" if phase_index == 0 else "1"
    usbl_x = 905 if usbl_host == "Wavebot USV" else 1155
    link_color = "#52d7a5" if data["telemetry_link"] else "#e95f51"

    if phase_index == 5:
        pile_top, pile_bottom = 286, 575
    elif phase_index == 6:
        pile_top, pile_bottom = 306, 625
    else:
        pile_top, pile_bottom = 400, 650

    return {
        "TEMPLATE_Y": f"{template_y}",
        "TEMPLATE_LABEL_Y": f"{template_y + 154}",
        "TEMPLATE_DEPTH": f"{template_depth:.1f}",
        "FRAME_Y": f"{frame_y}",
        "FRAME_X": f"{frame_x}",
        "FRAME_CENTER_X": f"{frame_center_x}",
        "SLING_OPACITY": sling_opacity,
        "PILE_OPACITY": pile_opacity,
        "HAMMER_OPACITY": hammer_opacity,
        "ACOUSTIC_OPACITY": acoustic_opacity,
        "GEMINI_OPACITY": gemini_opacity,
        "MBES_OPACITY": mbes_opacity,
        "LIDAR_OPACITY": lidar_opacity,
        "TILT_ANGLE": f"{tilt_angle:.2f}",
        "TEMPLATE_OPACITY": template_opacity,
        "USBL_X": f"{usbl_x}",
        "USBL_HOST": usbl_host.upper(),
        "LINK_COLOR": link_color,
        "LINK_STATUS": "ONLINE" if data["telemetry_link"] else "NO INPUT / TIMEOUT",
        "CURRENT_VALUE": f'{data["surface_current"]:.2f} m/s @ {data["current_direction"]}Â°',
        "SVP_VALUE": f'{data["sound_speed"]:.1f} m/s' if data["svp_valid"] else "INVALID / STALE",
        "PILE_TOP": f"{pile_top}",
        "PILE_BOTTOM": f"{pile_bottom}",
    }


SCENE_TEMPLATE = r"""
<svg viewBox="0 0 1300 700" role="img" aria-label="SST deployment and pile installation mission cross-section">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cad9d9"/><stop offset="1" stop-color="#e8e6dc"/></linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#19768b"/><stop offset="0.55" stop-color="#0b5368"/><stop offset="1" stop-color="#073949"/></linearGradient>
    <linearGradient id="sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a79067"/><stop offset="1" stop-color="#62543b"/></linearGradient>
    <linearGradient id="sonarFan" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffbd4a" stop-opacity=".62"/><stop offset="1" stop-color="#ffbd4a" stop-opacity=".03"/></linearGradient>
    <linearGradient id="mbesFan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4bd8e8" stop-opacity=".63"/><stop offset="1" stop-color="#4bd8e8" stop-opacity=".04"/></linearGradient>
    <pattern id="soil" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M0 20L20 0" stroke="#dfc995" stroke-opacity=".13" stroke-width="3"/></pattern>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#071c22" flood-opacity=".28"/></filter>
    <clipPath id="wavebotClip"><rect x="775" y="40" width="270" height="124" rx="9"/></clipPath>
    <clipPath id="rigScreenClip"><rect x="101" y="50" width="108" height="24" rx="2"/></clipPath>
    <clipPath id="navScreenClip"><rect x="1101" y="111" width="91" height="23" rx="2"/></clipPath>
  </defs>
  <style>
    .lab{font:800 12px 'Arial Narrow','Segoe UI',sans-serif;letter-spacing:1px;text-transform:uppercase}
    .micro{font:700 11px 'Segoe UI',sans-serif}
    .tiny{font:700 9px 'Segoe UI',sans-serif;letter-spacing:.4px}
    .dash{stroke-dasharray:9 8;animation:dash 1.3s linear infinite}
    .pulse{animation:pulse 1.5s ease-in-out infinite}
    .hammering{animation:hammer .42s ease-in-out infinite;transform-origin:630px 285px}
    .boat{animation:bob 2.7s ease-in-out infinite;transform-origin:center}
    @keyframes dash{to{stroke-dashoffset:-34}}
    @keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}
    @keyframes hammer{0%,100%{transform:translateY(0)}47%{transform:translateY(8px)}54%{transform:translateY(-3px)}}
    @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(3px)}}
  </style>

  <rect width="1300" height="170" fill="url(#sky)"/>
  <rect y="170" width="1300" height="405" fill="url(#water)"/>
  <path d="M0 575 C150 559 260 586 400 569 C560 548 690 590 840 567 C1010 541 1140 582 1300 558 L1300 700 L0 700Z" fill="url(#sand)"/>
  <path d="M0 575 C150 559 260 586 400 569 C560 548 690 590 840 567 C1010 541 1140 582 1300 558" fill="none" stroke="#d4bf8d" stroke-width="5"/>
  <path d="M0 575 C150 559 260 586 400 569 C560 548 690 590 840 567 C1010 541 1140 582 1300 558 L1300 700 L0 700Z" fill="url(#soil)"/>
  <path d="M0 174 C140 163 285 184 425 172 C570 160 710 184 865 171 C1030 158 1165 181 1300 169" fill="none" stroke="#a7d8dc" stroke-width="4"/>

  <!-- Jack-up rig and drilling spread -->
  <g id="rig" filter="url(#shadow)">
    <rect x="65" y="92" width="535" height="55" fill="#d6a32d" stroke="#4f431f" stroke-width="5"/>
    <rect x="75" y="77" width="250" height="17" fill="#5c686c"/>
    <rect x="95" y="45" width="120" height="33" fill="#e7e0cd" stroke="#4d585c" stroke-width="4"/>
    <rect x="225" y="54" width="88" height="24" fill="#c45a2b" stroke="#713118" stroke-width="4"/>
    <path d="M330 92 L376 7 L430 92 M347 61 H412 M359 35 H398 M343 61L414 61 M352 35L405 92 M407 35L354 92" fill="none" stroke="#566368" stroke-width="7"/>
    <rect x="455" y="51" width="252" height="39" fill="#e5b63e" stroke="#514620" stroke-width="5"/>
    <rect x="495" y="31" width="112" height="20" fill="#e9e4d4" stroke="#566368" stroke-width="4"/>
    <rect x="600" y="108" width="175" height="30" fill="#bdc3bf" stroke="#4f5b60" stroke-width="5"/>
    <text x="83" y="126" class="lab" fill="#29281f">JACK-UP RIG / MAIN DECK</text>
    <text x="505" y="77" class="lab" fill="#2c291f">DRILL FLOOR</text>
    <text x="618" y="128" class="lab" fill="#374348">DRILL DECK</text>

    <!-- JUR lattice leg -->
    <path d="M145 147 L112 615 M267 147 L300 615" stroke="#626e72" stroke-width="13"/>
    <path d="M145 170L275 230L126 290L285 350L118 410L294 470L111 530L300 590 M267 170L135 230L280 290L122 350L290 410L113 470L296 530L111 590" fill="none" stroke="#7c888b" stroke-width="5" opacity=".85"/>
    <path d="M112 615H300" stroke="#454f53" stroke-width="17"/>
    <text x="170" y="330" class="lab" fill="#d5e8e7" transform="rotate(-90 170 330)">JUR LEG</text>
  </g>

  <!-- Rig survey desk mirrors USV telemetry -->
  <g filter="url(#shadow)">
    <rect x="93" y="42" width="124" height="42" rx="3" fill="#1c2930" stroke="#55656b" stroke-width="3"/>
    <image href="__RIG_SCREEN_URI__" x="101" y="50" width="108" height="24" preserveAspectRatio="xMidYMid slice" clip-path="url(#rigScreenClip)"/>
    <circle cx="207" cy="78" r="3" fill="__LINK_COLOR__"/>
    <text x="95" y="37" class="tiny" fill="#26353a">RIG SURVEY DESK â€¢ MBES / GEMINI / LiDAR</text>
  </g>

  <!-- Hanging frame and drill pipe -->
  <line x1="635" y1="90" x2="__FRAME_CENTER_X__" y2="__FRAME_Y__" stroke="#4d5a5f" stroke-width="11"/>
  <line x1="635" y1="90" x2="__FRAME_CENTER_X__" y2="__FRAME_Y__" stroke="#c8d0ce" stroke-width="3" stroke-dasharray="16 9"/>
  <g transform="translate(__FRAME_X__ __FRAME_Y__)" filter="url(#shadow)">
    <path d="M527 0H742L716 39H552Z" fill="#758489" stroke="#38454a" stroke-width="5"/>
    <path d="M552 39L590 0M716 39L678 0" stroke="#d6a32d" stroke-width="7"/>
    <text x="635" y="25" text-anchor="middle" class="lab" fill="#f7f4e8">HANGING FRAME</text>
  </g>

  <!-- Lift / levelling slings -->
  <g opacity="__SLING_OPACITY__">
    <line x1="552" y1="__FRAME_Y__" x2="545" y2="__TEMPLATE_Y__" stroke="#efc75f" stroke-width="4"/>
    <line x1="716" y1="__FRAME_Y__" x2="724" y2="__TEMPLATE_Y__" stroke="#efc75f" stroke-width="4"/>
    <line x1="588" y1="__FRAME_Y__" x2="592" y2="__TEMPLATE_Y__" stroke="#f1d582" stroke-width="3"/>
    <line x1="679" y1="__FRAME_Y__" x2="680" y2="__TEMPLATE_Y__" stroke="#f1d582" stroke-width="3"/>
  </g>

  <!-- SST support template; tilt is visually exaggerated -->
  <g transform="translate(0 __TEMPLATE_Y__) rotate(__TILT_ANGLE__ 635 60)" filter="url(#shadow)" opacity="__TEMPLATE_OPACITY__">
    <rect x="525" y="0" width="220" height="125" fill="#33474c" fill-opacity=".68" stroke="#c9b172" stroke-width="8"/>
    <path d="M525 0L745 125M745 0L525 125M585 0V125M685 0V125M525 42H745M525 84H745" fill="none" stroke="#d7c58f" stroke-width="6"/>
    <path d="M515 125H755" stroke="#68777b" stroke-width="14"/>
    <path d="M535 125L525 148M735 125L745 148" stroke="#56666a" stroke-width="12"/>

    <!-- Acoustic beacons -->
    <g class="pulse">
      <rect x="536" y="-23" width="14" height="28" rx="5" fill="#e06432" stroke="#f1d379" stroke-width="3"/>
      <circle cx="543" cy="-29" r="8" fill="#e7c84e"/>
      <rect x="720" y="-23" width="14" height="28" rx="5" fill="#e06432" stroke="#f1d379" stroke-width="3"/>
      <circle cx="727" cy="-29" r="8" fill="#e7c84e"/>
    </g>
    <text x="508" y="-30" class="tiny" fill="#ffeab3">B1</text>
    <text x="744" y="-30" class="tiny" fill="#ffeab3">B2</text>

    <!-- Pressure/depth sensor: lowering amount is not derived from inclination -->
    <g>
      <rect x="510" y="73" width="28" height="20" rx="5" fill="#16313a" stroke="#53d7df" stroke-width="4"/>
      <circle cx="524" cy="83" r="5" fill="#a7f0f2"/>
      <text x="474" y="105" class="tiny" fill="#d7eff5">DEP-01</text>
    </g>

    <!-- Dual-axis inclinometer -->
    <g>
      <circle cx="693" cy="91" r="20" fill="#f1eee2" stroke="#d45b2a" stroke-width="5"/>
      <path d="M678 91H708M693 76V106" stroke="#4d5d63" stroke-width="3"/>
      <circle cx="693" cy="91" r="5" fill="#d45b2a"/>
      <text x="716" y="96" class="tiny" fill="#fff0cd">INC-01 â€¢ PITCH / ROLL</text>
    </g>
  </g>
  <text x="600" y="__TEMPLATE_LABEL_Y__" text-anchor="end" class="lab" fill="#fff0c8">SST â€¢ DEPTH __TEMPLATE_DEPTH__ m â€¢ INC-01 ON TEMPLATE</text>

  <!-- USBL transducer may be hosted from Wavebot or watchkeeping boat -->
  <g opacity="__ACOUSTIC_OPACITY__">
    <rect x="__USBL_X__" y="174" width="16" height="24" rx="6" fill="#f0c65b" stroke="#28373d" stroke-width="3"/>
    <path d="M__USBL_X__ 198 Q800 328 543 __TEMPLATE_Y__ M__USBL_X__ 198 Q850 345 727 __TEMPLATE_Y__" fill="none" stroke="#f2c85f" stroke-width="3" class="dash"/>
    <text x="860" y="232" text-anchor="middle" class="tiny" fill="#ffeab3">USBL â€¢ __USBL_HOST__ â€¢ SV CORRECTION __SVP_VALUE__</text>
  </g>

  <!-- Tritech Gemini is side-mounted on Wavebot, just submerged and above iWBMS -->
  <g opacity="__GEMINI_OPACITY__" class="pulse">
    <path d="M825 184 Q735 260 660 __TEMPLATE_Y__ Q770 400 840 194Z" fill="url(#sonarFan)" stroke="#f2b84a" stroke-width="2"/>
    <path d="M828 188Q760 280 690 __TEMPLATE_Y__M828 188Q790 330 735 __TEMPLATE_Y__" fill="none" stroke="#ffdc86" stroke-width="2" opacity=".7"/>
    <text x="786" y="258" class="tiny" fill="#ffe6a7">GEMINI 1200ik â€¢ SUBMERGED TEMPLATE VIEW</text>
  </g>

  <!-- Pile and MENCK hammer -->
  <g opacity="__PILE_OPACITY__">
    <rect x="619" y="__PILE_TOP__" width="32" height="calc(__PILE_BOTTOM__ - __PILE_TOP__)" fill="#aeb9bc" stroke="#435157" stroke-width="5"/>
    <path d="M626 __PILE_TOP__V__PILE_BOTTOM__M644 __PILE_TOP__V__PILE_BOTTOM__" stroke="#e7eceb" stroke-width="3" opacity=".7"/>
    <path d="M614 __PILE_BOTTOM__H656L649 675H621Z" fill="#68767b" stroke="#435157" stroke-width="4"/>
    <text x="670" y="545" class="lab" fill="#f2e6c8">SKIRT PILE</text>
  </g>
  <g opacity="__HAMMER_OPACITY__" class="hammering" filter="url(#shadow)">
    <path d="M592 211H678L667 314H603Z" fill="#e1ab2e" stroke="#4d451e" stroke-width="7"/>
    <rect x="604" y="224" width="62" height="23" fill="#1f3949"/>
    <text x="635" y="240" text-anchor="middle" class="tiny" fill="#fff">MENCK</text>
    <path d="M602 266H668M610 314H660L654 329H616Z" stroke="#4d451e" stroke-width="7"/>
    <text x="686" y="282" class="lab" fill="#ffe8a0">MHU 150S</text>
  </g>

  <!-- Real Wavebot reference from the supplied Vikra brochure -->
  <g class="boat" filter="url(#shadow)">
    <rect x="770" y="35" width="280" height="134" rx="11" fill="#21353b" stroke="#d45e2f" stroke-width="5"/>
    <image href="__WAVEBOT_URI__" x="775" y="40" width="270" height="124" preserveAspectRatio="xMidYMid slice" clip-path="url(#wavebotClip)"/>
    <rect x="775" y="137" width="270" height="27" fill="#10252c" fill-opacity=".82"/>
    <text x="787" y="154" class="lab" fill="#f4e7c8">VIKRA WAVEBOT â€¢ AUTONOMOUS OPERATION</text>
  </g>

  <!-- Velodyne on top of USV; rays stop at the waterline -->
  <g opacity="__LIDAR_OPACITY__">
    <ellipse cx="914" cy="44" rx="15" ry="7" fill="#27363b" stroke="#d45e2f" stroke-width="4"/>
    <rect x="907" y="29" width="14" height="14" fill="#465155"/>
    <path d="M914 45L633 91L775 169L1010 169Z" fill="#e4ca52" opacity=".13" stroke="#e4ca52" stroke-width="2"/>
    <path d="M914 45L635 91M914 45L778 169M914 45L1008 169" stroke="#f1d963" stroke-width="2" stroke-dasharray="6 5"/>
    <text x="813" y="22" class="tiny" fill="#26353a">VELODYNE LiDAR â€¢ EXPOSED ROD / HAMMER TO MSL</text>
    <text x="696" y="190" text-anchor="middle" class="tiny" fill="#dff2f2">LiDAR â†’ ACOUSTIC HANDOVER AT WATERLINE</text>
  </g>

  <!-- Sensor stack beneath Wavebot: Gemini above NORBIT -->
  <g>
    <rect x="817" y="171" width="28" height="16" rx="4" fill="#172a32" stroke="#f2b84a" stroke-width="3"/>
    <path d="M823 176H839" stroke="#f8e0a3" stroke-width="3"/>
    <text x="851" y="183" class="tiny" fill="#ffe6a7">TRITECH GEMINI</text>
    <rect x="821" y="193" width="21" height="16" rx="3" fill="#172a32" stroke="#4fd6e5" stroke-width="3"/>
    <text x="851" y="205" class="tiny" fill="#baf4f6">NORBIT iWBMS</text>
  </g>

  <!-- Multibeam swath -->
  <g opacity="__MBES_OPACITY__" class="pulse">
    <path d="M832 209L712 574Q835 540 958 570Z" fill="url(#mbesFan)" stroke="#4fd6e5" stroke-width="2"/>
    <path d="M832 209L770 566M832 209V558M832 209L913 565" stroke="#80e8f0" stroke-width="2" opacity=".48"/>
    <path d="M726 574Q835 545 949 569" fill="none" stroke="#9af0f4" stroke-width="4" stroke-dasharray="8 7"/>
  </g>

  <!-- SV probe and current context -->
  <g>
    <line x1="1008" y1="164" x2="1008" y2="245" stroke="#d7d4bf" stroke-width="2" stroke-dasharray="7 5"/>
    <rect x="1000" y="240" width="16" height="30" rx="7" fill="#e7d9a4" stroke="#283b42" stroke-width="3"/>
    <text x="941" y="286" class="tiny" fill="#dff2f2">SV PROBE â€¢ __SVP_VALUE__ â€¢ ACOUSTIC RAY-PATH QC</text>
    <path d="M930 314H1044L1028 302M1044 314L1028 326" fill="none" stroke="#b9eef0" stroke-width="4"/>
    <text x="927" y="344" class="tiny" fill="#dff2f2">SURFACE CURRENT __CURRENT_VALUE__</text>
  </g>

  <!-- Telemetry is mirrored to rig and NAVALT survey consoles -->
  <g>
    <path d="M894 58Q570 4 208 52M950 63Q1072 45 1146 107" fill="none" stroke="__LINK_COLOR__" stroke-width="3" class="dash"/>
    <text x="665" y="18" text-anchor="middle" class="tiny" fill="__LINK_COLOR__">USV TELEMETRY __LINK_STATUS__ â€¢ MBES / GEMINI / LiDAR / USBL / INC-DEP</text>
  </g>

  <!-- NAVALT conceptual watchkeeping/support boat -->
  <g class="boat" filter="url(#shadow)">
    <path d="M1028 142H1248L1219 178H1051Z" fill="#f4f1e7" stroke="#34454c" stroke-width="5"/>
    <path d="M1062 141L1085 104H1182L1218 141" fill="#f7f4e8" stroke="#34454c" stroke-width="5"/>
    <path d="M1086 103H1192L1174 83H1102Z" fill="#253a48" stroke="#4a626d" stroke-width="4"/>
    <path d="M1096 87H1180M1124 87V102M1154 87V102" stroke="#4d7890" stroke-width="2"/>
    <rect x="1094" y="115" width="28" height="19" fill="#6fb4c4"/>
    <rect x="1130" y="115" width="28" height="19" fill="#6fb4c4"/>
    <rect x="1166" y="115" width="28" height="19" fill="#6fb4c4"/>
    <image href="__NAVALT_SCREEN_URI__" x="1101" y="111" width="91" height="23" preserveAspectRatio="xMidYMid slice" clip-path="url(#navScreenClip)"/>
    <rect x="1098" y="108" width="97" height="29" rx="3" fill="none" stroke="__LINK_COLOR__" stroke-width="3"/>
    <line x1="1202" y1="105" x2="1202" y2="71" stroke="#34454c" stroke-width="4"/>
    <circle cx="1202" cy="67" r="6" fill="#d85e2f"/>
    <text x="1137" y="204" text-anchor="middle" class="lab" fill="#dfeff0">NAVALT WATCHKEEPING / SUPPORT BOAT</text>
    <text x="1137" y="221" text-anchor="middle" class="tiny" fill="#cfe5e7">MODEL TBC â€¢ SURVEY MIRROR â€¢ GUARD / RECOVERY COVER</text>
  </g>

  <!-- Drawing elevations -->
  <g opacity=".86">
    <line x1="1261" y1="51" x2="1261" y2="650" stroke="#35464c" stroke-width="2"/>
    <path d="M1249 51H1273M1249 104H1273M1249 170H1273M1249 566H1273" stroke="#35464c" stroke-width="3"/>
    <text x="1238" y="45" text-anchor="end" class="tiny" fill="#26353a">EL +39.700 DRILL FLOOR</text>
    <text x="1238" y="100" text-anchor="end" class="tiny" fill="#26353a">EL +28.278 MAIN DECK</text>
    <text x="1238" y="166" text-anchor="end" class="tiny" fill="#dff2f2">MSL Â±0.000</text>
    <text x="1238" y="562" text-anchor="end" class="tiny" fill="#fff0c9">MUDLINE EL -30.800</text>
  </g>

  <text x="26" y="194" class="lab" fill="#d5eff0">WATER COLUMN</text>
  <text x="26" y="603" class="lab" fill="#f7e9c5">SEABED / FOUNDATION ZONE</text>
  <text x="26" y="678" class="tiny" fill="#efdfb8">VERTICAL PROPORTIONS ARE SCHEMATIC â€¢ SST TILT IS VISUALLY EXAGGERATED</text>
</svg>
"""


def render_scene(phase_index: int, data: dict[str, Any], usbl_host: str) -> str:
    scene = SCENE_TEMPLATE
    geometry = phase_geometry(phase_index, data, usbl_host)
    for token, value in geometry.items():
        scene = scene.replace(f"__{token}__", value)
    # SVG does not support arithmetic inside rect height. Replace with a value.
    pile_height = int(geometry["PILE_BOTTOM"]) - int(geometry["PILE_TOP"])
    scene = scene.replace(f'height="calc({geometry["PILE_BOTTOM"]} - {geometry["PILE_TOP"]})"', f'height="{pile_height}"')
    scene = scene.replace("__WAVEBOT_URI__", asset_data_uri("wavebot-real.jpg"))
    scene = scene.replace("__RIG_SCREEN_URI__", asset_data_uri("lidar-pointcloud.jpg"))
    scene = scene.replace("__NAVALT_SCREEN_URI__", asset_data_uri("gemini-template.jpg"))
    return scene


def render_gate_rows(gates: list[dict[str, str]], phase_index: int) -> str:
    rows = []
    for index, gate in enumerate(gates):
        state = gate["status"] if index <= phase_index else "PENDING"
        active = " active" if index == phase_index else ""
        rows.append(
            f'<div class="gate{active}"><span class="gnum">G{index + 1}</span>'
            f'<div><b>{html.escape(gate["name"])}</b><small>{html.escape(gate["detail"])}</small></div>'
            f'<em class="{state.lower()}">{state}</em></div>'
        )
    return "".join(rows)


def phase_evidence(phase_index: int, data: dict[str, Any], usbl_host: str) -> list[tuple[str, str, str]]:
    spread = tension_spread(data["tensions"])
    template_depth = [0.0, 2.5, 18.4, 30.8, 30.8, 30.8, 30.8, 30.8][phase_index]
    evidence = [
        [
            ("NORBIT coverage", f'{data["survey_coverage"]:.1f}%', "SIMULATED MEASUREMENT"),
            ("Sound speed / SVP", f'{data["sound_speed"]:.1f} m/s' if data["svp_valid"] else "Invalid / stale", "ACOUSTIC CORRECTION QC"),
            ("Surface current", f'{data["surface_current"]:.2f} m/s @ {data["current_direction"]}Â°', "OPERATING CONTEXT"),
        ],
        [
            ("Sling A/B/C/D", " / ".join(f"{v:.1f}" for v in data["tensions"]) + " kN", "SIMULATED MEASUREMENT"),
            ("Four-point spread", f"{spread:.1f}%", "MRSIF DERIVED"),
            ("USV LiDAR rod frame", "Valid" if data["lidar_reference"] else "Invalid", "ABOVE-WATER TO WATERLINE"),
        ],
        [
            ("DEP-01 template depth", f'{template_depth:.1f} m', "PRESSURE / DEPTH SENSOR"),
            ("Template pitch / roll", f'{data["pitch"]:.2f}Â° / {data["roll"]:.2f}Â°', "TEMPLATE INCLINOMETER"),
            ("Descent / surface current", f'{data["descent_rate"]:.2f} / {data["surface_current"]:.2f} m/s', "HOIST + CURRENT SENSOR"),
        ],
        [
            ("DEP-01 touchdown depth", f'{template_depth:.1f} m', "DEPTH + LOAD CONFIRMATION"),
            ("Touchdown pitch / roll", f'{data["pitch"]:.2f}Â° / {data["roll"]:.2f}Â°', "TEMPLATE INCLINOMETER"),
            ("Movement after set-down", f'{data["movement"]:.2f} m', "SIMULATED TREND"),
        ],
        [
            ("USBL host / beacons", f'{usbl_host} â€¢ {data["beacons"]} of 2', "ACOUSTIC OBSERVATION"),
            ("Fix uncertainty", f'Â±{data["fix_uncertainty"]:.2f} m', "SIMULATED QC"),
            ("SV correction", "Valid" if data["svp_valid"] else "Invalid / stale", "RAY-PATH QC; NOT SOIL DATA"),
        ],
        [
            ("USV Gemini interpretation", f'{data["gemini_confidence"]}% confidence', "SUBMERGED SIDE SONAR"),
            ("Pile centre offset", f'{data["pile_offset"]:.2f} m', "SIMULATED MEASUREMENT"),
            ("LiDAR / acoustic handover", "At waterline", "DUAL-DOMAIN EVIDENCE"),
        ],
        [
            ("MENCK energy setting", f'{data["hammer_energy"]} kJ', "SIMULATED HAMMER LOG"),
            ("Blow / penetration trend", f'{data["blow_rate"]}/min â€¢ {data["penetration"]} mm/10', "SIMULATED HAMMER LOG"),
            ("Surface / submerged track", "LiDAR / USBL + Gemini", "SENSOR HANDOVER"),
        ],
        [
            ("Post-install coverage", f'{data["post_coverage"]:.1f}%', "SIMULATED MEASUREMENT"),
            ("Telemetry archive", "Rig + NAVALT mirror", "USV DATA DISTRIBUTION"),
            ("Evidence records", f'{data["records"]} of 7', "MRSIF COMPLETENESS"),
        ],
    ]
    return evidence[phase_index]


def render_workspace(phase_index: int, scenario_name: str, usbl_host: str) -> str:
    data = scenario_data(scenario_name)
    phase = PHASES[phase_index]
    gates = evaluate_gates(data)
    state, controlling_gate = mission_recommendation(gates, phase_index)
    color = STATUS_COLOR[state]

    if state == "GO":
        recommendation_title = "Evidence supports controlled progression"
        recommendation_reason = phase["next"]
    elif state == "WATCH":
        recommendation_title = f'{controlling_gate["name"]} is in its watch band'
        recommendation_reason = "Continue only under active monitoring and prepare the approved corrective response before the configured limit is exceeded."
    else:
        recommendation_title = f'{controlling_gate["name"]} requires HOLD'
        recommendation_reason = controlling_gate["action"]

    evidence_html = "".join(
        f'<div class="evidence"><span>{html.escape(label)}</span><b>{html.escape(value)}</b><small>{html.escape(source)}</small></div>'
        for label, value, source in phase_evidence(phase_index, data, usbl_host)
    )

    stage_html = "".join(
        f'<div class="stage {"done" if i < phase_index else "active" if i == phase_index else ""}"><b>{p["code"]}</b><span>{html.escape(p["short"])}</span></div>'
        for i, p in enumerate(PHASES)
    )

    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
      :root{{--ink:#172228;--paper:#f4f0e7;--line:rgba(23,34,40,.18);--rig:#d6a32d;--orange:#d95f2f;--sea:#0b5368;--go:#168366;--watch:#c47d18;--hold:#b43a32}}
      *{{box-sizing:border-box}} body{{margin:0;background:#e7e5dc;color:var(--ink);font-family:'Arial Narrow','Segoe UI',Arial,sans-serif}}
      .frame{{border:1px solid var(--line);background:var(--paper);box-shadow:0 18px 45px rgba(18,31,36,.16)}}
      .head{{display:grid;grid-template-columns:1fr auto;gap:18px;padding:15px 18px;border-top:7px solid var(--ink);border-bottom:1px solid var(--line);align-items:end}}
      .kicker{{font-size:11px;font-weight:900;letter-spacing:1.7px;text-transform:uppercase;color:#0b5368;margin-bottom:5px}}
      h1{{font-size:clamp(25px,3vw,48px);line-height:.95;letter-spacing:-1.5px;text-transform:uppercase;margin:0}} h1 span{{color:#0b6478}}
      .meta{{text-align:right;font-size:11px;line-height:1.45;color:#657073}} .meta b{{display:block;color:#172228;font-size:13px}}
      .stages{{display:grid;grid-template-columns:repeat(8,1fr);background:#fffaf0;border-bottom:1px solid var(--line)}}
      .stage{{min-height:56px;padding:9px 8px;border-right:1px solid var(--line);color:#7a8282}} .stage:last-child{{border-right:0}}
      .stage b{{display:block;font-size:10px;letter-spacing:1px}} .stage span{{font-size:10px;line-height:1.15;font-weight:800;text-transform:uppercase}}
      .stage.done{{background:#e4f0eb;color:#236b57}} .stage.active{{background:#f4dfaa;color:#322918;box-shadow:inset 0 5px 0 var(--rig)}}
      .body{{display:grid;grid-template-columns:minmax(0,1.78fr) minmax(330px,.72fr);min-height:650px}}
      .scene{{background:#c9dada;border-right:1px solid var(--line);overflow:hidden}} .scene svg{{display:block;width:100%;height:auto}}
      .side{{background:#fffaf0;display:flex;flex-direction:column}}
      .status{{padding:14px 16px;color:white;background:{color}}} .status small{{font-size:9px;font-weight:900;letter-spacing:1.4px;text-transform:uppercase;opacity:.82}}
      .statusline{{display:flex;align-items:baseline;gap:10px;margin-top:4px}} .statusline strong{{font-size:28px;letter-spacing:1px}} .statusline b{{font-size:14px}}
      .status p{{margin:7px 0 0;font-size:11px;line-height:1.4}}
      .phasecopy{{padding:13px 15px;border-bottom:1px solid var(--line)}} .phasecopy small{{font-size:9px;letter-spacing:1.2px;font-weight:900;text-transform:uppercase;color:#7a715f}}
      .phasecopy h2{{font-size:17px;margin:5px 0 6px}} .phasecopy p{{font-size:11px;line-height:1.45;margin:0;color:#596466}}
      .distribution{{padding:8px 15px;background:#dcebec;border-bottom:1px solid var(--line);font-size:9px;line-height:1.35;font-weight:800;text-transform:uppercase;color:#24444d}}
      .evidencegrid{{display:grid;grid-template-columns:1fr;padding:4px 15px 8px}}
      .evidence{{display:grid;grid-template-columns:1fr auto;gap:2px 8px;padding:9px 0;border-bottom:1px solid var(--line)}}
      .evidence span{{font-size:10px;text-transform:uppercase;font-weight:800;color:#657073}} .evidence b{{font-size:12px;text-align:right}} .evidence small{{grid-column:1/-1;font-size:8px;letter-spacing:.9px;color:#947739}}
      .gates{{border-top:1px solid var(--line);margin-top:auto}}
      .gate{{display:grid;grid-template-columns:28px 1fr auto;gap:8px;padding:8px 12px;border-bottom:1px solid var(--line);align-items:start;opacity:.72}}
      .gate.active{{opacity:1;background:#f4ead3}} .gnum{{display:grid;place-items:center;width:25px;height:25px;background:#27363d;color:white;font-size:9px;font-weight:900}}
      .gate b{{display:block;font-size:10px;text-transform:uppercase}} .gate small{{display:block;margin-top:2px;color:#71797a;font-size:8px;line-height:1.25}}
      .gate em{{min-width:48px;padding:4px;color:white;font-size:8px;font-weight:900;font-style:normal;text-align:center;letter-spacing:.7px}}
      .gate em.go{{background:var(--go)}} .gate em.watch{{background:var(--watch)}} .gate em.hold{{background:var(--hold)}} .gate em.pending{{background:#778187}}
      .boundary{{padding:8px 12px;background:#26353c;color:#dbe5e5;font-size:8px;line-height:1.35;letter-spacing:.25px}}
      @media(max-width:900px){{.body{{grid-template-columns:1fr}}.scene{{border-right:0}}.stages{{grid-template-columns:repeat(4,1fr)}}.head{{grid-template-columns:1fr}}.meta{{text-align:left}}}}
    </style></head><body>
      <main class="frame">
        <header class="head"><div><div class="kicker">VODIDS | MRSIF Foundation Installation Workspace</div><h1>SST deployment &amp; <span>pile installation mission</span></h1></div><div class="meta"><b>{html.escape(scenario_name)}</b>{html.escape(phase["drawing"])}<br>OFFLINE-CAPABLE DEMO â€¢ NO LIVE EQUIPMENT CONTROL</div></header>
        <div class="stages">{stage_html}</div>
        <div class="body">
          <section class="scene">{render_scene(phase_index, data, usbl_host)}</section>
          <aside class="side">
            <div class="status"><small>MRSIF mission recommendation</small><div class="statusline"><strong>{state}</strong><b>{html.escape(recommendation_title)}</b></div><p>{html.escape(recommendation_reason)}</p></div>
            <div class="phasecopy"><small>Active mission â€¢ {phase["code"]}</small><h2>{html.escape(phase["name"])}</h2><p>{html.escape(phase["instruction"])}</p></div>
            <div class="distribution">Wavebot telemetry â†’ rig survey desk + NAVALT mirror<br>MBES â€¢ Gemini â€¢ LiDAR â€¢ USBL â€¢ INC/DEP â€¢ SV/current</div>
            <div class="evidencegrid">{evidence_html}</div>
            <div class="gates">{render_gate_rows(gates, phase_index)}</div>
            <div class="boundary">BOUNDARIES â€¢ INC-01 measures template pitch/roll, not lowering distance. DEP-01/hoist/acoustics provide depth. LiDAR stops at the waterline; Gemini/MBES/USBL provide submerged evidence. Sound velocity corrects acoustic ray paths; it is not a geotechnical seabed measurement. MRSIF does not control the hammer or certify pile capacity.</div>
          </aside>
        </div>
      </main>
    </body></html>
    """


st.markdown(
    """
    <style>
      header[data-testid="stHeader"] { background: transparent; }
      .stApp { background: #e7e5dc; }
      .block-container { max-width: 1680px; padding: .55rem .8rem 2rem; }
      div[data-testid="stHorizontalBlock"] { align-items: end; }
      div.stButton > button { border-radius: 0; min-height: 42px; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; }
      div[data-baseweb="select"] > div { border-radius: 0; }
      #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_browser_mission(scenario_name: str, usbl_host: str) -> str:
    """Pre-render all mission phases and play them locally in the browser.

    No interval calls Streamlit, so the mission does not create continuous
    WebSocket reruns. The only server rerun occurs when a Streamlit selectbox is
    deliberately changed.
    """
    asset_markers = {
        asset_data_uri("wavebot-real.jpg"): "MRSIF_WAVEBOT_ASSET",
        asset_data_uri("lidar-pointcloud.jpg"): "MRSIF_RIG_SCREEN_ASSET",
        asset_data_uri("gemini-template.jpg"): "MRSIF_NAVALT_SCREEN_ASSET",
    }
    pages: list[str] = []
    for phase_index in range(len(PHASES)):
        page = render_workspace(phase_index, scenario_name, usbl_host)
        for data_uri, marker in asset_markers.items():
            if data_uri:
                page = page.replace(data_uri, marker)
        pages.append(page)

    pages_json = json.dumps(pages).replace("</", "<\\/")
    assets_json = json.dumps(
        {
            "wavebot": asset_data_uri("wavebot-real.jpg"),
            "rig": asset_data_uri("lidar-pointcloud.jpg"),
            "navalt": asset_data_uri("gemini-template.jpg"),
        }
    ).replace("</", "<\\/")
    reference_cards = [
        ("Real Wavebot", "wavebot-real.jpg"),
        ("Dual-domain geometry", "dual-domain.jpg"),
        ("LiDAR point cloud", "lidar-pointcloud.jpg"),
        ("Gemini template view", "gemini-template.jpg"),
        ("MENCK hammering", "hammer-reference.jpg"),
    ]
    cards_html = "".join(
        f'<figure><img src="{asset_data_uri(filename)}" alt="{html.escape(label)} reference"><figcaption>{html.escape(label)}</figcaption></figure>'
        for label, filename in reference_cards
    )

    return f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
      *{{box-sizing:border-box}} body{{margin:0;background:#e7e5dc;color:#172228;font-family:'Segoe UI',Arial,sans-serif}}
      .toolbar{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:10px;background:#182a31;border-top:5px solid #d6a32d}}
      button{{appearance:none;border:1px solid #78878b;border-radius:0;background:#f4f0e7;color:#172228;padding:9px 14px;font:800 11px 'Segoe UI',sans-serif;letter-spacing:.7px;text-transform:uppercase;cursor:pointer}}
      button.primary{{background:#d6a32d;border-color:#d6a32d;color:#201d16}} button:disabled{{opacity:.38;cursor:not-allowed}}
      .phase-status{{margin-left:auto;color:#dbe9e9;font-size:11px;font-weight:800;letter-spacing:.7px;text-transform:uppercase}}
      .notice{{display:none;gap:12px;align-items:center;padding:10px 12px;background:#8e302b;color:#fff;font-size:12px;font-weight:700}}
      .notice.show{{display:flex}} .notice button{{margin-left:auto;background:#fff1df}}
      iframe{{display:block;width:100%;height:1000px;border:0;background:#e7e5dc}}
      .references{{padding:11px 12px 14px;background:#172b33;color:#eef4f2}}
      .references h2{{margin:0 0 8px;font-size:11px;letter-spacing:1.1px;text-transform:uppercase}}
      .strip{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
      figure{{margin:0;background:#0e2027;overflow:hidden}} figure img{{display:block;width:100%;height:90px;object-fit:cover;filter:saturate(.86) contrast(1.03)}}
      figcaption{{padding:6px 7px;font-size:9px;font-weight:800;letter-spacing:.5px;text-transform:uppercase}}
      @media(max-width:850px){{iframe{{height:1500px}}.strip{{grid-template-columns:repeat(2,1fr)}}.phase-status{{width:100%;margin-left:0}}}}
    </style></head><body>
      <div class="toolbar" role="toolbar" aria-label="Mission controls">
        <button id="run" class="primary" type="button">Run mission</button>
        <button id="prev" type="button">Previous</button>
        <button id="next" type="button">Next phase</button>
        <button id="reset" type="button">Reset mission</button>
        <button id="refresh" type="button">Refresh screen</button>
        <span id="phaseStatus" class="phase-status" aria-live="polite"></span>
      </div>
      <div id="notice" class="notice" role="alert">
        <span id="noticeText">No input received / connection timed out. The loaded mission remains available. Reset the mission or refresh the screen to reset the work.</span>
        <button id="dismiss" type="button">Dismiss</button>
      </div>
      <iframe id="missionFrame" title="MRSIF piling foundation mission demonstration"></iframe>
      <section class="references"><h2>Reference imagery from supplied Wavebot and subsea metrology PDFs</h2><div class="strip">{cards_html}</div></section>
      <script>
        const pages = {pages_json};
        const assets = {assets_json};
        const frame = document.getElementById("missionFrame");
        const runButton = document.getElementById("run");
        const prevButton = document.getElementById("prev");
        const nextButton = document.getElementById("next");
        const resetButton = document.getElementById("reset");
        const refreshButton = document.getElementById("refresh");
        const phaseStatus = document.getElementById("phaseStatus");
        const notice = document.getElementById("notice");
        const noticeText = document.getElementById("noticeText");
        const dismissButton = document.getElementById("dismiss");
        let phaseIndex = 0;
        let timer = null;
        let lastInput = Date.now();
        const simulateTelemetryTimeout = {json.dumps(scenario_name == "USV telemetry timeout / no input")};

        function hydratedPage(index) {{
          return pages[index]
            .replaceAll("MRSIF_WAVEBOT_ASSET", assets.wavebot)
            .replaceAll("MRSIF_RIG_SCREEN_ASSET", assets.rig)
            .replaceAll("MRSIF_NAVALT_SCREEN_ASSET", assets.navalt);
        }}
        function render() {{
          frame.srcdoc = hydratedPage(phaseIndex);
          phaseStatus.textContent = "Phase " + (phaseIndex + 1) + " of " + pages.length + " â€¢ {html.escape(usbl_host)} USBL host";
          prevButton.disabled = phaseIndex === 0;
          nextButton.disabled = phaseIndex === pages.length - 1;
          if (phaseIndex === pages.length - 1 && timer) stopMission();
        }}
        function stopMission() {{
          if (timer) window.clearInterval(timer);
          timer = null;
          runButton.textContent = "Run mission";
          runButton.classList.add("primary");
        }}
        function startMission() {{
          if (phaseIndex === pages.length - 1) phaseIndex = 0;
          render();
          timer = window.setInterval(() => {{
            if (phaseIndex < pages.length - 1) {{ phaseIndex += 1; render(); }}
            else stopMission();
          }}, 3600);
          runButton.textContent = "Pause mission";
          runButton.classList.remove("primary");
        }}
        function showNotice(message) {{ noticeText.textContent = message; notice.classList.add("show"); }}
        runButton.addEventListener("click", () => timer ? stopMission() : startMission());
        prevButton.addEventListener("click", () => {{ stopMission(); phaseIndex = Math.max(0, phaseIndex - 1); render(); }});
        nextButton.addEventListener("click", () => {{ stopMission(); phaseIndex = Math.min(pages.length - 1, phaseIndex + 1); render(); }});
        resetButton.addEventListener("click", () => {{ stopMission(); phaseIndex = 0; notice.classList.remove("show"); lastInput = Date.now(); render(); }});
        refreshButton.addEventListener("click", () => {{ try {{ window.parent.location.reload(); }} catch (error) {{ window.location.reload(); }} }});
        dismissButton.addEventListener("click", () => {{ notice.classList.remove("show"); lastInput = Date.now(); }});
        ["pointerdown", "keydown", "touchstart"].forEach((eventName) => window.addEventListener(eventName, () => {{ lastInput = Date.now(); }}, {{passive:true}}));
        window.addEventListener("offline", () => showNotice("No connection / telemetry input detected. The loaded demonstration remains available. Reset the mission or refresh the screen."));
        window.addEventListener("online", () => {{ notice.classList.remove("show"); lastInput = Date.now(); }});
        window.setInterval(() => {{
          if (Date.now() - lastInput > 15 * 60 * 1000) showNotice("No input received for 15 minutes. Reset the mission or refresh the screen to reset the work.");
        }}, 30000);
        render();
        if (simulateTelemetryTimeout) showNotice("No USV telemetry input received / connection timed out. The mission is held. Reset the mission or refresh the screen after restoring input.");
      </script>
    </body></html>
    """


selector_cols = st.columns(2)
with selector_cols[0]:
    scenario_name = st.selectbox("Demonstration scenario", options=list(SCENARIOS))
with selector_cols[1]:
    usbl_host = st.selectbox("USBL transducer host", options=["Wavebot USV", "NAVALT watchkeeping boat"])

components.html(
    render_browser_mission(scenario_name, usbl_host),
    height=1250,
    scrolling=True,
)


with st.expander("Mission basis, equipment roles and demonstration boundaries"):
    st.markdown(
        """
        **Drawing-led sequence used in this demo**

        - SST rigged below the drill deck using the hanging frame, HM drill pipe and levelling slings.
        - SST lowered to the mudline shown at approximately EL -30.800 m.
        - Lowering amount tracked by hoist payout plus pressure/depth and acoustic evidence; the template-mounted inclinometer measures pitch/roll only.
        - Touchdown, levelling and post-set-down movement monitoring using depth/load and template attitude evidence.
        - Hanging frame recovered while the SST remains on the seabed.
        - B1/B2 acoustic beacons localize the template from a selectable USBL transducer on Wavebot or the NAVALT watchkeeping boat.
        - Pile stabbed through the SST and driven using a MENCK MHU 150S.
        - Autonomous Wavebot/NORBIT iWBMS used for pre/post multibeam survey outside the controlled exclusion zone.
        - USV telemetry mirrored to the rig survey desk and NAVALT survey console.

        **Equipment roles represented**

        - **Vikra Wavebot + NORBIT iWBMS:** autonomous bathymetry, target-area surface and post-install seabed change. The supplied Wavebot brochure image is used; final payload integration and sensor offsets require verification.
        - **Tritech Gemini 1200ik:** shown side-mounted just below the Wavebot waterline and above iWBMS for submerged template/pile context. The operator selects the appropriate acoustic mode and range.
        - **Velodyne LiDAR:** shown on top of Wavebot for exposed drill-rod, hanging-frame and hammer movement down to the waterline. It is not treated as an underwater sensor; Gemini/MBES/USBL/depth evidence take over below MSL.
        - **Sound velocity + surface current:** sound velocity is used for acoustic ray-path correction/QC, not soil or geotechnical classification. Surface current is shown as an installation operating-context input.
        - **NAVALT watchkeeping boat:** conceptual survey mirror, surface guard, communications and recovery-cover vessel. The exact NAVALT vessel model must be confirmed.
        - **Structure beacons + sensors:** B1/B2 provide acoustic position evidence. INC-01 is on the SST and provides pitch/roll; DEP-01 plus hoist/acoustic evidence provides lowering depth.
        - **MENCK MHU 150S:** the OEM page lists an energy range of 15-150 kJ, recommended oil flow of 380 L/min, average operating pressure of 260 bar and 38 blows/min at recommended flow. The displayed mission readings are simulated and are not acceptance limits.

        **Connection/reset behaviour**

        - Mission playback is browser-side; it does not continuously rerun Streamlit.
        - After 15 minutes without input, or if the browser reports offline status, the demo shows a no-input/connection warning with Reset Mission and Refresh Screen actions.

        **Information still required for a project-specific release**

        1. Exact NAVALT watchkeeping boat model or GA/image.
        2. Exact Velodyne LiDAR model, mounting bracket and validated field of view.
        3. Approved USBL host, transducer offset/alignment and beacon/transponder model.
        4. Approved SST levelling, settlement, pile verticality, offset and driving review criteria.
        5. Confirm whether SST means *Subsea Support Template* for this project.
        """
    )

with st.expander("Manufacturer references used to ground the demonstration"):
    st.markdown(
        """
        - [MENCK hydraulic hammers - Acteon](https://acteon.com/solutions/project-lifecycle/offshore-construction/integrated-marine-foundation-installation-services/hydraulic-hammers)
        - [Vikra Ocean Tech - Wavebot](https://vikraoceantech.com/)
        - [NORBIT multibeam sonar systems](https://norbit.com/oceans/subsea/multibeam-sonar-systems)
        - [Tritech Gemini 1200ik](https://www.tritech.co.uk/products/gemini-1200ikd)
        - [Velodyne/Ouster VLP-16](https://ouster.com/products/hardware/vlp-16)
        - [NAVALT boats](https://navaltboats.com/)
        - [Sonardyne transponders and beacons](https://www.sonardyne.com/transponders-beacons/)
        - [Sonardyne Compatt 6+](https://www.sonardyne.com/product/compatt-6-plus/)
        """
    )
