#!/usr/bin/env python3
"""Render an AnimDSL film scene-by-scene, then join the MP4 segments."""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def split_scenes(source: str) -> tuple[str, list[tuple[str, str, float]]]:
    starts = list(re.finditer(r'^scene\s+"([^"\n]+)"', source, re.M))
    if not starts:
        raise ValueError("No scene declarations found")
    header = source[:starts[0].start()]
    scenes = []
    for match in starts:
        start = match.start()
        brace = source.find("{", match.end())
        if brace < 0:
            raise ValueError(f"Scene {match.group(1)} has no body")
        depth = 0
        quote = escaped = False
        end = None
        for i in range(brace, len(source)):
            ch = source[i]
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
                    end = i + 1
                    break
        if end is None:
            raise ValueError(f"Unclosed scene {match.group(1)}")
        block = source[start:end]
        duration = re.search(r'duration\s*:\s*([\d.]+)s', block)
        if duration is None:
            raise ValueError(f"Scene {match.group(1)} has no duration")
        scenes.append((match.group(1), block, float(duration.group(1))))
    return header, scenes


def run(command: list[str], env: dict[str, str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="AnimDSL .anim source")
    parser.add_argument("--animdsl", default=str(ROOT / "animdsl"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--gif", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=int)
    parser.add_argument("--gif-width", type=int, default=480)
    parser.add_argument("--gif-fps", type=int, default=6)
    parser.add_argument("--no-gif", action="store_true")
    args = parser.parse_args()

    source_path = args.input.resolve()
    source = source_path.read_text(encoding="utf-8")
    header, scenes = split_scenes(source)
    out = args.output.resolve() if args.output else source_path.with_suffix(".mp4")
    gif = args.gif.resolve() if args.gif else source_path.with_name(source_path.stem + "-preview.gif")
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = source_path.parent / f".render-{source_path.stem}"
    shutil.rmtree(temp, ignore_errors=True)
    temp.mkdir(parents=True)
    env = os.environ.copy()
    videos = []
    try:
        for i, (name, block, _duration) in enumerate(scenes, 1):
            script = source_path.parent / f".render-{source_path.stem}-{i:02d}.anim"
            script.write_text(header + block + "\n", encoding="utf-8")
            segment = temp / f"scene-{i:02d}.mp4"
            cmd = [args.animdsl, "render", str(script), "-o", str(segment)]
            if args.width is not None:
                cmd += ["--width", str(args.width)]
            if args.height is not None:
                cmd += ["--height", str(args.height)]
            if args.fps is not None:
                cmd += ["--fps", str(args.fps)]
            run(cmd, env)
            videos.append(segment)
            script.unlink(missing_ok=True)
        concat = temp / "concat.txt"
        concat.write_text("".join(f"file '{v.as_posix()}'\n" for v in videos), encoding="utf-8")
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(out)], env)
        if not args.no_gif:
            palette = temp / "palette.png"
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(out),
                 "-vf", f"fps={args.gif_fps},scale={args.gif_width}:-1:flags=lanczos,palettegen=stats_mode=diff",
                 "-frames:v", "1", "-update", "1", str(palette)], env)
            run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(out), "-i", str(palette),
                 "-filter_complex", f"fps={args.gif_fps},scale={args.gif_width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
                 "-loop", "0", str(gif)], env)
    finally:
        for script in source_path.parent.glob(f".render-{source_path.stem}-*.anim"):
            script.unlink(missing_ok=True)
        shutil.rmtree(temp, ignore_errors=True)
    print(f"Rendered {len(scenes)} scenes, {sum(s[2] for s in scenes):g}s total -> {out}")
    if not args.no_gif:
        print(f"GIF preview -> {gif}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
