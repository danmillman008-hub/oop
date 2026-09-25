#!/usr/bin/env python3
"""Render the Lighthouse Keeper one scene at a time to keep peak memory bounded."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANIM = ROOT / "lighthouse" / "lighthouse.anim"


def split_scenes(source: str) -> tuple[str, list[tuple[str, str]]]:
    starts = list(re.finditer(r'^scene\s+"([^"\n]+)"', source, re.M))
    if not starts:
        raise ValueError("No scene declarations found")
    header = source[:starts[0].start()]
    results = []
    for i, match in enumerate(starts):
        start = match.start()
        brace = source.find("{", match.end())
        if brace < 0:
            raise ValueError(f"Scene {match.group(1)} has no body")
        depth = 0
        quote = False
        escaped = False
        end = None
        for j in range(brace, len(source)):
            ch = source[j]
            if quote:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    quote = False
                continue
            if ch == '"':
                quote = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end is None:
            raise ValueError(f"Unclosed scene {match.group(1)}")
        results.append((match.group(1), source[start:end]))
    return header, results


def run(command: list[str], env: dict[str, str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--animdsl", default=os.environ.get("ANIMDSL", str(ROOT / "animdsl")))
    parser.add_argument("--output", type=Path, default=ROOT / "lighthouse" / "lighthouse-keeper-60s.mp4")
    parser.add_argument("--gif", type=Path, default=ROOT / "lighthouse" / "lighthouse-keeper-preview.gif")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--gif-width", type=int, default=640)
    parser.add_argument("--gif-fps", type=int, default=8)
    parser.add_argument("--no-gif", action="store_true")
    args = parser.parse_args()
    source = ANIM.read_text(encoding="utf-8")
    header, scenes = split_scenes(source)
    if len(scenes) != 5:
        raise ValueError(f"Expected 5 scenes, got {len(scenes)}")
    env = os.environ.copy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmpdir = ROOT / "lighthouse" / ".render_tmp"
    shutil.rmtree(tmpdir, ignore_errors=True)
    tmpdir.mkdir(parents=True)
    list_path = tmpdir / "concat.txt"
    segments = []
    try:
        for index, (name, scene) in enumerate(scenes, 1):
            scene_source = tmpdir.parent / f".render-scene-{index:02d}.anim"
            scene_source.write_text(header + scene + "\n", encoding="utf-8")
            segment = tmpdir / f"scene-{index:02d}.mp4"
            run([
                args.animdsl, "render", str(scene_source),
                "--width", str(args.width), "--height", str(args.height), "--fps", str(args.fps),
                "--output", str(segment),
            ], env)
            segments.append(segment)
            scene_source.unlink(missing_ok=True)
        list_path.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments), encoding="utf-8")
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0",
            "-i", str(list_path), "-c", "copy", "-movflags", "+faststart", str(args.output),
        ], env)
        if not args.no_gif:
            palette = tmpdir / "palette.png"
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(args.output),
                "-vf", f"fps={args.gif_fps},scale={args.gif_width}:-1:flags=lanczos,palettegen=stats_mode=diff",
                "-frames:v", "1", "-update", "1", str(palette),
            ], env)
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(args.output), "-i", str(palette),
                "-filter_complex", f"fps={args.gif_fps},scale={args.gif_width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                "-loop", "0", str(args.gif),
            ], env)
    finally:
        for path in (ROOT / "lighthouse").glob(".render-scene-*.anim"):
            path.unlink(missing_ok=True)
        shutil.rmtree(tmpdir, ignore_errors=True)
    print(f"Rendered {len(scenes)} scenes ({sum((12, 15, 18, 10, 5))}s target) to {args.output}")
    if not args.no_gif:
        print(f"GIF preview: {args.gif}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
