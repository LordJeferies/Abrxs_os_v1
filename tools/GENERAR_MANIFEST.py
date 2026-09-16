#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, os
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE_PARTS={'.git','__pycache__','.pytest_cache'}
EXCLUDE_NAMES={'REPO_MANIFEST.json','MANIFEST_SHA256.txt','REPO_TREE.txt','LOCAL_CAPTURE_REPORT.json','LOCAL_VERIFY_REPORT.json'}

def files():
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(part in EXCLUDE_PARTS for part in rel.parts): continue
        if p.name in EXCLUDE_NAMES: continue
        if p.suffix in {'.pyc','.pyo'}: continue
        yield p,rel

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
rows=[]
for p,rel in files(): rows.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
manifest={'schemaVersion':'abrxos.repo-manifest.v1','release':'3.1.1-r6.1','generatedAt':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'files':rows}
(ROOT/'REPO_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'MANIFEST_SHA256.txt').write_text('\n'.join(f"{r['sha256']}  {r['path']}" for r in rows)+'\n',encoding='utf-8')
# compact tree grouped by path
lines=[]
for _,rel in files(): lines.append(rel.as_posix())
(ROOT/'REPO_TREE.txt').write_text('ABRXOS ECOSYSTEM REPO TREE\n\n'+'\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'files':len(rows)},indent=2))
