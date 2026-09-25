#!/usr/bin/env python3
"""Make a short 2D walk-with-dog clip using CMU BVH 02_01 for the human gait.

Requires: Python 3, numpy, Pillow, ffmpeg.
The dog is a hand-drawn procedural character; CMU 02_01 is human mocap.
"""
from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Joint:
    name: str
    kind: str
    offset: np.ndarray = field(default_factory=lambda: np.zeros(3))
    channels: list[str] = field(default_factory=list)
    children: list["Joint"] = field(default_factory=list)
    channel_start: int = -1


def parse_bvh(path: Path):
    text = path.read_text(errors="replace")
    hierarchy, motion = text.split("MOTION", 1)
    tokens = re.findall(r"\{|\}|[^\s{}]+", hierarchy)
    i = 0
    if tokens[i] == "HIERARCHY":
        i += 1

    def parse_joint(kind: str) -> Joint:
        nonlocal i
        if kind == "end":
            name = f"EndSite{i}"
        else:
            name = tokens[i]
            i += 1
        node = Joint(name=name, kind=kind)
        if tokens[i] != "{":
            raise ValueError(f"Expected '{{' after {name}, found {tokens[i]!r}")
        i += 1
        while tokens[i] != "}":
            token = tokens[i]
            if token == "OFFSET":
                node.offset = np.asarray([float(x) for x in tokens[i + 1:i + 4]])
                i += 4
            elif token == "CHANNELS":
                count = int(tokens[i + 1])
                node.channels = tokens[i + 2:i + 2 + count]
                i += 2 + count
            elif token == "JOINT":
                i += 1
                node.children.append(parse_joint("joint"))
            elif token == "End":
                i += 2  # End Site
                node.children.append(parse_joint("end"))
            else:
                raise ValueError(f"Unexpected hierarchy token: {token}")
        i += 1
        return node

    if tokens[i] != "ROOT":
        raise ValueError("BVH hierarchy has no ROOT")
    i += 1
    root = parse_joint("root")

    channels: list[tuple[Joint, str]] = []

    def assign_channels(node: Joint):
        if node.channels:
            node.channel_start = len(channels)
            channels.extend((node, ch) for ch in node.channels)
        for child in node.children:
            assign_channels(child)

    assign_channels(root)
    rows = motion.splitlines()
    frame_count = int(next(line.split(":", 1)[1] for line in rows if line.startswith("Frames:")))
    frame_time = float(next(line.split(":", 1)[1] for line in rows if line.startswith("Frame Time:")))
    frame_rows = [line.strip() for line in rows if line.strip() and not line.startswith("Frames:") and not line.startswith("Frame Time:")]
    frames = np.asarray([[float(v) for v in row.split()] for row in frame_rows], dtype=np.float64)
    if len(frames) != frame_count or frames.shape[1] != len(channels):
        raise ValueError(f"BVH frame dimensions mismatch: {frames.shape}, expected {frame_count}x{len(channels)}")
    return root, frames, frame_time


def rotation(axis: str, degrees: float) -> np.ndarray:
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    if axis == "X":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "Y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def forward_kinematics(root: Joint, values: np.ndarray) -> dict[str, np.ndarray]:
    points: dict[str, np.ndarray] = {}

    def visit(node: Joint, parent_pos=None, parent_rot=None):
        local_rot = np.eye(3)
        translation = np.zeros(3)
        for k, channel in enumerate(node.channels):
            value = values[node.channel_start + k]
            if channel.endswith("position"):
                translation["XYZ".index(channel[0])] = value
            else:
                local_rot = local_rot @ rotation(channel[0], value)
        if parent_pos is None:
            pos = node.offset + translation
            world_rot = local_rot
        else:
            pos = parent_pos + parent_rot @ node.offset
            world_rot = parent_rot @ local_rot
        points[node.name] = pos
        for child in node.children:
            visit(child, pos, world_rot)

    visit(root)
    return points


W, H, FPS = 960, 540, 24
SCALE = 10.5
GROUND = 452


def font(size: int):
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def background(t: float) -> Image.Image:
    im = Image.new("RGB", (W, H))
    pix = im.load()
    top = (244, 190, 133)
    bottom = (255, 233, 186)
    for y in range(H):
        q = min(1.0, y / 390)
        col = tuple(round(top[c] * (1 - q) + bottom[c] * q) for c in range(3))
        for x in range(W):
            pix[x, y] = col
    d = ImageDraw.Draw(im)
    # Late-afternoon sun and layered, low hills.
    d.ellipse((756, 65, 862, 171), fill=(255, 231, 159))
    d.polygon([(0, 330), (110, 275), (230, 325), (370, 260), (525, 326), (685, 274), (850, 326), (960, 285), (960, 440), (0, 440)], fill=(194, 137, 104))
    d.polygon([(0, 365), (155, 315), (300, 365), (445, 300), (595, 366), (760, 318), (960, 365), (960, 455), (0, 455)], fill=(157, 122, 89))
    # Sandy trail and scrub.
    d.rectangle((0, 414, W, H), fill=(211, 168, 112))
    d.polygon([(0, 468), (170, 440), (400, 455), (650, 432), (960, 460), (960, 540), (0, 540)], fill=(226, 190, 136))
    for x in range(32, W, 73):
        y = 409 + (x * 7 % 24)
        d.line((x, y, x - 5, y - 14), fill=(102, 112, 66), width=3)
        d.line((x, y, x + 8, y - 11), fill=(118, 120, 69), width=3)
    # Small distant clouds.
    for x, y in ((150, 105), (440, 135), (630, 80)):
        shift = int(8 * math.sin(t * .18 + x))
        d.ellipse((x + shift, y, x + 44 + shift, y + 15), fill=(255, 232, 205))
        d.ellipse((x + 12 + shift, y - 8, x + 38 + shift, y + 15), fill=(255, 232, 205))
    return im


def screen_point(p: np.ndarray, root_p: np.ndarray, base_x: float, scale: float = SCALE):
    # CMU's +Z is forward; blend in a little lateral X for a readable 3/4 side view.
    sx = base_x + ((p[2] - root_p[2]) + 0.30 * (p[0] - root_p[0])) * scale
    sy = GROUND - p[1] * scale
    return (int(round(sx)), int(round(sy)))


def draw_human(draw: ImageDraw.ImageDraw, pose: dict[str, np.ndarray], base_x: float):
    root_p = pose["Hips"]
    q = {name: screen_point(pose[name], root_p, base_x) for name in pose if not name.startswith("EndSite")}
    hip = q["Hips"]
    # Soft ground shadow.
    draw.ellipse((hip[0] - 45, GROUND - 7, hip[0] + 55, GROUND + 6), fill=(139, 103, 72))
    back = ("RightUpLeg", "RightLeg", "RightFoot", "RightToeBase", "RightShoulder", "RightArm", "RightForeArm", "RightHand")
    front = ("LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand")
    def limb(a, b, color, width):
        if a not in q or b not in q:
            return
        draw.line((q[a], q[b]), fill=(59, 49, 45), width=width + 4)
        draw.line((q[a], q[b]), fill=color, width=width)
        r = max(3, width // 2)
        for p in (q[a], q[b]):
            draw.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color, outline=(59,49,45), width=2)
    # Far limbs first, then jacket/torso, then near limbs.
    for chain, col, width in [
        (("RightUpLeg", "RightLeg", "RightFoot", "RightToeBase"), (84, 91, 102), 13),
        (("RightShoulder", "RightArm", "RightForeArm", "RightHand"), (139, 79, 61), 10),
    ]:
        for a, b in zip(chain, chain[1:]): limb(a, b, col, width)
    # Torso as a warm jacket around the mocap spine.
    neck = q["Neck"]
    spine = q["Spine1"]
    lower = q["Hips"]
    d = draw
    jacket = [(neck[0]-17, neck[1]+3), (neck[0]+17, neck[1]+3), (spine[0]+22, spine[1]+15), (lower[0]+18, lower[1]-2), (lower[0]-18, lower[1]-2), (spine[0]-22, spine[1]+15)]
    d.polygon(jacket, fill=(151, 80, 57), outline=(59,49,45))
    # belt / trousers waist
    d.line((lower[0]-17, lower[1]-1, lower[0]+17, lower[1]-1), fill=(57,57,59), width=5)
    for chain, col, width in [
        (("LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"), (54, 67, 83), 15),
        (("LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"), (170, 96, 67), 11),
    ]:
        for a, b in zip(chain, chain[1:]): limb(a, b, col, width)
    # Neck and head.
    hx, hy = q["Head"]
    d.line((q["Neck"], (hx, hy + 10)), fill=(59,49,45), width=15)
    d.line((q["Neck"], (hx, hy + 10)), fill=(211, 157, 116), width=11)
    d.ellipse((hx-16, hy-18, hx+18, hy+17), fill=(222, 174, 133), outline=(59,49,45), width=3)
    # Hair and simple nose facing forward/right.
    d.pieslice((hx-18, hy-20, hx+18, hy+17), 180, 355, fill=(73, 53, 43))
    d.ellipse((hx+12, hy-1, hx+18, hy+4), fill=(59,49,45))
    # Boots at the mocap toe joints.
    for toe in ("LeftToeBase", "RightToeBase"):
        if toe in q:
            x, y = q[toe]
            d.rounded_rectangle((x-2, y-3, x+24, y+5), radius=3, fill=(73, 51, 42), outline=(49,39,35), width=2)
    # Return the wrist used for the leash.
    return q["LeftHand"]


def draw_dog(draw: ImageDraw.ImageDraw, center_x: float, t: float):
    phase = 2 * math.pi * (t * 1.25)
    ground = GROUND
    bob = 3 * math.sin(2 * phase)
    # Tail wag sits behind the body.
    tail_tip = (int(center_x - 63 + 14 * math.sin(phase * 1.2)), int(ground - 105 + 11 * math.cos(phase * 1.2)))
    draw.line(((int(center_x-53), int(ground-91+bob)), (int(center_x-75), int(ground-116+bob)), tail_tip), fill=(68,48,38), width=9, joint="curve")
    draw.line(((int(center_x-53), int(ground-91+bob)), (int(center_x-75), int(ground-116+bob)), tail_tip), fill=(177,111,66), width=5, joint="curve")
    # Far legs behind torso, then torso and near legs.
    def leg(x0, phase_offset, color):
        p = phase + phase_offset
        stride = 22 * math.sin(p)
        lift = 18 * max(0.0, math.cos(p))
        hip = (int(x0), int(ground-64+bob))
        knee = (int(x0 + stride*.45), int(ground-35-lift*.45+bob))
        paw = (int(x0 + stride), int(ground-lift+bob))
        draw.line((hip, knee, paw), fill=(78,54,42), width=12, joint="curve")
        draw.line((hip, knee, paw), fill=color, width=8, joint="curve")
        draw.ellipse((paw[0]-9, paw[1]-4, paw[0]+9, paw[1]+4), fill=(116,72,48), outline=(69,48,38), width=2)
    leg(center_x-32, math.pi, (157,96,56))
    leg(center_x+32, 0, (157,96,56))
    # Rounded body.
    draw.ellipse((int(center_x-61), int(ground-119+bob), int(center_x+50), int(ground-51+bob)), fill=(182,119,72), outline=(68,48,38), width=4)
    # chest patch
    draw.ellipse((int(center_x+7), int(ground-105+bob), int(center_x+46), int(ground-57+bob)), fill=(231,194,144))
    leg(center_x-27, 0, (191,127,78))
    leg(center_x+36, math.pi, (191,127,78))
    # Neck, head, muzzle, floppy ear.
    draw.ellipse((int(center_x+25), int(ground-143+bob), int(center_x+76), int(ground-91+bob)), fill=(191,127,78), outline=(68,48,38), width=4)
    draw.ellipse((int(center_x+62), int(ground-126+bob), int(center_x+98), int(ground-101+bob)), fill=(226,190,147), outline=(68,48,38), width=3)
    draw.ellipse((int(center_x+85), int(ground-120+bob), int(center_x+94), int(ground-112+bob)), fill=(53,43,39))
    draw.ellipse((int(center_x+48), int(ground-143+bob), int(center_x+67), int(ground-111+bob)), fill=(105,65,49), outline=(68,48,38), width=2)
    draw.ellipse((int(center_x+72), int(ground-117+bob), int(center_x+77), int(ground-112+bob)), fill=(55,42,36))
    # Collar and leash ring.
    collar_y = int(ground-104+bob)
    draw.arc((int(center_x+32), int(ground-145+bob), int(center_x+74), int(ground-98+bob)), 55, 160, fill=(69,115,119), width=8)
    collar = (int(center_x+43), collar_y)
    draw.ellipse((collar[0]-5, collar[1]-5, collar[0]+5, collar[1]+5), fill=(235,203,130), outline=(68,48,38), width=2)
    # Small neckerchief for a friendly, readable silhouette.
    draw.polygon([(int(center_x+32), int(ground-108+bob)), (int(center_x+53), int(ground-103+bob)), (int(center_x+37), int(ground-82+bob))], fill=(183,76,58), outline=(95,52,42))
    return collar


def make_frame(pose, t, title_font, small_font):
    im = background(t)
    d = ImageDraw.Draw(im)
    # A soft path line gives the characters a stable ground plane.
    d.line((0, GROUND+2, W, GROUND+2), fill=(145, 111, 75), width=2)
    base_x = 288 + 100 * (t / 5.74)
    leash_hand = draw_human(d, pose, base_x)
    collar = draw_dog(d, base_x + 145, t)
    # Leash is drawn last so it remains visible over the characters.
    mx = (leash_hand[0] + collar[0]) // 2
    my = (leash_hand[1] + collar[1]) // 2 - 18
    d.line((leash_hand, (mx, my), collar), fill=(70, 61, 52), width=3, joint="curve")
    # Titles and a restrained attribution.
    d.rounded_rectangle((24, 22, 303, 76), radius=16, fill=(255, 246, 226))
    d.text((42, 31), "A LITTLE WALK", font=title_font, fill=(75, 57, 48))
    d.text((30, 510), "Human gait: CMU Graphics Lab Mocap · Subject 02 / Trial 01", font=small_font, fill=(78, 63, 51))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bvh", type=Path, default=Path("cmu_data/02_01.bvh"))
    ap.add_argument("--output", type=Path, default=Path("walk-with-dog-cmu.mp4"))
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()
    root, frames, frame_time = parse_bvh(args.bvh)
    poses = [forward_kinematics(root, row) for row in frames]
    cycle = len(frames) * frame_time
    duration = 2 * cycle
    frame_count = int(round(duration * FPS))
    cmd = [args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-profile:v", "baseline", "-level:v", "3.1", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20", "-movflags", "+faststart", str(args.output)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    title_font = font(25)
    small_font = font(13)
    try:
        for i in range(frame_count):
            t = i / FPS
            source_pos = (t % cycle) / frame_time
            i0 = int(source_pos) % len(poses)
            i1 = (i0 + 1) % len(poses)
            alpha = source_pos - int(source_pos)
            names = poses[i0].keys()
            pose = {name: poses[i0][name] * (1 - alpha) + poses[i1][name] * alpha for name in names}
            image = make_frame(pose, t, title_font, small_font)
            proc.stdin.write(image.tobytes())
        proc.stdin.close()
        code = proc.wait()
        if code:
            raise RuntimeError(f"ffmpeg exited with status {code}")
    except Exception:
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
        proc.kill()
        raise
    print(f"Wrote {args.output} ({frame_count} frames, {duration:.2f}s, {W}x{H} @ {FPS}fps)")
    print("Human motion: CMU Graphics Lab Motion Capture Database, Subject 02 Trial 01.")
    print("Dog gait is procedural illustration, not captured CMU animal motion.")


if __name__ == "__main__":
    main()
