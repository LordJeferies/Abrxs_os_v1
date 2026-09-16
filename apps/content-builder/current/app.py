from __future__ import annotations

import argparse,json,mimetypes,os,threading,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,unquote

from content_engine import ContentStore, build_content_ai_package, PROMPTS

APP_VERSION='1.0.0'
BASE_DIR=Path(__file__).resolve().parent
DEFAULT_DATA=Path.home()/'ABRXOS_CONTENT_BUILDER_DATA'
DEFAULT_EXPORTS=Path.home()/'ABRXOS_CONTENT_BUILDER_EXPORTS'
DEFAULT_RESOURCES=BASE_DIR/'resources'/'canon_r6'
DEFAULT_WEB=BASE_DIR/'web'


def _read_json(h):
    n=int(h.headers.get('Content-Length') or 0); raw=h.rfile.read(n) if n else b'{}'; return json.loads(raw.decode('utf-8'))


def _handler_factory(data_root:Path,export_root:Path,resources_dir:Path,web_dir:Path):
    store=ContentStore(data_root); export_root.mkdir(parents=True,exist_ok=True)
    class H(BaseHTTPRequestHandler):
        server_version='ABRXOSContentBuilder/1.0'
        def log_message(self,fmt,*args):
            if os.environ.get('ABRXOS_HTTP_LOG')=='1': super().log_message(fmt,*args)
        def _json(self,obj,status=200):
            b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(b)
        def _file(self,p:Path):
            if not p.exists() or not p.is_file(): self.send_error(404); return
            b=p.read_bytes(); ct=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'; self.send_response(200); self.send_header('Content-Type',ct+('; charset=utf-8' if ct.startswith('text/') else '')); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-cache'); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            path=urlparse(self.path).path
            if path=='/api/health': return self._json({'ok':True,'app':'ABRXOS Content Builder','version':APP_VERSION})
            if path=='/api/drafts': return self._json({'ok':True,'drafts':store.list_drafts()})
            if path.startswith('/api/draft/'):
                try:return self._json({'ok':True,'draft':store.load_draft(unquote(path.split('/api/draft/',1)[1]))})
                except FileNotFoundError:return self._json({'ok':False,'error':'Draft not found'},404)
            if path=='/api/library/brands': return self._json({'ok':True,'items':store.list_library('brand')})
            if path=='/api/library/projects': return self._json({'ok':True,'items':store.list_library('project')})
            if path=='/api/cases': return self._json({'ok':True,'cases':PROMPTS})
            if path.startswith('/resources/'):
                rel=Path(unquote(path[len('/resources/'):]))
                if rel.is_absolute() or '..' in rel.parts:return self.send_error(400)
                return self._file(resources_dir/rel)
            rel=Path(unquote(path.lstrip('/') or 'index.html'))
            if rel.is_absolute() or '..' in rel.parts:return self.send_error(400)
            return self._file(web_dir/rel)
        def do_POST(self):
            path=urlparse(self.path).path
            try:
                obj=_read_json(self)
                if path=='/api/draft/save':
                    s=store.save_draft(obj); return self._json({'ok':True,'slug':s['slug'],'draft':s['draft']})
                if path=='/api/draft/delete': return self._json({'ok':store.delete_draft(obj.get('slug',''))})
                if path=='/api/library/brand':
                    s=store.save_library('brand',obj); return self._json({'ok':True,**s})
                if path=='/api/library/project':
                    s=store.save_library('project',obj); return self._json({'ok':True,**s})
                if path=='/api/export':
                    s=store.save_draft(obj); result=build_content_ai_package(s['draft'],export_root,resources_dir); return self._json({'ok':True,**result})
                return self._json({'ok':False,'error':'Unknown endpoint'},404)
            except Exception as exc:return self._json({'ok':False,'error':str(exc)},400)
    return H


def make_server(host='127.0.0.1',port=0,data_root=DEFAULT_DATA,export_root=DEFAULT_EXPORTS,resources_dir=DEFAULT_RESOURCES,web_dir=DEFAULT_WEB):
    return ThreadingHTTPServer((host,int(port)),_handler_factory(Path(data_root),Path(export_root),Path(resources_dir),Path(web_dir)))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=0); ap.add_argument('--no-open',action='store_true'); ap.add_argument('--data-root',default=str(DEFAULT_DATA)); ap.add_argument('--export-root',default=str(DEFAULT_EXPORTS)); a=ap.parse_args()
    s=make_server(a.host,a.port,Path(a.data_root),Path(a.export_root),DEFAULT_RESOURCES,DEFAULT_WEB); url=f'http://{a.host}:{s.server_address[1]}/'; print(url,flush=True)
    if not a.no_open:threading.Timer(.35,lambda:webbrowser.open(url)).start()
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()

if __name__=='__main__':main()
