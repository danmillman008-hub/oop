#!/usr/bin/env python3
"""Assemble the 60-second Lighthouse Keeper AnimDSL script from local assets/BVH."""
from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bvh_to_animdsl import (  # noqa: E402
    POSE_FIELDS, format_pose_definitions, format_track, sample_bvh_poses,
)


def pose(**overrides: float) -> dict[str, float]:
    values = {
        "line-of-action": 0.0,
        "torso-bend": 0.0,
        "torso-squash": 1.0,
        "shoulder-left": 0.0,
        "shoulder-right": 0.0,
        "arm-left-angle": 10.0,
        "arm-right-angle": -10.0,
        "elbow-left-bend": 0.05,
        "elbow-right-bend": 0.05,
        "leg-left-angle": 3.0,
        "leg-right-angle": -3.0,
        "knee-left-bend": 0.0,
        "knee-right-bend": 0.0,
        "head-tilt": 0.0,
        "head-nod": 0.0,
        "y-offset": 0.0,
        "body-angle": 0.0,
        "eyebrow-left": 0.0,
        "eyebrow-right": 0.0,
        "eye-open-left": 1.0,
        "eye-open-right": 1.0,
        "eye-direction": 0.0,
        "mouth-smile": 0.1,
        "mouth-open": 0.0,
    }
    unknown = set(overrides) - set(POSE_FIELDS)
    if unknown:
        raise ValueError(f"Unsupported AnimDSL pose fields: {sorted(unknown)}")
    values.update(overrides)
    return values


POSES = OrderedDict([
    ("gazing", pose(
        **{"body-angle": 180.0, "line-of-action": 0.04, "torso-bend": -2.0,
           "shoulder-left": 0.18, "shoulder-right": 0.18,
           "arm-left-angle": -24.0, "arm-right-angle": 24.0,
           "elbow-left-bend": 0.42, "elbow-right-bend": 0.42,
           "head-nod": -7.0, "eye-open-left": 0.92, "eye-open-right": 0.92,
           "mouth-smile": 0.0})),
    ("shielding", pose(
        **{"body-angle": 75.0, "line-of-action": 0.28, "torso-bend": -9.0,
           "torso-squash": 0.96, "shoulder-left": 0.48, "shoulder-right": 0.35,
           "arm-left-angle": -55.0, "arm-right-angle": -72.0,
           "elbow-left-bend": 0.74, "elbow-right-bend": 0.86,
           "leg-left-angle": -7.0, "leg-right-angle": 8.0,
           "knee-left-bend": 0.24, "knee-right-bend": 0.2,
           "head-nod": 12.0, "eyebrow-left": 0.58, "eyebrow-right": 0.48,
           "eye-open-left": 1.16, "eye-open-right": 1.16,
           "mouth-smile": -0.08, "mouth-open": 0.26})),
    ("lifting", pose(
        **{"body-angle": 75.0, "line-of-action": 0.38, "torso-bend": -13.0,
           "torso-squash": 0.94, "shoulder-left": -0.1, "shoulder-right": 0.56,
           "arm-left-angle": -34.0, "arm-right-angle": -142.0,
           "elbow-left-bend": 0.88, "elbow-right-bend": 0.24,
           "leg-left-angle": -13.0, "leg-right-angle": 12.0,
           "knee-left-bend": 0.48, "knee-right-bend": 0.43,
           "head-tilt": 3.0, "head-nod": -12.0, "y-offset": -4.0,
           "eyebrow-left": -0.12, "eyebrow-right": -0.12,
           "eye-open-left": 0.9, "eye-open-right": 0.9,
           "mouth-smile": -0.18, "mouth-open": 0.1})),
    ("signaling", pose(
        **{"body-angle": 75.0, "line-of-action": 0.16, "torso-bend": -3.0,
           "shoulder-left": 0.42, "shoulder-right": 0.55,
           "arm-left-angle": -58.0, "arm-right-angle": -154.0,
           "elbow-left-bend": 0.78, "elbow-right-bend": 0.08,
           "leg-left-angle": -12.0, "leg-right-angle": 12.0,
           "knee-left-bend": 0.08, "knee-right-bend": 0.08,
           "head-tilt": -2.0, "head-nod": -3.0,
           "eyebrow-left": -0.36, "eyebrow-right": -0.32,
           "eye-open-left": 0.9, "eye-open-right": 0.9,
           "eye-direction": 0.35, "mouth-smile": -0.22,
           "mouth-open": 0.06})),
    ("watching", pose(
        **{"body-angle": 70.0, "line-of-action": 0.1, "torso-bend": 5.0,
           "shoulder-left": -0.04, "shoulder-right": -0.04,
           "arm-left-angle": 9.0, "arm-right-angle": -9.0,
           "elbow-left-bend": 0.1, "elbow-right-bend": 0.1,
           "head-tilt": -2.0, "head-nod": -1.0,
           "eyebrow-left": 0.18, "eyebrow-right": 0.3,
           "eye-open-left": 1.0, "eye-open-right": 1.0,
           "eye-direction": 0.38, "mouth-smile": 0.12})),
    ("exhausted-peace", pose(
        **{"body-angle": 180.0, "line-of-action": -0.18, "torso-bend": 8.0,
           "torso-squash": 0.97, "shoulder-left": -0.42, "shoulder-right": -0.42,
           "arm-left-angle": 18.0, "arm-right-angle": -18.0,
           "elbow-left-bend": 0.18, "elbow-right-bend": 0.18,
           "leg-left-angle": 4.0, "leg-right-angle": -4.0,
           "knee-left-bend": 0.1, "knee-right-bend": 0.1,
           "head-tilt": 2.0, "head-nod": 15.0,
           "eyebrow-left": -0.15, "eyebrow-right": -0.15,
           "eye-open-left": 0.72, "eye-open-right": 0.72,
           "mouth-smile": -0.18})),
    ("grateful", pose(
        **{"body-angle": 68.0, "line-of-action": 0.08, "torso-bend": -4.0,
           "shoulder-left": 0.24, "shoulder-right": 0.0,
           "arm-left-angle": -34.0, "arm-right-angle": 8.0,
           "elbow-left-bend": 0.86, "elbow-right-bend": 0.12,
           "head-tilt": -3.0, "head-nod": -8.0,
           "eyebrow-left": 0.3, "eyebrow-right": 0.36,
           "eye-open-left": 0.96, "eye-open-right": 0.96,
           "mouth-smile": 0.72, "mouth-open": 0.02})),
    ("dashing", pose(
        **{"body-angle": 75.0, "line-of-action": 0.48, "torso-bend": -17.0,
           "torso-squash": 1.04, "shoulder-left": 0.12, "shoulder-right": 0.18,
           "arm-left-angle": 46.0, "arm-right-angle": -46.0,
           "elbow-left-bend": 0.46, "elbow-right-bend": 0.42,
           "leg-left-angle": -23.0, "leg-right-angle": 23.0,
           "knee-left-bend": 0.46, "knee-right-bend": 0.43,
           "head-tilt": 1.0, "head-nod": -5.0, "y-offset": -2.0,
           "eyebrow-left": -0.18, "eyebrow-right": -0.18,
           "eye-open-left": 0.88, "eye-open-right": 0.88,
           "mouth-smile": -0.08, "mouth-open": 0.23})),
])


def custom_pose_text() -> str:
    return "\n\n".join(format_pose_definitions([(name, values)]) for name, values in POSES.items())


def make_mocap() -> tuple[dict[str, list], dict[str, float]]:
    run = sample_bvh_poses(
        ROOT / "cmu_data" / "16_35.bvh", "mocap-run", sample_fps=24,
        start=0.05, duration=1.30, gain=0.7, body_angle=75.0,
        expression={"eyebrow-left": -0.22, "eyebrow-right": -0.22,
                    "eye-open-left": 0.9, "eye-open-right": 0.9,
                    "mouth-smile": -0.1, "mouth-open": 0.08},
    )
    lifting = sample_bvh_poses(
        ROOT / "cmu_data" / "13_11.bvh", "mocap-lift", sample_fps=12,
        start=0.05, duration=3.35, gain=0.62, body_angle=75.0,
        expression={"eyebrow-left": -0.16, "eyebrow-right": -0.16,
                    "eye-open-left": 0.91, "eye-open-right": 0.91,
                    "mouth-smile": -0.16, "mouth-open": 0.08},
    )
    signal = sample_bvh_poses(
        ROOT / "cmu_data" / "26_01.bvh", "mocap-signal", sample_fps=12,
        start=0.10, duration=3.0, gain=0.42, body_angle=75.0,
        expression={"eyebrow-left": -0.4, "eyebrow-right": -0.34,
                    "eye-open-left": 0.88, "eye-open-right": 0.88,
                    "eye-direction": 0.25, "mouth-smile": -0.24,
                    "mouth-open": 0.06},
    )
    # Keep CMU-derived torso/leg timing but use authored arm arcs. Raw 3D
    # shoulder rotations project poorly into this 2D rig and tended toward a T-pose.
    manual_arm_fields = (
        "shoulder-left", "shoulder-right", "arm-left-angle", "arm-right-angle",
        "elbow-left-bend", "elbow-right-bend",
    )
    for track, pose_name in ((lifting, "lifting"), (signal, "signaling")):
        for _name, values in track:
            for field in manual_arm_fields:
                values[field] = POSES[pose_name][field]
    return {"run": run, "lifting": lifting, "signal": signal}, {
        "run": len(run) * 2 / 24,
        "lifting": len(lifting) / 12,
        "signal": len(signal) / 12,
    }


def indent_block(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in text.splitlines())


def build_full_anim() -> tuple[str, float]:
    motions, durations = make_mocap()
    generated_defs = "\n\n".join(
        format_pose_definitions(motions[key]) for key in ("run", "lifting", "signal")
    )
    defs = custom_pose_text() + "\n\n// BVH-derived, lossy 3D-to-2D key poses (all 24 engine fields explicit).\n" + generated_defs
    run_track = format_track(motions["run"], "kai", 24, repeat=2, indent="      ")
    lift_track = format_track(motions["lifting"], "kai", 12, indent="        ")
    signal_track = format_track(motions["signal"], "kai", 12, indent="    ")

    header = '''import character kai from "assets/characters/kai.json"
import character maya from "assets/characters/maya.json"
import set lighthouse-interior from "assets/sets/lighthouse-interior.svg"
import set lighthouse-window from "assets/sets/lighthouse-window.svg"
import set lighthouse-beam from "assets/sets/lighthouse-beam.svg"
import set sea-view from "assets/sets/sea-view.svg"
import set dawn-sky from "assets/sets/dawn-sky.svg"
import prop beacon from "assets/props/beacon-lantern.svg"
import prop red-scarf from "assets/props/red-scarf.svg"

config {
  width: 1280
  height: 720
  fps: 24
  background: #111d2e
}

'''
    scenes = f'''scene "01-the-tower" (duration: 12s, set: lighthouse-interior) {{
  place kai at (0.56, 0.72) facing up layer 1
  place red-scarf at (0.56, 0.58) layer 2
  camera wide
  kai pose "gazing"
  wait 1s

  together {{
    camera zoom-to kai over 7s ease-in-out
    do {{
      wait 1s
      kai pose "watching"
    }}
  }}
  wait 2s
  transition fade-black 2s
}}

scene "02-the-storm" (duration: 15s, set: lighthouse-window) {{
  place kai at (0.18, 0.72) facing right layer 1
  place red-scarf at (0.18, 0.58) layer 2
  camera wide
  kai pose "surprised"
  wait 1s

  together {{
    kai moves-to (0.58, 0.72) over 2.8s ease-in
    red-scarf moves-to (0.58, 0.58) over 2.8s ease-in
    camera pan-to (0.58, 0.5) over 2.8s ease-out
    camera shake 2.8s intensity 2
    do {{
{run_track}
    }}
  }}
  camera medium kai
  kai pose "shielding"
  wait 2s
  kai pose "angry"
  wait 4s
  camera shake 0.5s intensity 1.5
  wait 3.7s
  transition dissolve 1s
}}

scene "03-the-signal" (duration: 18s, set: lighthouse-beam) {{
  place kai at (0.50, 0.72) facing right layer 1
  place red-scarf at (0.50, 0.58) layer 2
  place beacon at (0.46, 0.58) layer 3
  camera close-up kai
  kai pose "angry"
  wait 0.5s
  together {{
    beacon moves-to (0.47, 0.63) over 3.5s ease-out
    camera shake 0.5s intensity 8
    do {{
      kai pose "lifting"
      wait 0.083333s
{lift_track}
    }}
  }}
  camera reset over 1.5s
  camera wide
  kai pose "signaling"
  do {{
{signal_track}
  }}
  kai pose "excited"
  wait 8s
  transition wipe left 1.5s
}}

scene "04-the-rescue" (duration: 10s, set: sea-view) {{
  place kai at (0.50, 0.72) facing right layer 1
  place maya at (0.74, 0.58) facing left layer 2
  place red-scarf at (0.50, 0.58) layer 3
  camera wide
  kai pose "watching"
  maya pose "watching"
  wait 1s
  together {{
    camera pan-to (0.62, 0.50) over 5s ease-in-out
    maya moves-to (0.66, 0.72) over 5s ease-out
  }}
  kai pose "grateful"
  maya pose "grateful"
  wait 2s
  transition fade-white 2s
}}

scene "05-dawn" (duration: 5s, set: dawn-sky) {{
  place kai at (0.36, 0.72) facing up layer 1
  place maya at (0.66, 0.72) facing up layer 1
  place red-scarf at (0.36, 0.58) layer 2
  camera wide
  kai pose "exhausted-peace"
  maya pose "gazing"
  wait 1.2s
  kai pose "grateful"
  maya pose "grateful"
  wait 2.8s
  transition fade-black 1s
}}
'''
    return header + defs + "\n\n" + scenes, sum((12, 15, 18, 10, 5))


def build_scene1_preview() -> str:
    header = '''import character kai from "assets/characters/kai.json"
import set lighthouse-interior from "assets/sets/lighthouse-interior.svg"
import prop red-scarf from "assets/props/red-scarf.svg"

config {
  width: 1280
  height: 720
  fps: 24
  background: #111d2e
}

'''
    preview_scene = '''scene "scene-1-10s-preview" (duration: 10s, set: lighthouse-interior) {
  place kai at (0.56, 0.72) facing up layer 1
  place red-scarf at (0.56, 0.58) layer 2
  camera wide
  kai pose "gazing"
  wait 1s
  together {
    camera zoom-to kai over 7s ease-in-out
    do {
      wait 1s
      kai pose "watching"
    }
  }
  wait 2s
}
'''
    return header + custom_pose_text() + "\n\n" + preview_scene


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene1-preview", type=Path, help="also write the 10-second scene-one validation script")
    parser.add_argument("--output", type=Path, default=ROOT / "lighthouse" / "lighthouse.anim")
    args = parser.parse_args()
    text, duration = build_full_anim()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    if args.scene1_preview:
        args.scene1_preview.parent.mkdir(parents=True, exist_ok=True)
        args.scene1_preview.write_text(build_scene1_preview(), encoding="utf-8")
    print(f"Wrote {args.output}; target timeline {duration:.1f}s; {len(POSES)} named poses each include {len(POSE_FIELDS)} engine fields")
    if args.scene1_preview:
        print(f"Wrote 10-second first-scene test: {args.scene1_preview}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
