from __future__ import annotations

import argparse
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

from .library import Library
from .migrate_library import migrate_legacy_library
from .registry import RendererRegistry, CatalogRegistry
from .server import create_server


def prepare_library(data_dir: Path) -> Library:
    data_dir = Path(data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    legacy = data_dir / 'library.json'
    target = data_dir / 'library_v3.json'
    if not target.exists() and legacy.exists():
        migrate_legacy_library(legacy, target)
    return Library(target)


def find_port(host: str = '127.0.0.1', start: int = 8973) -> int:
    for port in range(start, start + 80):
        sock = socket.socket()
        try:
            sock.bind((host, port))
            sock.close()
            return port
        except OSError:
            sock.close()
    raise RuntimeError('No hay puerto local libre para Geometra V3.')


def run(root: Path, data_dir: Path, port: int | None = None, open_browser: bool = True) -> None:
    root = Path(root).resolve()
    library = prepare_library(data_dir)
    renderers = RendererRegistry(root / 'renderers')
    catalogs = CatalogRegistry(root / 'catalogs')
    host = '127.0.0.1'
    chosen = port or find_port(host)
    server = create_server((host, chosen), library, renderers, catalogs, root)
    url = f'http://{host}:{chosen}/'

    if open_browser:
        def opener():
            time.sleep(0.35)
            try:
                if sys.platform == 'darwin':
                    subprocess.Popen(['open', url])
                else:
                    webbrowser.open(url)
            except Exception:
                webbrowser.open(url)
        threading.Thread(target=opener, daemon=True).start()

    print(f'ABRXOS GEOMETRA V3 · {url}')
    print(f'Datos: {Path(data_dir).expanduser()}')
    try:
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='ABRXOS Geometra V3 · Kernel + Renderer Packs')
    parser.add_argument('--port', type=int)
    parser.add_argument('--data-dir', default=str(Path.home() / 'ABRXOS_GEOMETRA_DATA'))
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    run(root, Path(args.data_dir), args.port, not args.no_browser)


if __name__ == '__main__':
    main()
