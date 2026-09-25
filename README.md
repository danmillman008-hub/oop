# CMU mocap walk-with-dog demo

A short, side-view 2D animation driven by an actual human walking sequence from the CMU Graphics Lab Motion Capture Database (Subject 02, Trial 01). The BVH joints are projected into a simple illustrated scene and looped twice. The dog and its gait are hand-drawn/procedural; CMU 02_01 is human motion capture, not a dog recording. This is a generic figure, not a likeness of a specific person.

## Files

- `walk-with-dog-cmu.mp4` — 5.73-second H.264 Baseline preview, 960×540 at 24 fps.
- `walk-with-dog-cmu.gif` — compact animated preview.
- `walk_with_dog.py` — BVH parser and small renderer.
- `cmu_data/02_01.bvh` — the short CMU walking clip used by the renderer.
- `cmu_data/README.md` — source and terms/attribution note.

## Regenerate

Install Python dependencies and make sure `ffmpeg` with `libx264` is available on `PATH`:

```bash
python3 -m pip install -r requirements-walk.txt
python3 walk_with_dog.py
```

The default command reads `cmu_data/02_01.bvh` and writes `walk-with-dog-cmu.mp4`. Use `--bvh`, `--output`, or `--ffmpeg` to override those paths.

## Attribution

Human gait data: CMU Graphics Lab Motion Capture Database, Subject 02, Trial 01. The CMU database requests acknowledgement of the source and NSF funding; details are in [`cmu_data/README.md`](cmu_data/README.md) and at [mocap.cs.cmu.edu](https://mocap.cs.cmu.edu/).
