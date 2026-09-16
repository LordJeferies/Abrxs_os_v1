from __future__ import annotations

import copy, hashlib, json, re, shutil, unicodedata, zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENGINE_VERSION='1.0.1'
CANON_VERSION='R6'
CANON_FAMILY='R6'
CANON_REVISION='R6.1'
R61_FEATURES=['sourceAlignment','microtrim','voAdded','routeSemanticsR61','captionGroupsR6','shortSourceException','projectionReady']
BASE_DIR=Path(__file__).resolve().parent
R61_RESOURCES=BASE_DIR/'resources'/'r6_1'
DEFAULT_RESOURCES=BASE_DIR/'resources'/'canon_r6'


def safe_slug(value:str,fallback='item')->str:
    value=unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode('ascii').lower().replace('_','-')
    value=re.sub(r'[^a-z0-9]+','-',value)
    value=re.sub(r'-+','-',value).strip('-.')
    return value or fallback


def deep_merge(base:Any,patch:Any)->Any:
    if isinstance(base,dict) and isinstance(patch,dict):
        out=copy.deepcopy(base)
        for k,v in patch.items(): out[k]=deep_merge(out[k],v) if k in out else copy.deepcopy(v)
        return out
    return copy.deepcopy(patch)


def _sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def _write_json(path:Path,obj:Any):
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


class ContentStore:
    def __init__(self,root:Path):
        self.root=Path(root); self.drafts=self.root/'drafts'; self.brands=self.root/'brands'; self.projects=self.root/'projects'
        for p in (self.drafts,self.brands,self.projects): p.mkdir(parents=True,exist_ok=True)
    def save_draft(self,obj:dict)->dict:
        obj=copy.deepcopy(obj); rid=obj.get('requestId') or obj.get('projectId') or 'request'; slug=obj.get('slug') or safe_slug(rid)
        obj['slug']=slug; obj.setdefault('createdAt',datetime.now(timezone.utc).isoformat()); obj['updatedAt']=datetime.now(timezone.utc).isoformat()
        _write_json(self.drafts/f'{slug}.json',obj); return {'slug':slug,'draft':obj,'path':str(self.drafts/f'{slug}.json')}
    def load_draft(self,slug:str)->dict: return json.loads((self.drafts/f'{safe_slug(slug)}.json').read_text(encoding='utf-8'))
    def list_drafts(self)->list[dict]:
        out=[]
        for p in sorted(self.drafts.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True):
            try:o=json.loads(p.read_text(encoding='utf-8'))
            except:continue
            out.append({'slug':o.get('slug',p.stem),'requestId':o.get('requestId',''),'projectId':o.get('projectId',''),'contentType':o.get('contentType',''),'stage':o.get('stage',''),'updatedAt':o.get('updatedAt','')})
        return out
    def delete_draft(self,slug:str)->bool:
        p=self.drafts/f'{safe_slug(slug)}.json'
        if p.exists(): p.unlink(); return True
        return False
    def save_library(self,kind:str,obj:dict)->dict:
        directory=self.brands if kind=='brand' else self.projects
        identity=obj.get('brandId') if kind=='brand' else obj.get('projectId')
        identity=identity or obj.get('brandName') or obj.get('projectName') or kind
        slug=safe_slug(identity); _write_json(directory/f'{slug}.json',obj)
        return {'slug':slug,'item':obj}
    def list_library(self,kind:str)->list[dict]:
        directory=self.brands if kind=='brand' else self.projects
        out=[]
        for p in sorted(directory.glob('*.json')):
            try:o=json.loads(p.read_text(encoding='utf-8'))
            except:continue
            out.append({'slug':p.stem,'item':o})
        return out


def select_case(req:dict)->str:
    mode=req.get('workflowMode','transcript_only'); stage=req.get('stage','BETA').upper(); typ=req.get('contentType','vertical'); profile=req.get('editProfile','XR_FULL')
    if mode=='all_project': return '14'
    if mode=='multi_source': return '12'
    if mode=='full_episode' or typ=='full_episode': return '11'
    if mode=='update_alpha': return '08'
    if mode=='beta_to_alpha': return '07'
    if mode=='fixed_plan':
        return '13' if req.get('timingQuality') in ('no_timing','unresolved') else '01'
    if stage=='BETA': return '06'
    if profile=='MOTION_SFX' and typ in {'intro','vertical','horizontal'}: return '09'
    if profile=='SFX_ONLY' and typ in {'intro','vertical','horizontal'}: return '10'
    if typ=='intro': return '02'
    if typ=='vertical': return '03'
    if typ=='horizontal': return '04'
    if typ in {'carousel','quote','thread','note','pdf','script'}: return '05'
    return '06'

PROMPTS={
'01':'PROMPT_01_PLAN_FIJO_MAS_TRANSCRIPCION_A_ALFA_R6.txt','02':'PROMPT_02_SOLO_TRANSCRIPCION_A_INTRO_ALFA_R6.txt','03':'PROMPT_03_SOLO_TRANSCRIPCION_A_VERTICALES_ALFA_R6.txt','04':'PROMPT_04_SOLO_TRANSCRIPCION_A_HORIZONTAL_ALFA_R6.txt','05':'PROMPT_05_TRANSCRIPCION_A_CARRUSEL_ALFA_R6.txt','06':'PROMPT_06_TRANSCRIPCION_A_BETAS_PARA_SELECCION_R6.txt','07':'PROMPT_07_BETA_SELECCIONADA_A_ALFA_R6.txt','08':'PROMPT_08_ACTUALIZAR_ALFA_EXISTENTE_R6.txt','09':'PROMPT_09_VIDEO_DYNAMIC_EDIT_SIN_XR_R6.txt','10':'PROMPT_10_VIDEO_CLEAN_EDIT_SFX_ONLY_R6.txt','11':'PROMPT_11_EPISODIO_COMPLETO_ALFA_R6.txt','12':'PROMPT_12_MULTI_SOURCE_CH_AS_WB_R6.txt','13':'PROMPT_13_PLAN_SIN_TIMESTAMPS_A_ALFA_NEEDS_REVIEW_R6.txt','14':'PROMPT_14_GENERAR_TODO_EL_PROYECTO_R6.txt'}

TYPE_DIR={'intro':'INTRO','vertical':'VERTICAL','horizontal':'HORIZONTAL','full_episode':'FULL_EPISODE','carousel':'CAROUSEL','quote':'QUOTE','thread':'THREAD','note':'NOTE','pdf':'PDF','script':'SCRIPT'}


def _template_name(req:dict)->str:
    typ=req.get('contentType','vertical'); stage=req.get('stage','BETA').upper(); profile=req.get('editProfile','XR_FULL')
    if typ=='all': return 'ABRXOS_TODAS_LAS_FICHAS_R6.json'
    up=TYPE_DIR.get(typ,typ.upper())
    if stage=='BETA': return f'FICHA_{up}_BETA_R6.json'
    if typ in {'intro','vertical','horizontal','full_episode'} and profile=='XR_FULL': return f'FICHA_{up}_ALFA_CINEMATIC_R6.json'
    return f'FICHA_{up}_ALFA_R6.json'


def resolve_prompt_template(req:dict,resources_dir:Path|None=None)->tuple[Path,Path]:
    res=Path(resources_dir or DEFAULT_RESOURCES); cid=select_case(req)
    prompt_name = PROMPTS[cid]
    if cid == '05' and req.get('contentType') in {'quote','thread','note','pdf','script'}:
        prompt_name = 'PROMPT_STATIC_ALFA_R6.txt'
    prompt=res/'prompts'/prompt_name
    name=_template_name(req)
    if req.get('contentType')=='all': template=res/'fichas'/name
    else: template=res/'fichas'/TYPE_DIR.get(req.get('contentType','vertical'),'VERTICAL')/name
    return prompt,template


def _append_request_instructions(base:str,req:dict,case_id:str)->str:
    type_name=req.get('contentType','')
    lines=[base.rstrip(),'','=== REQUEST COMPILADO POR ABRXOS CONTENT BUILDER V1 ===',f'CASE_ID: {case_id}',f'PROJECT_ID: {req.get("projectId","")}',f'CONTENT_TYPE: {type_name}',f'STAGE: {req.get("stage","")}',f'EDIT_PROFILE: {req.get("editProfile","")}',f'QUANTITY: {req.get("quantity",1)}',f'SOURCE_GROUP: {req.get("sourceGroup","DEFAULT")}',f'TIMING_QUALITY: {req.get("timingQuality","unknown")}']
    if req.get('xrCount') not in (None,''): lines.append(f'XR_COUNT_OR_RULE: {req.get("xrCount")}')
    if req.get('orientations'): lines.append('ORIENTATIONS: '+', '.join(req['orientations']))
    if req.get('platforms'): lines.append('PLATFORMS: '+', '.join(req['platforms']))
    lines += ['','REGLAS DE SALIDA:','- Devuelve JSON válido listo para Geometra y un TXT humano equivalente.','- No inventes timestamps.','- Conserva IDs estables al actualizar fichas.','', '=== SOURCE ALIGNMENT R6.1 ===','- Primero crea sourceAlignment por part/cue. Si el corte fino vive dentro de un cue, marca microtrim=true y conserva startAnchor/endAnchor.','- Sólo después crea sourceRanges finales para rangos resueltos. sourceRanges sigue siendo verdad del Cutter.','- VO_ADDED no recibe sourceRange: usa placement.after/before y evento T6 con timingStatus editorial_planned.','- Una route es una alternativa editorial completa; no uses vo/xr/sfx como primaryRoute.','- Caption Groups cortos pueden usar shortSourceException=true cuando toda la part es menor al soft range.','- Proyecta assets/motion/SFX/VO/CINE/captions en T1–T9 para que Projection Ready pueda verificarse.']
    if req.get('specialRules'): lines += ['','REGLAS ESPECIALES DEL USUARIO:',str(req['specialRules'])]
    return '\n'.join(lines)+'\n'


def _r61_contract(resources_dir: Path) -> dict:
    libraries = {}
    lib_dir = Path(resources_dir) / 'libraries'
    for path in sorted(lib_dir.glob('*.json')) if lib_dir.exists() else []:
        libraries[path.name] = f"sha256:{_sha256(path)}"
    return {
        'schemaVersion': 'abrxos.ecosystem-contract.v1',
        'canonFamily': CANON_FAMILY,
        'canonRevision': CANON_REVISION,
        'contentSchema': 'abrxos.content-project.r6',
        'features': list(R61_FEATURES),
        'libraries': libraries,
        'geometraMinimum': '3.1.1-r6.1',
        'builder': 'ABRXOS Content Builder',
        'builderVersion': ENGINE_VERSION,
    }


def build_content_ai_package(req:dict,export_root:Path,resources_dir:Path)->dict:
    export_root=Path(export_root); resources_dir=Path(resources_dir); case_id=select_case(req); prompt_path,template_path=resolve_prompt_template(req,resources_dir)
    if not prompt_path.exists(): raise FileNotFoundError(f'Missing prompt: {prompt_path}')
    if not template_path.exists(): raise FileNotFoundError(f'Missing template: {template_path}')
    canon=resources_dir/'ONE_FILE_CONTEXT_R6.txt'
    if not canon.exists(): raise FileNotFoundError(f'Missing canon context: {canon}')
    package_id=safe_slug(req.get('requestId') or f"{req.get('projectId','project')}-{req.get('contentType','content')}")
    package_name=f'{package_id.upper()}_CONTENT_AI_PACKAGE_R6'; folder=export_root/package_name
    if folder.exists(): shutil.rmtree(folder)
    folder.mkdir(parents=True,exist_ok=True)
    base_prompt=prompt_path.read_text(encoding='utf-8')
    compiled=_append_request_instructions(base_prompt,req,case_id)
    template_obj=json.loads(template_path.read_text(encoding='utf-8'))
    start=f"ABRXOS CONTENT BUILDER V1\n\nRequest: {req.get('requestId','')}\nProject: {req.get('projectId','')}\nCase: {case_id}\nType: {req.get('contentType','')}\nStage: {req.get('stage','')}\nProfile: {req.get('editProfile','')}\nCanon: R6 / R6.1\n\nEste paquete NO ejecuta IA. Usa 01_QUE_SUBIR_A_CHATGPT.txt y espera JSON + TXT.\n"
    upload='''ORDEN RECOMENDADO\n\n1. 02_PROMPT_FINAL.txt\n2. 03_REQUEST.json\n3. 04_TRANSCRIPCION.txt\n4. 05_PLAN_EDITORIAL.txt (si aplica)\n5. 06_PROJECT_CONFIG.json\n6. 07_BRAND_ADAPTER.json\n7. 08_FICHA_TARGET.json\n8. 09_CANON_CONTEXT.txt\n9. 10_CURRENT_FICHA.json (si aplica)\n10. 11_SPECIAL_RULES.txt\n11. 12_R6_1_SOURCE_ALIGNMENT.txt\n12. 13_R6_1_VO_ROUTE_CAPTIONS.txt\n13. 14_LIENZO_PROJECTION_CONTRACT.json\n14. contract_manifest.json\n\nDespués escribe: \"Ejecuta el paquete y devuelve JSON + TXT listos para Geometra.\"\n'''
    objs={
      '03_REQUEST.json':{k:v for k,v in req.items() if k not in {'transcript','editorialPlan','currentFicha','specialRules'}},
      '06_PROJECT_CONFIG.json':req.get('projectConfig') or {},'07_BRAND_ADAPTER.json':req.get('brandAdapter') or {},'08_FICHA_TARGET.json':template_obj
    }
    texts={'00_START_HERE.txt':start,'01_QUE_SUBIR_A_CHATGPT.txt':upload,'02_PROMPT_FINAL.txt':compiled,'04_TRANSCRIPCION.txt':str(req.get('transcript','')),'05_PLAN_EDITORIAL.txt':str(req.get('editorialPlan','')),'09_CANON_CONTEXT.txt':canon.read_text(encoding='utf-8'),'11_SPECIAL_RULES.txt':str(req.get('specialRules',''))}
    if req.get('currentFicha'):
        objs['10_CURRENT_FICHA.json']=req['currentFicha'] if isinstance(req['currentFicha'],dict) else {'raw':req['currentFicha']}
    for name,text in texts.items(): (folder/name).write_text(text,encoding='utf-8')
    for name,obj in objs.items(): _write_json(folder/name,obj)

    libraries_dir = resources_dir / 'libraries'
    if libraries_dir.exists():
        target_lib = folder / 'CANON_LIBRARIES'
        target_lib.mkdir(exist_ok=True)
        for src in sorted(libraries_dir.glob('*.json')):
            shutil.copy2(src, target_lib / src.name)

    r61_dir = Path(__file__).resolve().parent / 'resources' / 'r6_1'
    for name in ('12_R6_1_SOURCE_ALIGNMENT.txt','13_R6_1_VO_ROUTE_CAPTIONS.txt','14_LIENZO_PROJECTION_CONTRACT.json'):
        src = r61_dir / name
        if not src.exists():
            raise FileNotFoundError(f'Missing R6.1 supplement: {src}')
        shutil.copy2(src, folder / name)
    contract = _r61_contract(resources_dir)
    _write_json(folder / 'contract_manifest.json', contract)

    files=[]
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.name!='package_manifest.json': files.append({'path':str(p.relative_to(folder)),'bytes':p.stat().st_size,'sha256':_sha256(p)})
    manifest={'schemaVersion':'abrxos.ai-package.content.v1','builder':'ABRXOS Content Builder','builderVersion':ENGINE_VERSION,'canonVersion':CANON_VERSION,'canonFamily':CANON_FAMILY,'canonRevision':CANON_REVISION,'contractFile':'contract_manifest.json','features':list(R61_FEATURES),'caseId':case_id,'requestId':req.get('requestId',''),'projectId':req.get('projectId',''),'contentType':req.get('contentType',''),'stage':req.get('stage',''),'editProfile':req.get('editProfile',''),'createdAt':datetime.now(timezone.utc).isoformat(),'files':files}
    _write_json(folder/'package_manifest.json',manifest)
    zip_path=export_root/f'{package_name}.zip'
    if zip_path.exists(): zip_path.unlink()
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob('*')):
            if p.is_file(): z.write(p,str(p.relative_to(folder)))
    return {'folder':str(folder),'zip':str(zip_path),'manifest':manifest,'caseId':case_id,'promptFile':prompt_path.name,'templateFile':template_path.name}
