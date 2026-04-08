# Splat Compare

Side-by-side viewer for comparing up to 3 Gaussian splat PLY files with an animated camera flythrough generated from training camera poses.

## Usage

```bash
cd ~/Documents/gaussian-splatting-projects

python3 splat-compare/viewer.py \
    --splats <ply1> [ply2] [ply3] \
    --cameras <cameras.json>
```

Opens a browser at `http://localhost:8080`. Accessible from other machines at `http://<ip>:8080`.

## Examples

```bash
# Compare iterations of the same training
python3 splat-compare/viewer.py \
    --splats output/fastgs-fullres-chunk-0/point_cloud/iteration_7000/point_cloud.ply \
             output/fastgs-fullres-chunk-0/point_cloud/iteration_30000/point_cloud.ply \
             output/fastgs-fullres-chunk-0/point_cloud/iteration_60000/point_cloud.ply \
    --cameras output/fastgs-fullres-chunk-0/cameras.json

# Compare different methods on the same dataset
python3 splat-compare/viewer.py \
    --splats output/3dgs-dublin-full/point_cloud/iteration_30000/point_cloud.ply \
             output/fastgs-dublin-full/point_cloud/iteration_30000/point_cloud.ply \
    --cameras output/3dgs-dublin-full/cameras.json

# Compare chunks
python3 splat-compare/viewer.py \
    --splats output/fastgs-fullres-chunk-0/point_cloud/iteration_60000/point_cloud.ply \
             output/fastgs-fullres-chunk-1/point_cloud/iteration_60000/point_cloud.ply \
             output/fastgs-fullres-chunk-2/point_cloud/iteration_60000/point_cloud.ply \
    --cameras output/fastgs-nwic-fullres-chunk-0/cameras.json
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--splats` | required | 1-3 PLY files to compare |
| `--cameras` | required | `cameras.json` from any training output |
| `--port` | 8080 | HTTP server port |
| `--no-browser` | false | Don't auto-open browser |

## Controls

| Key | Action |
|-----|--------|
| Space | Play / pause |
| Left / Right arrow | Step one frame |
| `[` / `]` | Decrease / increase speed |
| Progress slider | Scrub to any frame |
| Speed slider | Adjust playback rate (1-200 fps) |

## How it works

1. `viewer.py` starts a local HTTP server that serves the PLY files and `cameras.json` from their original locations (no copying)
2. The browser loads the splats using [gaussian-splats-3d](https://github.com/mkkellogg/GaussianSplats3D) (Three.js)
3. Camera poses are read from `cameras.json`, sorted by image name (capture order), and interpolated (lerp position, slerp rotation) for smooth playback

## Requirements

- Modern browser with WebGL2 (Chrome, Firefox, Edge)
- `cameras.json` from a 3DGS/FastGS/2DGS training output
- PLY files from training (any iteration checkpoint)
