from __future__ import annotations
import copy, json, os
from pathlib import Path
from typing import Any
from .core import piece_id, now_iso


class Library:
    def __init__(self, path: Path):
        self.path=Path(path)
        self.data={'schemaVersion':'abrxos.geometra-library.v3','currentProjectId':None,'projects':{},'updatedAt':now_iso()}
        self.load()

    def load(self):
        if self.path.exists():
            try:
                obj=json.loads(self.path.read_text(encoding='utf-8'))
                if isinstance(obj,dict) and isinstance(obj.get('projects'),dict): self.data=obj
            except Exception: pass

    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True);self.data['updatedAt']=now_iso();tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(self.data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,self.path)

    def list(self):
        return [copy.deepcopy(v) for v in self.data['projects'].values()]

    def get(self, project_id: str):
        p=self.data['projects'].get(project_id);return copy.deepcopy(p) if p else None

    def current(self):
        pid=self.data.get('currentProjectId');return self.get(pid) if pid else None

    def select(self, project_id: str):
        if project_id not in self.data['projects']: raise KeyError(project_id)
        self.data['currentProjectId']=project_id;self.save()

    def merge(self, incoming: dict[str,Any]):
        pid=str(incoming.get('projectId') or '')
        if not pid: raise ValueError('projectId required')
        old=self.data['projects'].get(pid)
        if old is None:
            self.data['projects'][pid]=copy.deepcopy(incoming);self.data['currentProjectId']=pid;self.save();return {'projectId':pid,'stats':{'new':len(incoming.get('pieces') or []),'updated':0,'unchanged':0}}
        merged=copy.deepcopy(old);existing={piece_id(x):x for x in merged.get('pieces') or [] if isinstance(x,dict)};new=updated=unchanged=0
        for p in incoming.get('pieces') or []:
            if not isinstance(p,dict):continue
            key=piece_id(p)
            if key not in existing:
                merged.setdefault('pieces',[]).append(copy.deepcopy(p));existing[key]=merged['pieces'][-1];new+=1
            elif existing[key]==p: unchanged+=1
            else:
                idx=merged['pieces'].index(existing[key]);merged['pieces'][idx]=copy.deepcopy(p);existing[key]=merged['pieces'][idx];updated+=1
        for k,v in incoming.items():
            if k not in {'pieces','sourcePayload'}: merged[k]=copy.deepcopy(v)
        merged['sourcePayload']=copy.deepcopy(incoming.get('sourcePayload',old.get('sourcePayload',{})))
        self.data['projects'][pid]=merged;self.data['currentProjectId']=pid;self.save();return {'projectId':pid,'stats':{'new':new,'updated':updated,'unchanged':unchanged}}

    def update_piece(self, project_id: str, pid: str, patch: dict[str,Any]):
        proj=self.data['projects'].get(project_id)
        if not proj: raise KeyError(project_id)
        piece=next((x for x in proj.get('pieces') or [] if piece_id(x)==pid),None)
        if not piece: raise KeyError(pid)
        for k,v in patch.items():
            if k=='scheduleDate':
                new_date=v or ''
                piece.setdefault('schedule',{'date':'','time':'','platforms':[]})['date']=new_date
                if new_date and piece.get('workflowStatus')=='LISTO':
                    piece['workflowStatus']='PROGRAMADO'
                elif not new_date and piece.get('workflowStatus')=='PROGRAMADO':
                    piece['workflowStatus']='LISTO'
            else:
                piece[k]=v
        self.save();return copy.deepcopy(piece)
