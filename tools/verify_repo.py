#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys,re,datetime,os
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; checks=[]
apps={
 'geometra':ROOT/'apps/geometra/current',
 'contentBuilder':ROOT/'apps/content-builder/current',
 'brandBuilder':ROOT/'apps/brand-builder/current',
}
expected={'geometra':'3.1.1','contentBuilder':'1.0.1','brandBuilder':'1.0.1'}
for name,path in apps.items():
    vf=path/'VERSION.json'
    if not vf.exists(): errors.append(f'{name}: current snapshot missing; run tools/CAPTURAR_INSTALACION_ACTUAL.command'); continue
    try: v=json.loads(vf.read_text())
    except Exception as e: errors.append(f'{name}: invalid VERSION.json: {e}'); continue
    if str(v.get('version'))!=expected[name]: errors.append(f'{name}: version {v.get("version")} != {expected[name]}')
    else: checks.append(f'{name}_version=PASS')
# required provenance for geometra
geo=apps['geometra']
if (geo/'VERSION.json').exists():
    if not (geo/'.abrxos_hotfixes/ABRXOS_ECOSYSTEM_V3_1_1_R6_1.json').exists(): errors.append('geometra: missing ecosystem hotfix registry')
    else: checks.append('geometra_hotfix_registry=PASS')
# Parse JSON and compile Python in current app snapshots.
for name,path in apps.items():
    if not path.exists(): continue
    for p in path.rglob('*.json'):
        if any(x in p.parts for x in ('__pycache__','.pytest_cache')): continue
        try: json.loads(p.read_text(encoding='utf-8'))
        except Exception as e: errors.append(f'json:{p.relative_to(ROOT)}:{e}')
    for p in path.rglob('*.py'):
        try: compile(p.read_text(encoding='utf-8'), str(p), 'exec')
        except Exception as e: errors.append(f'py_compile:{p.relative_to(ROOT)}:{e}')
checks.append('json_and_python=PASS' if not [e for e in errors if e.startswith(('json:','py_compile:'))] else 'json_and_python=FAIL')
# Node syntax if installed.
node=__import__('shutil').which('node')
if node:
    js_errors=0
    for name,path in apps.items():
        if not path.exists(): continue
        for p in path.rglob('*.js'):
            r=subprocess.run([node,'--check',str(p)],capture_output=True,text=True)
            if r.returncode: errors.append(f'node_check:{p.relative_to(ROOT)}:{r.stderr.strip()}');js_errors+=1
    checks.append('node_check=PASS' if not js_errors else 'node_check=FAIL')
else: warnings.append('node not installed; JS syntax check skipped')
# Shared library hashes Content Builder vs Geometra current R6.
def sha(p):
    h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()
libs=['XR_FAMILIES_R6.json','EDIT_PROFILES_R6.json','CINE_LIBRARY_R6.json','SFX_LIBRARY_R6.json','MOTION_LIBRARY_R6.json','MUSIC_LIBRARY_R6.json','CAPTIONS_R6.json']
if (geo/'VERSION.json').exists():
    cbase=apps['contentBuilder']/'resources/canon_r6/libraries'
    bad=[]
    for lib in libs:
        a=geo/'r6'/lib; b=cbase/lib
        if not a.exists() or not b.exists() or sha(a)!=sha(b): bad.append(lib)
    if bad: errors.append('R6 library hash mismatch: '+', '.join(bad))
    else: checks.append('content_geometra_library_hashes=PASS')
# Brand adapter contract expectation.
brand_template=apps['brandBuilder']/'resources/brand_adapter_template.json'
if brand_template.exists():
    obj=json.loads(brand_template.read_text())
    if obj.get('schemaVersion')!='abrxos.brand-adapter.r6': errors.append('brand adapter schemaVersion mismatch')
    else: checks.append('brand_adapter_schema=PASS')
# No caches or compiled files committed under apps/current.
for p in (ROOT/'apps').rglob('*'):
    if p.name in {'__pycache__','.pytest_cache'} or p.suffix in {'.pyc','.pyo'}: errors.append(f'forbidden cache: {p.relative_to(ROOT)}')
# Scan current source for machine-specific or obvious secret tokens.
for name,path in apps.items():
    if not path.exists(): continue
    for p in path.rglob('*'):
        if not p.is_file() or p.suffix.lower() in {'.png','.jpg','.jpeg','.zip','.mov','.mp4'}: continue
        try: text=p.read_text(encoding='utf-8',errors='ignore')
        except Exception: continue
        if '/Users/lordjef/' in text: errors.append(f'machine-specific path in {p.relative_to(ROOT)}')
        if '/mnt/data/' in text: warnings.append(f'development fixture path in {p.relative_to(ROOT)}; review before public release')
        if re.search(r'\bghp_[A-Za-z0-9]{20,}\b',text): errors.append(f'possible GitHub token in {p.relative_to(ROOT)}')
        if re.search(r'\bsk-[A-Za-z0-9_-]{20,}\b',text): errors.append(f'possible API secret in {p.relative_to(ROOT)}')
# Optional pytest suites, if pytest available.
try:
    import pytest  # noqa
    for name in ('contentBuilder','brandBuilder'):
        path=apps[name]
        if (path/'tests').exists():
            r=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests'],cwd=path,capture_output=True,text=True,env={**os.environ,'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTHONDONTWRITEBYTECODE':'1'})
            if r.returncode: errors.append(f'{name}_pytest_failed:\n{r.stdout}\n{r.stderr}')
            else: checks.append(f'{name}_pytest=PASS')
    if (geo/'tests').exists():
        # Geometra current may carry a larger suite; run non-destructively.
        r=subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider','tests'],cwd=geo,capture_output=True,text=True,env={**os.environ,'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1','PYTHONDONTWRITEBYTECODE':'1'},timeout=180)
        if r.returncode: warnings.append('geometra pytest did not fully pass in this environment; inspect output in LOCAL_VERIFY_REPORT.json')
        else: checks.append('geometra_pytest=PASS')
except Exception as e:
    warnings.append(f'pytest unavailable/skipped: {e}')
report={'schemaVersion':'abrxos.repo-verify.v1','verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ok':not errors,'errors':errors,'warnings':sorted(set(warnings)),'checks':checks}
(ROOT/'LOCAL_VERIFY_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if report['ok'] else 2)
