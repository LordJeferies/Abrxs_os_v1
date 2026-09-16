from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

from brand_engine import BrandStore, build_brand_ai_package, safe_slug

APP_VERSION = "1.0.0"
DEFAULT_DATA = Path.home() / "ABRXOS_BRAND_BUILDER_DATA"
DEFAULT_EXPORTS = Path.home() / "ABRXOS_BRAND_BUILDER_EXPORTS"
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RESOURCES = BASE_DIR / "resources"
DEFAULT_WEB = BASE_DIR / "web"


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or "0")
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8"))


def _handler_factory(data_root: Path, export_root: Path, resources_dir: Path, web_dir: Path):
    store = BrandStore(data_root)
    export_root.mkdir(parents=True, exist_ok=True)

    class Handler(BaseHTTPRequestHandler):
        server_version = "ABRXOSBrandBuilder/1.0"

        def log_message(self, fmt, *args):
            if os.environ.get("ABRXOS_HTTP_LOG") == "1":
                super().log_message(fmt, *args)

        def _json(self, obj, status=200):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _text_file(self, path: Path):
            if not path.exists() or not path.is_file():
                self.send_error(404); return
            data = path.read_bytes()
            ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text/") else ""))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers(); self.wfile.write(data)

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/api/health":
                return self._json({"ok": True, "app": "ABRXOS X Brand Builder", "version": APP_VERSION})
            if path == "/api/brands":
                return self._json({"ok": True, "brands": store.list()})
            if path.startswith("/api/brand/"):
                slug = unquote(path.split("/api/brand/", 1)[1])
                try:
                    return self._json({"ok": True, "project": store.load(slug)})
                except FileNotFoundError:
                    return self._json({"ok": False, "error": "Brand not found"}, 404)
            if path == "/api/method-registry":
                p = resources_dir / "branding_method_registry.json"
                if not p.exists(): return self._json({"ok": False, "error": "Method registry missing"}, 500)
                return self._json({"ok": True, "registry": json.loads(p.read_text(encoding="utf-8"))})
            if path == "/api/adapter-template":
                p = resources_dir / "brand_adapter_template.json"
                if not p.exists(): return self._json({"ok": False, "error": "Adapter template missing"}, 500)
                return self._json({"ok": True, "template": json.loads(p.read_text(encoding="utf-8"))})
            if path.startswith("/resources/"):
                rel = Path(unquote(path[len("/resources/"):]))
                if rel.is_absolute() or ".." in rel.parts: return self.send_error(400)
                return self._text_file(resources_dir / rel)
            rel = path.lstrip("/") or "index.html"
            relp = Path(unquote(rel))
            if relp.is_absolute() or ".." in relp.parts: return self.send_error(400)
            return self._text_file(web_dir / relp)

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                obj = _read_json(self)
                if path == "/api/brand/save":
                    saved = store.save(obj)
                    return self._json({"ok": True, "slug": saved["slug"], "project": saved["project"]})
                if path == "/api/brand/delete":
                    return self._json({"ok": store.delete(obj.get("slug", ""))})
                if path == "/api/export":
                    saved = store.save(obj)
                    result = build_brand_ai_package(saved["project"], export_root, resources_dir)
                    return self._json({"ok": True, **result})
                if path == "/api/reference/upload":
                    raw = base64.b64decode(obj.get("base64", ""), validate=True)
                    meta = store.save_reference(obj.get("slug") or obj.get("brandId") or "brand", obj.get("filename") or "reference.bin", raw)
                    return self._json({"ok": True, "reference": meta})
                if path == "/api/import/adapter":
                    project = obj.get("project") or {}
                    imported = obj.get("adapter") or {}
                    project["brandAdapterDraft"] = imported
                    saved = store.save(project)
                    return self._json({"ok": True, "project": saved["project"]})
                return self._json({"ok": False, "error": "Unknown endpoint"}, 404)
            except Exception as exc:
                return self._json({"ok": False, "error": str(exc)}, 400)

    return Handler


def make_server(host="127.0.0.1", port=0, data_root=DEFAULT_DATA, export_root=DEFAULT_EXPORTS, resources_dir=DEFAULT_RESOURCES, web_dir=DEFAULT_WEB):
    handler = _handler_factory(Path(data_root), Path(export_root), Path(resources_dir), Path(web_dir))
    return ThreadingHTTPServer((host, int(port)), handler)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--data-root", default=str(DEFAULT_DATA))
    ap.add_argument("--export-root", default=str(DEFAULT_EXPORTS))
    args = ap.parse_args()
    server = make_server(args.host, args.port, Path(args.data_root), Path(args.export_root), DEFAULT_RESOURCES, DEFAULT_WEB)
    url = f"http://{args.host}:{server.server_address[1]}/"
    print(url, flush=True)
    if not args.no_open:
        threading.Timer(0.35, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
