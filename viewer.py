#!/usr/bin/env python3
"""
Splat Compare - view up to 3 gaussian splats side by side with animated camera flythrough.

Usage:
    python3 splat-compare/viewer.py \
        --splats output/model/point_cloud/iteration_7000/point_cloud.ply \
                 output/model/point_cloud/iteration_30000/point_cloud.ply \
                 output/model/point_cloud/iteration_60000/point_cloud.ply \
        --cameras output/model/cameras.json

    python3 splat-compare/viewer.py \
        --splats output/chunk-0/point_cloud/iteration_60000/point_cloud.ply \
                 output/chunk-1/point_cloud/iteration_60000/point_cloud.ply \
                 output/chunk-2/point_cloud/iteration_60000/point_cloud.ply \
        --cameras output/chunk-0/cameras.json
"""

import argparse
import json
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


def make_handler(routes, serve_dir):
    """Create an HTTP handler that maps specific URL paths to local files."""

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=serve_dir, **kwargs)

        def do_GET(self):
            path = urlparse(self.path).path
            if path in routes:
                self._serve_mapped(routes[path])
            else:
                super().do_GET()

        def _serve_mapped(self, file_path):
            try:
                size = os.path.getsize(file_path)
                self.send_response(200)
                ext = Path(file_path).suffix.lower()
                types = {
                    '.ply': 'application/octet-stream',
                    '.json': 'application/json',
                    '.html': 'text/html',
                }
                self.send_header('Content-Type', types.get(ext, 'application/octet-stream'))
                self.send_header('Content-Length', str(size))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except Exception as e:
                self.send_error(500, str(e))

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(
        description='Compare gaussian splats side by side with camera flythrough'
    )
    parser.add_argument('--splats', nargs='+', required=True,
                        help='PLY files to compare (1-3)')
    parser.add_argument('--cameras', required=True,
                        help='cameras.json from training output')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    if len(args.splats) > 3:
        print('Error: maximum 3 splats supported', file=sys.stderr)
        sys.exit(1)

    # Resolve and verify all paths
    splat_paths = []
    for s in args.splats:
        p = Path(s).resolve()
        if not p.exists():
            print(f'Error: not found: {p}', file=sys.stderr)
            sys.exit(1)
        splat_paths.append(str(p))

    cameras_path = str(Path(args.cameras).resolve())
    if not Path(cameras_path).exists():
        print(f'Error: not found: {cameras_path}', file=sys.stderr)
        sys.exit(1)

    # Build URL-to-file route map
    routes = {'/cameras.json': cameras_path}
    labels = []
    for i, sp in enumerate(splat_paths):
        routes[f'/splat/{i}.ply'] = sp
        parent = Path(sp).parent.name
        if parent.startswith('iteration_'):
            labels.append(parent.replace('iteration_', 'iter '))
        else:
            labels.append(Path(sp).stem)

    # Write config for the frontend
    viewer_dir = str(Path(__file__).parent)
    config = {'labels': labels, 'numSplats': len(splat_paths)}
    config_path = os.path.join(viewer_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f)
    routes['/config.json'] = config_path

    # Start server
    handler = make_handler(routes, viewer_dir)
    server = HTTPServer(('0.0.0.0', args.port), handler)

    url = f'http://localhost:{args.port}'
    print(f'Splat Compare: {url}')
    for i, label in enumerate(labels):
        print(f'  [{i}] {label} ({os.path.getsize(splat_paths[i]) / 1e6:.1f} MB)')
    print(f'  Cameras: {Path(cameras_path).name}')
    print('  Ctrl+C to stop\n')

    if not args.no_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nDone.')


if __name__ == '__main__':
    main()
