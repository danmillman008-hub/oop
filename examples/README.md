# Heat — diner-scene tribute

`heat-diner.anim` is an **86-second**, five-scene, dialogue-free tribute built with the repository's procedural AnimDSL characters and camera system. Hanna and McCauley are original generic cartoon interpretations, not actor likenesses. The diner set, counter, and coffee cup are original vector artwork; no film footage or audio is used.

The scene lengths are 10s, 12s, 20s, 28s, and 16s. The script defines nine custom poses, each listing all 24 fields enumerated in the current DSL specification. The supported character JSON schema is used for both figures. The table is a foreground prop that hides their lower bodies to suggest a seated conversation; the coffee cup moves independently during McCauley's sip.

The arrival approaches from the right and Hanna steps into a separate back-aisle lane before leaving left. This keeps the trajectories clear of AnimDSL's hard character-overlap check while preserving the entrance/departure beats.

## Check and render

```bash
./animdsl check examples/heat-diner.anim
python3 tools/render_animdsl_in_segments.py examples/heat-diner.anim
```

The segmented renderer uses the `.anim` file's 1280×720, 24 fps config, renders each scene in its own process to bound memory, then joins the MP4s and writes a 480px-wide, 6 fps GIF preview. FFmpeg must be on `PATH`; use `--animdsl /path/to/animdsl` if the CLI is not at the repository root.

Outputs: `heat-diner.mp4` (86 seconds, 2,064 frames) and `heat-diner-preview.gif`.
