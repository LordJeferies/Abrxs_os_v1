from __future__ import annotations
import json, mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from typing import Any
from .core import import_text, piece_id
from .compiler import compile_lienzo
# ABRXOS_PATCH:R6_SERVER_IMPORTS
import copy as _abrxos_r6_copy
from .r6 import validate_r6_project, load_r6_libraries
_R6_LIBRARIES = load_r6_libraries(Path(__file__).resolve().parents[1] / "r6")
_ABRXOS_IMPORT_TEXT_V3 = import_text
_ABRXOS_COMPILE_LIENZO_V3 = compile_lienzo

def _r6_annotate_project(project):
    doc = _abrxos_r6_copy.deepcopy(project)
    report = validate_r6_project(doc, _R6_LIBRARIES)
    doc["r6Validation"] = report
    doc["r6Version"] = "R6" if report.get("r6Detected") else "LEGACY_COMPAT"
    return doc

def import_text(name, text):
    return _r6_annotate_project(_ABRXOS_IMPORT_TEXT_V3(name, text))

def compile_lienzo(project, *args, **kwargs):
    return _ABRXOS_COMPILE_LIENZO_V3(_r6_annotate_project(project), *args, **kwargs)
# /ABRXOS_PATCH:R6_SERVER_IMPORTS


def _summary(p: dict[str,Any]):
    return {'projectId':p.get('projectId'),'title':p.get('title'),'pieces':len(p.get('pieces') or []),'revision':p.get('revision') or {}}


class GeometraHTTPServer(ThreadingHTTPServer):
    def __init__(self,address,handler,library,renderers,catalogs,root):
        super().__init__(address,handler);self.library=library;self.renderers=renderers;self.catalogs=catalogs;self.root=Path(root)


class Handler(BaseHTTPRequestHandler):
    def log_message(self,fmt,*args): return
    def _send(self,status:int,body:bytes,ctype='application/json; charset=utf-8',extra=None):
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        for k,v in (extra or {}).items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
    def json(self,obj,status=200):self._send(status,json.dumps(obj,ensure_ascii=False).encode(), 'application/json; charset=utf-8')
    def body(self):
        n=int(self.headers.get('Content-Length','0') or 0);return json.loads(self.rfile.read(n).decode('utf-8')) if n else {}
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/state':
            lib=self.server.library;current=lib.current();self.json({'ok':True,'state':{'projects':[_summary(p) for p in lib.list()],'currentProjectId':lib.data.get('currentProjectId'),'current':current,'renderers':self.server.renderers.list(),'catalogs':{k:self.server.catalogs.list(k) for k in ('xr','sfx','motion','captions')}}});return
        # ABRXOS_PATCH:R6_SERVER_STATIC
        if path == '/r6_patch.js':
            file = self.server.root / 'app' / 'r6_patch.js'
            self._send(200, file.read_bytes(), 'application/javascript; charset=utf-8'); return
        if path == '/r6_patch.css':
            file = self.server.root / 'app' / 'r6_patch.css'
            self._send(200, file.read_bytes(), 'text/css; charset=utf-8'); return
        # /ABRXOS_PATCH:R6_SERVER_STATIC
        mapping={'/':'app/index.html','/app.js':'app/app.js','/styles.css':'app/styles.css'}
        rel=mapping.get(path)
        if rel:
            file=self.server.root/rel
            if not file.exists():self._send(404,b'not found','text/plain');return
            ctype=mimetypes.guess_type(file.name)[0] or 'text/plain';self._send(200,file.read_bytes(),ctype+'; charset=utf-8' if ctype.startswith('text/') or ctype in {'application/javascript'} else ctype);return
        self._send(404,b'not found','text/plain')
    def do_POST(self):
        try:
            path=urlparse(self.path).path;data=self.body()
            if path=='/api/import_text':
                doc=import_text(str(data.get('name') or 'input.txt'),str(data.get('text') or ''));res=self.server.library.merge(doc);self.json({'ok':True,'result':res});return
            if path=='/api/select_project':
                self.server.library.select(str(data['projectId']));self.json({'ok':True});return
            if path=='/api/update_piece':
                row=self.server.library.update_piece(str(data['projectId']),str(data['pieceId']),data.get('patch') or {});self.json({'ok':True,'piece':row});return
            # ABRXOS_PATCH:R6_SERVER_VALIDATE_API
            if path == '/api/r6_validate':
                project_id = str(data.get('projectId') or self.server.library.data.get('currentProjectId') or '')
                project = self.server.library.get(project_id) if project_id else self.server.library.current()
                if not project:
                    raise KeyError('project not found')
                report = validate_r6_project(project, _R6_LIBRARIES)
                self.json({'ok': True, 'validation': report}); return
            # /ABRXOS_PATCH:R6_SERVER_VALIDATE_API
            if path=='/api/compile':
                project=self.server.library.get(str(data['projectId']))
                if not project: raise KeyError('project not found')
                html=compile_lienzo(project,str(data.get('rendererId') or 'joc-classic'),list(data.get('pieceIds') or []),str(data.get('title') or project.get('title') or project.get('projectId')),str(data.get('theme') or 'dark'),self.server.renderers,self.server.catalogs,self.server.root)
                name=''.join(c if c.isalnum() or c in '-_' else '_' for c in str(data.get('title') or project.get('projectId') or 'LIENZO'))+'.html'
                self._send(200,html.encode('utf-8'),'text/html; charset=utf-8',{'Content-Disposition':f'attachment; filename="{name}"'});return
            self.json({'ok':False,'error':'route not found'},404)
        except Exception as e:self.json({'ok':False,'error':str(e)},409)


def create_server(address,library,renderers,catalogs,root):
    return GeometraHTTPServer(address,Handler,library,renderers,catalogs,root)
