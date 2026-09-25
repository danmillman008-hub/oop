#!/usr/bin/env python3
"""Convert selected BVH joint channels into explicit AnimDSL pose keyframes.

AnimDSL does not ingest BVH directly. This intentionally lossy 3D-to-2D map
uses the nearest existing AnimDSL controls, emits all 24 pose fields, and leaves
camera/translation/face animation to the .anim scene.
"""
from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

POSE_FIELDS = (
    "line-of-action", "torso-bend", "torso-squash", "shoulder-left",
    "shoulder-right", "arm-left-angle", "arm-right-angle", "elbow-left-bend",
    "elbow-right-bend", "leg-left-angle", "leg-right-angle", "knee-left-bend",
    "knee-right-bend", "head-tilt", "head-nod", "y-offset", "body-angle",
    "eyebrow-left", "eyebrow-right", "eye-open-left", "eye-open-right",
    "eye-direction", "mouth-smile", "mouth-open",
)

@dataclass
class Joint:
    name: str
    channels: list[str] = field(default_factory=list)
    channel_start: int = 0
    children: list["Joint"] = field(default_factory=list)

@dataclass
class BVH:
    root: Joint
    frames: list[list[float]]
    frame_time: float
    joints: dict[str, Joint]


def parse_bvh(path: Path) -> BVH:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "MOTION" not in text:
        raise ValueError(f"{path} is not a BVH file (missing MOTION section)")
    hierarchy, motion = text.split("MOTION", 1)
    tokens = re.findall(r"\{|\}|[^\s{}]+", hierarchy)
    i = 0
    if tokens and tokens[0] == "HIERARCHY":
        i += 1
    joints: dict[str, Joint] = {}
    channel_cursor = 0

    def parse_node(kind: str) -> Joint:
        nonlocal i, channel_cursor
        if kind == "end":
            name = f"EndSite{len(joints)}"
        else:
            if i >= len(tokens):
                raise ValueError("Unexpected end of BVH hierarchy")
            name = tokens[i]
            i += 1
        if i >= len(tokens) or tokens[i] != "{":
            raise ValueError(f"Expected '{{' after BVH joint {name}")
        i += 1
        node = Joint(name=name, channel_start=channel_cursor)
        joints[name] = node
        while i < len(tokens) and tokens[i] != "}":
            token = tokens[i]
            if token == "OFFSET":
                i += 4  # OFFSET and xyz; offsets are not needed by the angle map.
            elif token == "CHANNELS":
                count = int(tokens[i + 1])
                node.channels = tokens[i + 2:i + 2 + count]
                node.channel_start = channel_cursor
                channel_cursor += count
                i += 2 + count
            elif token == "JOINT":
                i += 1
                node.children.append(parse_node("joint"))
            elif token == "End":
                i += 2  # End Site
                node.children.append(parse_node("end"))
            else:
                raise ValueError(f"Unexpected BVH hierarchy token {token!r}")
        if i >= len(tokens):
            raise ValueError(f"Unclosed BVH joint {name}")
        i += 1
        return node

    if i >= len(tokens) or tokens[i] != "ROOT":
        raise ValueError("BVH hierarchy must begin with ROOT")
    i += 1
    root = parse_node("root")

    frame_count = None
    frame_time = None
    rows: list[list[float]] = []
    for line in motion.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Frames:"):
            frame_count = int(line.split(":", 1)[1])
        elif line.startswith("Frame Time:"):
            frame_time = float(line.split(":", 1)[1])
        else:
            rows.append([float(value) for value in line.split()])
    if frame_count is None or frame_time is None:
        raise ValueError("BVH motion is missing Frames or Frame Time")
    if len(rows) != frame_count:
        raise ValueError(f"BVH declares {frame_count} frames but contains {len(rows)}")
    if rows and any(len(row) != channel_cursor for row in rows):
        raise ValueError(f"BVH frame width does not match {channel_cursor} channels")
    return BVH(root, rows, frame_time, joints)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _channel(bvh: BVH, frame: list[float], joint_name: str, channel_name: str) -> float:
    node = bvh.joints.get(joint_name)
    if node is None or channel_name not in node.channels:
        return 0.0
    return frame[node.channel_start + node.channels.index(channel_name)]


def sample_bvh_poses(
    path: Path,
    prefix: str,
    sample_fps: int = 24,
    start: float = 0.0,
    duration: float | None = None,
    gain: float = 0.7,
    body_angle: float = 75.0,
    expression: dict[str, float] | None = None,
) -> list[tuple[str, dict[str, float]]]:
    if sample_fps <= 0:
        raise ValueError("sample_fps must be positive")
    bvh = parse_bvh(path)
    clip_duration = len(bvh.frames) * bvh.frame_time
    if start < 0 or start >= clip_duration:
        raise ValueError(f"start {start}s lies outside {clip_duration:.3f}s clip")
    duration = min(duration if duration is not None else clip_duration - start, clip_duration - start)
    count = max(1, math.ceil(duration * sample_fps - 1e-9))
    root_y_channel = "Yposition"
    root_ys = [_channel(bvh, f, "Hips", root_y_channel) for f in bvh.frames]
    root_mean = sum(root_ys) / max(1, len(root_ys))
    gain = _clamp(gain, 0.0, 1.5)
    expression = expression or {}
    poses: list[tuple[str, dict[str, float]]] = []

    for frame_index in range(count):
        t = start + frame_index / sample_fps
        source_index = min(len(bvh.frames) - 1, round(t / bvh.frame_time))
        frame = bvh.frames[source_index]
        rot = lambda joint, axis: _channel(bvh, frame, joint, axis + "rotation")
        root_y = _channel(bvh, frame, "Hips", "Yposition")
        spine = rot("Spine", "Z") + 0.5 * rot("Spine1", "Z")
        left_upper = rot("LeftUpLeg", "Z")
        right_upper = rot("RightUpLeg", "Z")
        values = {
            "line-of-action": _clamp(spine / 45.0 * gain, -0.8, 0.8),
            "torso-bend": _clamp(spine * gain, -30.0, 30.0),
            "torso-squash": _clamp(1.0 + (root_y - root_mean) * 0.0015, 0.92, 1.08),
            "shoulder-left": _clamp(rot("LeftShoulder", "Z") / 90.0 * gain, -0.8, 0.8),
            "shoulder-right": _clamp(rot("RightShoulder", "Z") / 90.0 * gain, -0.8, 0.8),
            "arm-left-angle": _clamp(rot("LeftArm", "Z") * gain, -110.0, 110.0),
            "arm-right-angle": _clamp(rot("RightArm", "Z") * gain, -110.0, 110.0),
            "elbow-left-bend": _clamp(abs(rot("LeftForeArm", "Z")) / 145.0 * gain, 0.0, 1.0),
            "elbow-right-bend": _clamp(abs(rot("RightForeArm", "Z")) / 145.0 * gain, 0.0, 1.0),
            "leg-left-angle": _clamp(left_upper * gain, -55.0, 55.0),
            "leg-right-angle": _clamp(right_upper * gain, -55.0, 55.0),
            "knee-left-bend": _clamp(abs(rot("LeftLeg", "X")) / 130.0 * gain, 0.0, 0.95),
            "knee-right-bend": _clamp(abs(rot("RightLeg", "X")) / 130.0 * gain, 0.0, 0.95),
            "head-tilt": _clamp(rot("Head", "Z") * 0.55 * gain, -18.0, 18.0),
            "head-nod": _clamp(rot("Head", "X") * 0.55 * gain, -18.0, 18.0),
            "y-offset": _clamp((root_y - root_mean) * 0.06, -2.5, 2.5),
            "body-angle": body_angle,
            "eyebrow-left": 0.0,
            "eyebrow-right": 0.0,
            "eye-open-left": 1.0,
            "eye-open-right": 1.0,
            "eye-direction": 0.0,
            "mouth-smile": 0.0,
            "mouth-open": 0.0,
        }
        # A supplied expression overrides the neutral mocap face; BVH has no face channels.
        for key, value in expression.items():
            if key not in values or key not in {
                "eyebrow-left", "eyebrow-right", "eye-open-left", "eye-open-right",
                "eye-direction", "mouth-smile", "mouth-open",
            }:
                raise ValueError(f"{key!r} is not an AnimDSL expression field")
            values[key] = value
        poses.append((f"{prefix}-{frame_index:03d}", values))
    return poses


def format_pose(name: str, values: dict[str, float], indent: str = "") -> str:
    missing = set(POSE_FIELDS) - set(values)
    extra = set(values) - set(POSE_FIELDS)
    if missing or extra:
        raise ValueError(f"Pose {name}: missing={sorted(missing)}, unsupported={sorted(extra)}")
    lines = [f'{indent}pose "{name}" {{']
    for field_name in POSE_FIELDS:
        value = values[field_name]
        if abs(value) < 0.0005:
            value = 0.0
        lines.append(f"{indent}  {field_name}: {value:.4f}")
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def format_pose_definitions(poses: Iterable[tuple[str, dict[str, float]]]) -> str:
    return "\n\n".join(format_pose(name, values) for name, values in poses)


def format_track(
    poses: list[tuple[str, dict[str, float]]],
    entity: str,
    sample_fps: int,
    repeat: int = 1,
    indent: str = "    ",
) -> str:
    step = 1.0 / sample_fps
    lines: list[str] = []
    for _ in range(repeat):
        for name, _values in poses:
            lines.append(f'{indent}{entity} pose "{name}"')
            lines.append(f"{indent}wait {step:.6f}s")
    return "\n".join(lines)


def parse_expression(items: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"expression override must be field=value, got {item!r}")
        key, raw = item.split("=", 1)
        out[key] = float(raw)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--entity", default="kai")
    parser.add_argument("--sample-fps", type=int, default=24)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--gain", type=float, default=0.7)
    parser.add_argument("--body-angle", type=float, default=75.0)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--expression", action="append", default=[], metavar="FIELD=VALUE")
    parser.add_argument("--definitions-out", type=Path)
    parser.add_argument("--track-out", type=Path)
    args = parser.parse_args()
    poses = sample_bvh_poses(
        args.input, args.prefix, args.sample_fps, args.start, args.duration,
        args.gain, args.body_angle, parse_expression(args.expression),
    )
    definitions = format_pose_definitions(poses) + "\n"
    track = format_track(poses, args.entity, args.sample_fps, args.repeat) + "\n"
    if args.definitions_out:
        args.definitions_out.parent.mkdir(parents=True, exist_ok=True)
        args.definitions_out.write_text(definitions, encoding="utf-8")
    else:
        print(definitions, end="")
    if args.track_out:
        args.track_out.parent.mkdir(parents=True, exist_ok=True)
        args.track_out.write_text(track, encoding="utf-8")
    print(f"// {len(poses)} BVH-derived pose keyframes; action track duration {len(poses) * args.repeat / args.sample_fps:.3f}s", file=__import__("sys").stderr)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
