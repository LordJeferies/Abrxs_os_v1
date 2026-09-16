from __future__ import annotations

import copy
import html as html_lib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = 'abrxos.document.v3'
DOC_TYPE = 'ABRXOS_CANONICAL_DOCUMENT'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def clean(v: Any) -> str:
    if v is None:
        return ''
    return re.sub(r'\s+', ' ', str(v)).strip()


def piece_id(piece: dict[str, Any]) -> str:
    return clean(piece.get('canonicalId') or piece.get('contentId') or piece.get('content_id') or piece.get('uid') or piece.get('id'))


def piece_type(piece: dict[str, Any]) -> str:
    raw = clean(piece.get('type') or piece.get('kind') or piece.get('contentKind') or piece.get('physical_type')).lower()
    aliases = {'reel': 'vertical', 'vertical_clip': 'vertical', 'horizontal_video': 'horizontal', 'horizontal_clip': 'horizontal'}
    return aliases.get(raw, raw or 'note')


def _extract_script(raw: str, ids: tuple[str, ...] = ('app-data', 'seed', 'editorialData')) -> tuple[str, dict[str, Any]]:
    for sid in ids:
        pat = rf'<script[^>]+id=["\']{re.escape(sid)}["\'][^>]*>(.*?)</script>'
        m = re.search(pat, raw, re.I | re.S)
        if not m:
            continue
        payload = m.group(1).strip()
        try:
            obj = json.loads(payload)
        except Exception:
            obj = json.loads(html_lib.unescape(payload))
        if not isinstance(obj, dict):
            raise ValueError(f'script#{sid} must contain a JSON object')
        return sid, obj
    raise ValueError('No supported JSON script found (app-data/seed/editorialData)')



_CAPTION_STOPWORDS = {
    'de','la','el','los','las','y','o','a','en','un','una','que','por','para','con','sin','se','su','sus','es','son','era','como','yo','tu','tú','mi','mis','me','te','lo','le','al','del','si','sí','no','ya','muy','más','mas','pero','porque','cuando','donde','qué','cómo',
    'the','an','and','or','to','of','in','on','for','with','is','are','was','were','it','this','that'
}


def _caption_words(text: str) -> list[str]:
    return re.findall(r'\S+', clean(text))


def _plain_word(token: str) -> str:
    return re.sub(r'^[^\wÁÉÍÓÚÜÑáéíóúüñ]+|[^\wÁÉÍÓÚÜÑáéíóúüñ]+$', '', token)


def _highlight_word(words: list[str]) -> str:
    candidates=[]
    for token in words:
        plain=_plain_word(token)
        if not plain:
            continue
        if len(plain)>=3 and plain.upper()==plain and any(ch.isalpha() for ch in plain):
            return plain
        if plain.lower() not in _CAPTION_STOPWORDS:
            candidates.append(plain)
    if not candidates:
        candidates=[_plain_word(x) for x in words if _plain_word(x)]
    return max(candidates,key=len) if candidates else ''


def _split_caption(text: str) -> list[list[str]]:
    words=_caption_words(text)
    if not words:
        return []
    clauses=[]; current=[]
    for token in words:
        current.append(token)
        hard=bool(re.search(r'[.!?;:]$',token))
        comma=bool(re.search(r',$',token)) and len(current)>=3
        if hard or comma:
            clauses.append(current); current=[]
    if current:
        clauses.append(current)
    chunks=[]
    for clause in clauses:
        n=len(clause)
        if n<=5:
            chunks.append(clause); continue
        groups=(n+4)//5
        while groups>1 and n/groups<3:
            groups-=1
        base=n//groups; rem=n%groups; pos=0
        for idx in range(groups):
            size=base+(1 if idx<rem else 0)
            chunks.append(clause[pos:pos+size]); pos+=size
    return chunks


def _normalize_caption_timeline(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out=[]
    for event in timeline:
        if not isinstance(event,dict) or event.get('track')!='captions':
            out.append(copy.deepcopy(event)); continue
        if event.get('captionSchema')=='abrxos.caption.v2':
            out.append(copy.deepcopy(event)); continue
        text=clean(event.get('sourceText') or event.get('text') or event.get('displayText') or event.get('label'))
        chunks=_split_caption(text)
        if not chunks:
            out.append(copy.deepcopy(event)); continue
        start=_seconds(event.get('start')) or 0.0
        end=_seconds(event.get('end'))
        if end is None or end<=start:
            end=start+max(.5,len(chunks)*.7)
        total=sum(max(1,len(chunk)) for chunk in chunks)
        cursor=start
        original_id=clean(event.get('id')) or f'CAP_{len(out)+1:03d}'
        for idx,chunk in enumerate(chunks,1):
            row=copy.deepcopy(event)
            frac=len(chunk)/total
            seg_end=end if idx==len(chunks) else cursor+(end-start)*frac
            row['id']=original_id if len(chunks)==1 else f'{original_id}_CAP_{idx:02d}'
            row['captionSchema']='abrxos.caption.v2'
            row['captionGroupId']=original_id
            row['captionIndex']=idx
            row['captionCount']=len(chunks)
            row['sourceText']=text
            row['text']=' '.join(chunk)
            row['displayText']=row['text']
            row['label']=row['text']
            row['wordCount']=len(chunk)
            row['highlightWord']=clean(event.get('highlightWord')) if len(chunks)==1 and clean(event.get('highlightWord')) else _highlight_word(chunk)
            row['highlightStatus']='confirmed' if len(chunks)==1 and clean(event.get('highlightWord')) else 'suggested'
            row['displayMode']='hero_word' if len(chunk)==1 else 'normal'
            row['start']=round(cursor,3)
            row['end']=round(max(cursor+.05,seg_end),3)
            out.append(row)
            cursor=row['end']
    return out

def _normalize_piece(piece: dict[str, Any], index: int) -> dict[str, Any]:
    p = copy.deepcopy(piece)
    pid = piece_id(p) or f'PIECE_{index:03d}'
    p.setdefault('id', pid.lower())
    p['canonicalId'] = pid
    p['type'] = piece_type(p)
    p.setdefault('title', clean(p.get('workingTitle') or pid))
    p.setdefault('stage', clean(p.get('stage') or p.get('maturity') or 'BETA').upper())
    p.setdefault('workflowStatus', clean(p.get('workflowStatus') or p.get('status') or 'PENDIENTE').upper())
    if not isinstance(p.get('timeline'), list):
        p['timeline'] = []
    elif piece_type(p) in {'intro','vertical','horizontal','video','clip','vertical_clip','horizontal_video'}:
        p['timeline'] = _normalize_caption_timeline(p['timeline'])
    if not isinstance(p.get('sourceRanges'), list):
        p['sourceRanges'] = []
    if not isinstance(p.get('parts'), list):
        p['parts'] = []
    p.setdefault('included', True)
    return p


def normalize_project(data: dict[str, Any], source_name: str, source_format: str | None = None) -> dict[str, Any]:
    original = copy.deepcopy(data)
    # Piece objects live canonically in `pieces`; sourcePayload preserves root-level
    # provenance/unknown fields without duplicating the entire piece array. When a
    # V3 document is reimported, reuse its existing sourcePayload instead of nesting
    # sourcePayload inside sourcePayload on every roundtrip.
    source_payload = copy.deepcopy(data.get('sourcePayload')) if isinstance(data.get('sourcePayload'), dict) else {}
    if isinstance(original, dict):
        for key, value in original.items():
            if key in {'pieces', 'sourcePayload'}:
                continue
            source_payload.setdefault(key, copy.deepcopy(value))
    from_schema = clean(data.get('schemaVersion') or data.get('schema_version') or data.get('schema'))
    pieces_raw = data.get('pieces') if isinstance(data.get('pieces'), list) else []
    if not pieces_raw and any(k in data for k in ('id', 'uid', 'contentId', 'content_id', 'canonicalId')):
        pieces_raw = [data]
    project_id = clean(data.get('projectId') or ((data.get('project') or {}).get('projectId') if isinstance(data.get('project'), dict) else ''))
    if not project_id:
        project_id = clean(data.get('collection') or data.get('name') or Path(source_name).stem) or 'PROJECT'
    title = clean(data.get('title') or ((data.get('episode') or {}).get('title') if isinstance(data.get('episode'), dict) else '')) or project_id
    doc: dict[str, Any] = {
        'schemaVersion': SCHEMA,
        'documentType': DOC_TYPE,
        'projectId': project_id,
        'title': title,
        'pieces': [_normalize_piece(x, i + 1) for i, x in enumerate(pieces_raw) if isinstance(x, dict)],
        'catalogVersions': copy.deepcopy(data.get('catalogVersions') or {
            'xr': clean(data.get('xrCatalogRevision') or 'R5'),
            'sfx': '1.0',
            'motion': '1.0',
            'captions': '2.0',
        }),
        'extensions': copy.deepcopy(data.get('extensions') or {'xrDefinitions': [], 'sfxDefinitions': []}),
        'revision': copy.deepcopy(data.get('revision') or {'id': 'R1', 'number': 1, 'updatedAt': now_iso()}),
        'importHistory': copy.deepcopy(data.get('importHistory') or []),
        'sourcePayload': source_payload,
        'sourceName': source_name,
        'sourceFormat': source_format or 'json',
        'migration': {'fromSchema': from_schema or 'unknown', 'toSchema': SCHEMA, 'at': now_iso()},
    }
    for key in ('episode', 'sources', 'sourceTruth', 'brand', 'semanticRules', 'counts', 'distribution', 'staticProduction'):
        if key in data:
            doc[key] = copy.deepcopy(data[key])
    doc['importHistory'].append({'at': now_iso(), 'source': source_name, 'format': doc['sourceFormat']})
    return doc


def import_text(name: str, text: str) -> dict[str, Any]:
    suffix = Path(name).suffix.lower()
    if suffix in {'.html', '.htm'} or text.lstrip().startswith('<'):
        sid, data = _extract_script(text)
        doc = normalize_project(data, name, sid)
        doc['sourceFormat'] = sid
        return doc
    if suffix == '.json' or text.lstrip().startswith('{'):
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError('JSON root must be an object')
        return normalize_project(data, name, 'json')
    return {
        'schemaVersion': SCHEMA,
        'documentType': DOC_TYPE,
        'projectId': re.sub(r'[^A-Za-z0-9_-]+', '_', Path(name).stem).strip('_') or 'TEXT_PROJECT',
        'title': Path(name).stem,
        'pieces': [],
        'catalogVersions': {'xr': 'R5', 'sfx': '1.0', 'motion': '1.0', 'captions': '2.0'},
        'extensions': {'xrDefinitions': [], 'sfxDefinitions': []},
        'revision': {'id': 'R1', 'number': 1, 'updatedAt': now_iso()},
        'importHistory': [{'at': now_iso(), 'source': name, 'format': 'raw-text'}],
        'sourcePayload': {'rawText': text},
        'sourceName': name,
        'sourceFormat': 'raw-text',
        'migration': {'fromSchema': 'raw-text', 'toSchema': SCHEMA, 'at': now_iso()},
    }

VIDEO_TYPES = {'intro','vertical','horizontal','video','clip','vertical_clip','horizontal_video'}


def _seconds(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    text = clean(value).replace(',', '.')
    if not text:
        return None
    try:
        if ':' not in text:
            return float(text)
        parts = [float(x) for x in text.split(':')]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
    except ValueError:
        return None
    return None


def cutter_gate(project: dict[str, Any], piece_ids: list[str] | None = None) -> dict[str, Any]:
    wanted = set(piece_ids or [])
    rows: list[dict[str, Any]] = []
    critical = 0
    warnings = 0
    for piece in project.get('pieces') or []:
        if not isinstance(piece, dict) or piece_type(piece) not in VIDEO_TYPES:
            continue
        pid = piece_id(piece)
        if wanted and pid not in wanted:
            continue
        errors: list[str] = []
        warns: list[str] = []
        ranges = piece.get('sourceRanges') if isinstance(piece.get('sourceRanges'), list) else []
        if not ranges:
            errors.append('Falta sourceRanges[]')
        else:
            for idx, row in enumerate(ranges, 1):
                if not isinstance(row, dict):
                    errors.append(f'sourceRanges[{idx}] inválido')
                    continue
                start = _seconds(row.get('start', row.get('sourceStart')))
                end = _seconds(row.get('end', row.get('sourceEnd')))
                if start is None or end is None or end <= start:
                    errors.append(f'sourceRanges[{idx}] necesita start < end')
        if not clean(piece.get('source')):
            warns.append('Sin source explícito; se espera DEFAULT o source group resuelto por Cutter.')
        critical += len(errors)
        warnings += len(warns)
        rows.append({'id': pid, 'ready': not errors, 'errors': errors, 'warnings': warns})
    return {'ready': critical == 0, 'critical': critical, 'warnings': warnings, 'pieces': rows}
