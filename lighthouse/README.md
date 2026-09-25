# «نگهبان فانوس» — The Lighthouse Keeper

A five-scene AnimDSL short, authored at **1280×720, 24 fps**, with a total duration of **60 seconds (1,440 frames)**.

## Deliverables

- `lighthouse.anim` — editable 60-second timeline (12s + 15s + 18s + 10s + 5s).
- `scene1-preview.anim` — standalone 10-second first-scene staging test.
- `lighthouse-keeper-60s.mp4` — final H.264 film, 1280×720, 24 fps, 60 seconds.
- `lighthouse-keeper-preview.gif` — compact 640px-wide, 8 fps preview.
- `assets/sets/` — five original, layered SVG backgrounds.
- `assets/characters/` — complete supported character descriptions for Kai and Maya.
- `assets/props/` — lantern and scarf SVG props.
- `../tools/build_lighthouse_anim.py` — reproducible timeline and pose builder.
- `../tools/bvh_to_animdsl.py` — standard-library BVH parser and lossy pose mapper.
- `../tools/render_lighthouse.py` — scene-at-a-time render/concat helper, to keep peak memory below the full-film frame buffer.

## Scene plan

| Scene | Duration | Main beats |
| --- | ---: | --- |
| Lighthouse interior | 12s | Kai watches the storm through the tower window; slow camera push and fade. |
| Storm | 15s | CMU-derived run, lightning/rain artwork, camera pan and shake, shielding and alarm. |
| Signal | 18s | Kai raises the lantern, turns toward the beacon, and holds the signal. |
| Rescue | 10s | Maya leaves the rescue boat and joins Kai; grateful expressions and white fade. |
| Dawn | 5s | Kai and Maya together at sunrise; final fade. |

## Build, check, render

From the repository root (FFmpeg must be on `PATH`):

```bash
python3 tools/generate_lighthouse_assets.py
python3 tools/build_lighthouse_anim.py --scene1-preview lighthouse/scene1-preview.anim
./animdsl check lighthouse/scene1-preview.anim
./animdsl check lighthouse/lighthouse.anim
python3 tools/render_lighthouse.py
```

The renderer retains every frame of one scene in memory, so the helper renders the five scenes as separate videos, then joins their identical H.264 streams without re-encoding. The final timeline remains continuous and its five scene durations still total exactly 60 seconds.

## Mocap and constraints

The converter maps CMU BVH rotations and root bob to AnimDSL's supported 24 custom-pose fields. It is **not direct BVH playback**: the 3D-to-2D projection is lossy, and BVH has no facial channels, so expressions are authored separately. Clips `16_35`, `13_11`, and `26_01` contribute motion to the run, lift, and signal beats. CMU-derived torso/leg timing is retained for the lift and signal, while their arm arcs are manually authored because the raw shoulder mapping produced an unconvincing, near-T-pose silhouette. The storm run translates well; the lift/signal read clearly but remain simplified.

AnimDSL also has no prop-to-hand/bone attachment, so the lantern is positioned and moved as an independent prop near Kai's hand; a slight gap can remain as the arm moves. Camera `zoom-to` uses the engine's fixed close-up multiplier (2.5×), rather than an arbitrary zoom level; the scene-1 push therefore finishes tighter than a true medium shot. The renderer supplies procedural idle, walk, and secondary hair/clothing motion; custom poses do not provide arbitrary joint/socket animation. A pose starts with the renderer's built-in 0.3-second transition from idle.

Of the other requested clip names, `02_01`, `09_01`, and `111_05` are present locally but were not selected for these beats; `02_05` is not in the local `cmu_data/` directory. Source database attribution is required:

> The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.
