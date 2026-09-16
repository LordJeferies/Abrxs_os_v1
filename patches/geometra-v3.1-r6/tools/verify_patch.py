from __future__ import annotations
import argparse, importlib.util, json, shutil, subprocess, sys
from pathlib import Path

PATCH_ID='ABRXOS_GEOMETRA_V3_1_R6'
REQUIRED_FILES=[
    'geometra/r6.py',
    'r6/XR_FAMILIES_R6.json','r6/EDIT_PROFILES_R6.json','r6/CINE_LIBRARY_R6.json',
    'r6/SFX_LIBRARY_R6.json','r6/MOTION_LIBRARY_R6.json','r6/MUSIC_LIBRARY_R6.json','r6/CAPTIONS_R6.json',
    'r6/ABRXOS_CONTENT_PROJECT_R6.schema.json',
    'shared/r6_patch.js','app/r6_patch.js','app/r6_patch.css',
]
MARKERS={
    'geometra/server.py':['R6_SERVER_IMPORTS','R6_SERVER_STATIC','R6_SERVER_VALIDATE_API'],
    'geometra/compiler.py':['R6_COMPILER_LOAD','R6_COMPILER_INLINE'],
    'app/index.html':['R6_APP_CSS','R6_APP_JS'],
}

def _load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def verify_patch(target: Path, patch_root: Path | None=None) -> dict:
    target=Path(target).expanduser().resolve()
    errors=[]; warnings=[]; checks=[]
    if not target.exists():
        return {'ok':False,'errors':[f'Instalación no encontrada: {target}'],'warnings':[],'checks':[],'target':str(target)}
    vf=target/'VERSION.json'
    if not vf.exists(): errors.append('VERSION.json no encontrado')
    else:
        try:
            v=str(_load_json(vf).get('version') or '')
            if not v.startswith('3.'): errors.append(f'Versión incompatible: {v}')
            checks.append(f'version={v}')
        except Exception as exc: errors.append(f'VERSION.json inválido: {exc}')
    reg=target/'.abrxos_patches'/f'{PATCH_ID}.json'
    if not reg.exists(): errors.append(f'Patch no registrado: {PATCH_ID}')
    else: checks.append('patch_registry=PASS')
    for rel in REQUIRED_FILES:
        p=target/rel
        if not p.exists(): errors.append(f'Falta archivo: {rel}')
        else: checks.append(f'file:{rel}=PASS')
    for rel, markers in MARKERS.items():
        p=target/rel
        if not p.exists(): continue
        text=p.read_text(encoding='utf-8',errors='replace')
        for marker in markers:
            if f'ABRXOS_PATCH:{marker}' not in text: errors.append(f'Falta hook {marker} en {rel}')
            else: checks.append(f'hook:{marker}=PASS')
    pyfiles=[target/'geometra/r6.py',target/'geometra/server.py',target/'geometra/compiler.py']
    for p in pyfiles:
        if not p.exists(): continue
        cp=subprocess.run([sys.executable,'-m','py_compile',str(p)],capture_output=True,text=True)
        if cp.returncode: errors.append(f'py_compile {p.name}: {(cp.stderr or cp.stdout).strip()}')
        else: checks.append(f'py_compile:{p.name}=PASS')
    node=shutil.which('node')
    if node:
        for rel in ('shared/r6_patch.js','app/r6_patch.js'):
            p=target/rel
            if not p.exists(): continue
            cp=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
            if cp.returncode: errors.append(f'node --check {rel}: {(cp.stderr or cp.stdout).strip()}')
            else: checks.append(f'node_check:{rel}=PASS')
    else:
        warnings.append('Node no disponible; se omitió node --check.')
    r6py=target/'geometra/r6.py'
    if r6py.exists():
        try:
            spec=importlib.util.spec_from_file_location('_abrxos_r6_verify',r6py)
            mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
            libs=mod.load_r6_libraries(target/'r6')
            project={'schemaVersion':'abrxos.content-project.r6','projectId':'VERIFY','pieces':[{'canonicalId':'VERIFY_V1','type':'vertical','stage':'BETA','workflowStatus':'PENDIENTE','source':'DEFAULT','sourceRanges':[],'timeline':[]}]}
            report=mod.validate_r6_project(project,libs)
            if not report.get('r6Detected'): errors.append('Validador R6 no detectó proyecto sintético R6')
            else: checks.append('r6_validator=PASS')
        except Exception as exc: errors.append(f'R6 validator import: {exc}')
    return {'ok':not errors,'errors':errors,'warnings':warnings,'checks':checks,'target':str(target)}

def main(argv=None):
    ap=argparse.ArgumentParser(description='Verifica ABRXOS Geometra V3.1 R6 patch')
    ap.add_argument('--target',required=True);ap.add_argument('--patch-root')
    args=ap.parse_args(argv)
    report=verify_patch(Path(args.target),Path(args.patch_root) if args.patch_root else None)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 2)

if __name__=='__main__': main()
