"""MRSIF - realistic pile foundation installation mission demonstration.

Run locally:
    python -m pip install streamlit
    streamlit run mrsif_piling_realistic.py

This release contains embedded fallback images and therefore works when only
this Python file is copied to a repository. Higher-resolution images from the
optional assets/mrsif_piling folder are used automatically when available.
All values and limits are simulated examples and require project approval.
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
EMBEDDED_ASSETS: dict[str, str] = {
    "wavebot-real.jpg": "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",
    "dual-domain.jpg": "/9j/4AAQSkZJRgABAQIAIQAhAAD/2wBDABUOEBIQDRUSERIYFhUZHzQiHx0dH0AuMCY0TENQT0tDSUhUXnlmVFlyWkhJaY9qcnyAh4iHUWWUn5ODnXmEh4L/2wBDARYYGB8cHz4iIj6CVklWgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoL/wAARCAC0AL8DASIAAhEBAxEB/8QAGgABAAMBAQEAAAAAAAAAAAAAAAECAwUEBv/EADcQAAEEAAMEBwcEAgMBAAAAAAEAAgMRBBIhMUFRgRMiMmFxsdEjM1KRkqHBFEJy8AVTNEPhYv/EABgBAQEBAQEAAAAAAAAAAAAAAAABAgME/8QAIREBAQACAgMBAAMBAAAAAAAAAAECERIxIUFhAxMiMlH/2gAMAwEAAhEDEQA/APl0RFtkREQa4eV0UgcDsXuf1miSPsn7HguYvVhJwwlr9WO0IWpXLPH3GmY76KWPhC0kjyniDqCN6zpVzmjq/D90pnA/NKSkF2xNLcwulIhaTVlGA9Ga4hSWhure1v7kQdCCf3DQbkdCL/ds4KJtX8ld9ZsrtnHgh5UELe9W6JpAGv8AeSgNLGu4qpaHDM0a7wg1ewB1htnvtQGnIdLs7TaqRmkyHZx4K4a0My043vRka0k6gXxDdVOR7n0Dd+KoW5CMu071OIeIg5rtCe0eA4Knd8KYnrRmOM9Ub6Op4rxdA4nbfIqXEyxuobxQQERENGryRZ4dyw9GM4zTN7Cw0VpF/wAeXl5rOX3rvFaQ+4l5eaRb0xRECjYiIgIDSIg9+EmEjehedf2k7jwV3Mymiuc12U2upDIMRFr7xo17xxW55efPHjdxlSUrltJSM7Sxwa2q27UaWZgSKUUopEaODSdSNiPLNpFnuVXDXkEcNeQVRPSDLlrTwUgsDc4BBulSlavZD+Sgtp0oBGvGlNtseiV7cf3cjQAC52jW7T+FUJHsgY2RwsnsivuvHLIyWSQPsltnZt+6jGTGV8ZOmmg4C1mffT+BWbXbDDU3UNmYwENbV93/AKoD4tuTX+96yRR21FpHNc62iuK2gF4eY8K8151pDO+AksI10IIsFIlnjwzREUaEREBERAWsEzonhzTRCyRVLNuxbZYxIwaHQjgVSl5MFiOifR1adCOK6D2jQg206g8VueXkynG6ZUlK9KKRNjhryChw15BXcNeQRw15BE2zpWr2XNTS1yXEG6XdoWoazNOK/ui8WMnDnCNnYb9zxXrxL3RSZGVr2z+FzTG9zr0+aldPzm/NUk16Lw/Kk++n8CrPid7PQEDbr3q4YelmOlOBA71l33HkRCCCQdoRRsREQSTZUIiAiIgIiICIiADS6OBxAPspDodhO4rnKWkh1qy6YzxmU07bmlpoqtKuDmE8eR3baNO8LQhdHiu5dUcNeQUOGvIK5GvII4a8gibUAUYiX9MzNfXOjRw71oMrRnfo0H5nguTipJZpC5zTr3KW6dMMeV+Lsmc7GdZxokjasSTm7R+a1Z0bMQK67ydu4KhleXXpr3LD0z4TOc2ONtns3t71R73CS8x3b1rM5r2s6XQ5dHDdqspGOzmgSOIG3RFirxT3eKqrSAjLYokKqjUEREUQItGwyGIyhvUaaJ+XqgzRWdG5rGvNU7UaqHNLHFrhqNCghFszDTSNDmtsHZqj8LMxhc5tAC9qm4m2KIiqiIiDSGR0bwWmiDtXbw5GJZmYOtWo4FcFrHO2Be//ABeIfBOG3QdobCznlZjdM/xzLKWui9haRd2QEy2bJoAWSdyiPFQhjRPZcBWg2arL/JuIgb0RuNwBJ/Cv553X9nn/AE/L+2sXhx2K6V2VujG7PVeJWIcdaVVre3oxxmM00w/v2JvCYf37FNahC9om7MfgfNZhazdmPwPmslFnQiIiiIiDo5MD8cv0j1Uj9IG5RLLl4ZRXn3Lm2lrHD6xx+ukThCwMMkmUbsjfVHDBvJLpJCTtORvqubZS1OH04/XVbLh2NDWzSgAUOqPVHS4d7S180pB29Ueq5Vpafx/Tg6OTA/HL9I9UyYH45fpHquclq8Ppx+ujkwPxy/SPVMmB+OT6R6rnWlpw+nH668Yw/ROEL5GkEWarS6/K0lc1j8pZGCxxO3euXh8RJFmDNjhRBC7OEw+JEccnTAiWqsHqg7/s75FccsLK7Y9dvC0Rs7BP1qwnLdAXHlfmvc4TNa5z5Q0huaq26gH76ckxMczWPa+Y5QDRa07rvf3K7v8AxOM3vbziSMRO/UBzQ4UG0L8aXmy4Lc+T6R6rzYyN0WIkjLy/K4iyKtedbxw97Zym3VhZgulbT5L/AIj1TLgrFvk+keq52HPt2eKmzmGqcbvtnh9e+VmDplvkqtOqOPiqZMD8cv0j1XjmJyx+B81lasxtnacNe3RyYH45fpHqmTA/HL9I9VzrSyrw+nH66OTA/HL9I9UyYH45fpHquclpw+nH6IERbbEREBERAREQEAsovZgcN0r8ztGDaVnLKYzdWTdbYDCCulkHVGwcSt5o7a6ibpbFw0AFAaADcqk2vHcrbt3kkmgxYZhe4yknKSKlOzh4lVdGzpXNZI57KAzFxOZWLRfIIaB04BW52zSTHSs2GbPFlA642Hj3LjSMLHEELuBywxuHEzDI0dcdoce9a/PPjdUyx305mG9+zxT9wUwDLiGXxT9wXp9uJN2I/wCJ81ktZuzH/E+ayVnRRERVBERARSSSVCAiIgIiICItIY3SPDQCSdyW6F8LA6aQAfM7l1eqxgYzsj796oxrYI8jdSe0eKguXkzy5V3xnGL2otVtRaxpdtnHXkFDjryCq52vIKHHXkPJNLta1LXEGwVnaZk0m1JsMOlbMwdW9RwK557QXXgd7QA6g6EcV4sXh+ieHN1YdhXX88/OqxlPceWbsx+B81ktZ+zH4HzWS9GPTnRERVBERAREQKREQERSBaA1pcV1IIxh47I9oR9I9VlhIREwSvGv7QfNWc8uNlefPLl4jrjNeVibS1S0tZ0u17S1S0tNG2zj1uQ8lDzryHkqvPW5DyUPPW5DyUkXabS1S0tXSbbQn2rVoC14LH6tP271hCfatTNqs2eV282PhMRY07gdRv1XkXXka2aJrHUDRynhr5LlyxmN5BFEbl3/ADy3NVzyntRERdWBEXqwIizPdKzOGtsA8bCluptZNvKiIqgiKfBBAFr2YTDgjpH9gfc8FnhoTK/U0BqTwC9UjqAaOq0aAErlnl6jeM9okkLnaqlqLbvJ5JbdwvmsSLtNoozD4QmbuA5KiVPNVznu+SvHbnamhvKipeesfAeSOOvIeS0cGOebe4HQbO5VlNNa5pJ0F2pFUvTaoUZz/Qmfw+SumWsPvWqu8KYX+1boNqjM29R91PapeTTPA+aSxjER2PeNH1D1USkZY9o0PmkZo2HD50n0c9zaKhdHFRNkZ0jRR/cPyvCWHXRdsctxizSi9GE2Sfx/IWOTiaW+Gy5ZP4/kJnfCY9vMpAChT/di2hQUtAtR/dikKDoE9Hh2tYOq4WSN5/8AF5ifFVixDo7AOh2g7CthLC/tNyn/AOXfgrlqx03tki2yREaSgfyHonQE9lzD4OCbiaY3zVgesBe0q5w8gHuzXcLUCF4eLa4a8Fdw8tg6PQCNodZGxDmF5XNFamgFFiNhptvLjR3ALFpc12bf371iRp6Ac7mucW3fE6nTuUZnuGjmhrRVUNBzUNYLYWVTnbOGxYvIDRGyi0bTxKSD0AMDm52tNnh6LCVzbDmANBvQeKvA+iGyC2eRWk0MRw8XQhzpQDnG7km9XydxhC8CVpJoXtV8mu3mNQsxBIf+t3yKn9O4bab4uAWrpEzuAyNBBIGteKzDlp0bP3St5WUuFuwPefCgksGmHkc1wygm91bV5sUA2VwZsvipdinBuVjQxp4b+a85NnYbVxx87S3xovvW+F1bJqez+QvPpwXowpNSfx/IW8uknbzpaItMlpZRECzxU5jSIgkHqk7FOc0ERRVs7gNFYTyDY8jmURZ1FWGJm/2O+ZVhiZvjKIs6i7WbjJgCM32UDES/GURSSG6h2Im/2O+aocRL/sd8yiLWomyWRzmNeTqSbWOYoiuMK9WDeaeeBA8bK9AFFzQT1nAE3rw/CIsXtqdMZpXNLJKBJY40RY3D8LcULkAAc4Ek130iKVYxe4OjltjNG6HLqq/41jXmUOF9T8hES/4qe3//2Q==",
    "lidar-pointcloud.jpg": "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",
    "gemini-template.jpg": "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",
    "hammer-reference.jpg": "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",
}


def asset_data_uri(filename: str) -> str:
    """Return a local or embedded mission image without using a network URL."""
    if filename in _ASSET_CACHE:
        return _ASSET_CACHE[filename]
    path = ASSET_DIR / filename
    if path.exists():
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    else:
        encoded = EMBEDDED_ASSETS.get(filename, "")
    if not encoded:
        return ""
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
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
        "instruction": "Wavebot follows an autonomous survey line outside the installation exclusion zone. NORBIT iWBMS establishes the pre-install seabed surface, while sound-velocity and current sensors provide acoustic-correction and operational inputs.",
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
        "instruction": "Lower the SST through the water column while monitoring four-point tension, hoist payout and DEP-01 depth. The template-mounted inclinometer measures pitch and roll; it does not measure lowering distance. Gemini and acoustic positioning take over below the waterline.",
        "next": "Continue to the set-down window under the approved lowering procedure.",
    },
    {
        "code": "04",
        "name": "Touchdown & template levelling",
        "short": "Set down & level",
        "drawing": "Drawing 1 - SST at mudline",
        "instruction": "Confirm mudline contact using depth and load evidence. Unload the lifting system in a controlled manner, then use the template-mounted inclinometer to verify pitch, roll and movement after set-down.",
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
        "instruction": "Run the post-install autonomous Wavebot/NORBIT survey, confirm the final template attitude and consolidate MBES, Gemini, LiDAR, beacon, current, sound-velocity and driving records into the MRSIF work reference.",
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
    <text x="95" y="37" class="tiny" fill="#26353a">RIG SURVEY DESK â€¢ LIVE USV DATA</text>
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
      <text x="716" y="96" class="tiny" fill="#fff0cd">INC-01 â€¢ PITCH + ROLL</text>
    </g>
  </g>
  <text x="600" y="__TEMPLATE_LABEL_Y__" text-anchor="end" class="lab" fill="#fff0c8">SST â€¢ DEPTH __TEMPLATE_DEPTH__ m â€¢ INC-01 ON TEMPLATE</text>

  <!-- USBL transducer may be hosted from Wavebot or watchkeeping boat -->
  <g opacity="__ACOUSTIC_OPACITY__">
    <rect x="__USBL_X__" y="174" width="16" height="24" rx="6" fill="#f0c65b" stroke="#28373d" stroke-width="3"/>
    <path d="M__USBL_X__ 198 Q800 328 543 __TEMPLATE_Y__ M__USBL_X__ 198 Q850 345 727 __TEMPLATE_Y__" fill="none" stroke="#f2c85f" stroke-width="3" class="dash"/>
    <text x="860" y="232" text-anchor="middle" class="tiny" fill="#ffeab3">USBL HOST â€¢ __USBL_HOST__</text>
  </g>

  <!-- Tritech Gemini is side-mounted on Wavebot, just submerged and above iWBMS -->
  <g opacity="__GEMINI_OPACITY__" class="pulse">
    <path d="M825 184 Q735 260 660 __TEMPLATE_Y__ Q770 400 840 194Z" fill="url(#sonarFan)" stroke="#f2b84a" stroke-width="2"/>
    <path d="M828 188Q760 280 690 __TEMPLATE_Y__M828 188Q790 330 735 __TEMPLATE_Y__" fill="none" stroke="#ffdc86" stroke-width="2" opacity=".7"/>
    <text x="742" y="270" class="tiny" fill="#ffe6a7">GEMINI IMAGE â€¢ TEMPLATE + PILE</text>
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
    <text x="787" y="154" class="lab" fill="#f4e7c8">VIKRA WAVEBOT â€¢ AUTO USV</text>
  </g>

  <!-- Velodyne on top of USV; rays stop at the waterline -->
  <g opacity="__LIDAR_OPACITY__">
    <ellipse cx="914" cy="44" rx="15" ry="7" fill="#27363b" stroke="#d45e2f" stroke-width="4"/>
    <rect x="907" y="29" width="14" height="14" fill="#465155"/>
    <path d="M914 45L633 91L775 169L1010 169Z" fill="#e4ca52" opacity=".13" stroke="#e4ca52" stroke-width="2"/>
    <path d="M914 45L635 91M914 45L778 169M914 45L1008 169" stroke="#f1d963" stroke-width="2" stroke-dasharray="6 5"/>
    <text x="820" y="33" class="tiny" fill="#26353a">VELODYNE LiDAR â€¢ ABOVE-WATER TRACKING</text>
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
    <text x="941" y="286" class="tiny" fill="#dff2f2">SOUND VELOCITY â€¢ __SVP_VALUE__ â€¢ ACOUSTIC QC</text>
    <path d="M930 314H1044L1028 302M1044 314L1028 326" fill="none" stroke="#b9eef0" stroke-width="4"/>
    <text x="927" y="344" class="tiny" fill="#dff2f2">SURFACE CURRENT __CURRENT_VALUE__</text>
  </g>

  <!-- Telemetry is mirrored to rig and NAVALT survey consoles -->
  <g>
    <path d="M894 58Q570 4 208 52M950 63Q1072 45 1146 107" fill="none" stroke="__LINK_COLOR__" stroke-width="3" class="dash"/>
    <text x="665" y="18" text-anchor="middle" class="tiny" fill="__LINK_COLOR__">USV TELEMETRY __LINK_STATUS__ â€¢ RIG + WATCHKEEPING BOAT</text>
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
    <text x="1137" y="221" text-anchor="middle" class="tiny" fill="#cfe5e7">MODEL TBC â€¢ SURVEY DISPLAY â€¢ SAFETY COVER</text>
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
