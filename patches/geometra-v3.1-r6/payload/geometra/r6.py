from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

R6_SCHEMA = "abrxos.content-project.r6"
VALIDATION_SCHEMA = "abrxos.r6-validation.v1"
VIDEO = {"intro", "vertical", "horizontal", "full_episode", "video", "clip"}
STATIC = {"carousel", "quote", "thread", "note", "pdf", "script", "static"}
WORKFLOW = {"PENDIENTE", "REVISADO", "HACIENDO", "LISTO", "PROGRAMADO", "PUBLICADO"}
STAGES = {"BETA", "ALFA", "OMEGA"}
XR_FAMILIES = {"COMIC_INFO", "COMIC_CC", "TYPO", "PHOTOS", "OBJECTS", "PHOTO_OBJECT", "NO_XR"}
CINE_TYPES = {"CINE01_BLACK_HOLD", "CINE02_FREEZE_HOLD", "CINE03_PUNCH_CUT"}
EDIT_PROFILES = {"XR_FULL", "MOTION_SFX", "SFX_ONLY"}

CHECKLIST_KEYS = (
    "editorial", "source", "cut", "xr", "images", "broll", "cine", "motion",
    "sfx", "music", "captions", "cover", "copy", "qa",
)
DONE_STATUSES = {"ready", "done", "approved", "placed", "created", "complete", "completed", "verified"}


def _num(value: Any) -> float | None:
    try:
        if isinstance(value, bool):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _pid(piece: dict[str, Any], index: int = 0) -> str:
    return str(piece.get("canonicalId") or piece.get("id") or f"piece[{index}]")


def is_r6_project(project: dict[str, Any]) -> bool:
    if str(project.get("schemaVersion") or "").lower() == R6_SCHEMA:
        return True
    for piece in project.get("pieces") or []:
        if not isinstance(piece, dict):
            continue
        if piece.get("editProfile") or any(
            isinstance(e, dict) and (
                e.get("xrFamily") in XR_FAMILIES
                or e.get("cineType") in CINE_TYPES
                or e.get("captionPolicyVersion") == "R6"
            )
            for e in piece.get("timeline") or []
        ):
            return True
    return False


def load_r6_libraries(root: Path) -> dict[str, Any]:
    root = Path(root)
    mapping = {
        "xr": "XR_FAMILIES_R6.json",
        "editProfiles": "EDIT_PROFILES_R6.json",
        "cine": "CINE_LIBRARY_R6.json",
        "sfx": "SFX_LIBRARY_R6.json",
        "motion": "MOTION_LIBRARY_R6.json",
        "music": "MUSIC_LIBRARY_R6.json",
        "captions": "CAPTIONS_R6.json",
    }
    out: dict[str, Any] = {}
    for key, name in mapping.items():
        path = root / name
        if path.exists():
            out[key] = json.loads(path.read_text(encoding="utf-8"))
    return out


def ensure_production_checklist(piece: dict[str, Any]) -> dict[str, Any]:
    existing = piece.get("productionChecklist")
    if not isinstance(existing, dict):
        existing = {}
    checklist = copy.deepcopy(existing)
    for key in CHECKLIST_KEYS:
        current = checklist.get(key)
        if isinstance(current, str):
            current = {"status": current}
        if not isinstance(current, dict):
            current = {"status": "pending"}
        current.setdefault("status", "pending")
        checklist[key] = current
    piece["productionChecklist"] = checklist
    return checklist


def checklist_progress(piece: dict[str, Any]) -> int:
    # Validation/progress calculation is read-only. Missing checklist keys count as
    # pending but are not materialized into the canonical document until an explicit
    # editor action asks for defaults.
    checklist = piece.get("productionChecklist") if isinstance(piece.get("productionChecklist"), dict) else {}
    statuses: list[str] = []
    for key in CHECKLIST_KEYS:
        current = checklist.get(key)
        if isinstance(current, dict):
            status = current.get("status")
        else:
            status = current
        statuses.append(str(status or "pending").lower())
    done = sum(1 for status in statuses if status in DONE_STATUSES)
    return round(100 * done / len(statuses)) if statuses else 0


def _asset_missing(asset: dict[str, Any], fam: str) -> list[str]:
    missing: list[str] = []
    aid = str(asset.get("assetId") or asset.get("id") or "asset")
    if not (asset.get("description") or asset.get("whatIsVisible")):
        missing.append(f"{aid}: visual description")
    if fam not in {"TYPO"} and asset.get("assetType") not in {"object", "emoji"} and not asset.get("prompt"):
        missing.append(f"{aid}: prompt")
    if fam in {"PHOTOS", "OBJECTS", "PHOTO_OBJECT"}:
        if not (asset.get("brollReference") or asset.get("googleSearchQuery")):
            missing.append(f"{aid}: broll/search reference")
        if not asset.get("placementRecommendation"):
            missing.append(f"{aid}: placementRecommendation")
        if not asset.get("placementReason"):
            missing.append(f"{aid}: placementReason")
    if fam == "OBJECTS" and len(asset.get("emojiFallback") or []) != 2:
        missing.append(f"{aid}: exactly 2 emojiFallback")
    return missing


def _family_errors(piece_id: str, event: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    critical: list[str] = []
    warnings: list[str] = []
    missing: list[str] = []
    eid = str(event.get("id") or "XR")
    fam = event.get("xrFamily")
    if fam not in XR_FAMILIES:
        # Legacy XR00-XR09 are intentionally preserved and are not R6 family errors.
        if isinstance(fam, str) and fam.startswith("XR"):
            return critical, warnings, missing
        critical.append(f"{piece_id}/{eid}: XR family inválida {fam}")
        return critical, warnings, missing

    if fam == "NO_XR":
        return critical, warnings, missing

    start, end = _num(event.get("start")), _num(event.get("end"))
    duration = (end - start) if start is not None and end is not None else None
    states = event.get("states") if isinstance(event.get("states"), list) else []
    assets = event.get("assets") if isinstance(event.get("assets"), list) else []

    if not event.get("function"):
        missing.append(f"{eid}: function")
    if not (event.get("anchorText") or event.get("sourceQuote")):
        missing.append(f"{eid}: anchorText/sourceQuote")

    if fam == "COMIC_INFO":
        if len(assets) != 1:
            critical.append(f"{piece_id}/{eid}: COMIC_INFO debe tener 1 asset")
        if len(states) != 5:
            critical.append(f"{piece_id}/{eid}: COMIC_INFO debe tener 5 states")
        if duration is not None and not 12 <= duration <= 20:
            warnings.append(f"{piece_id}/{eid}: COMIC_INFO duración {duration:.2f}s fuera 12-20")
    elif fam == "COMIC_CC":
        if len(assets) != 3:
            critical.append(f"{piece_id}/{eid}: COMIC_CC debe tener 3 assets")
        if str(event.get("captionPolicy") or "").upper() != "HIDE":
            warnings.append(f"{piece_id}/{eid}: COMIC_CC debe ocultar captions")
    elif fam == "TYPO":
        if len(states) != 3:
            critical.append(f"{piece_id}/{eid}: TYPO debe tener 3 states")
        if duration is not None and not 6 <= duration <= 12:
            warnings.append(f"{piece_id}/{eid}: TYPO duración fuera 6-12")
    elif fam == "PHOTOS":
        if len(assets) != 3:
            critical.append(f"{piece_id}/{eid}: PHOTOS debe tener 3 assets")
        if duration is not None and not 6 <= duration <= 12:
            warnings.append(f"{piece_id}/{eid}: PHOTOS duración fuera 6-12")
    elif fam == "OBJECTS":
        if len(assets) != 3:
            critical.append(f"{piece_id}/{eid}: OBJECTS debe tener 3 assets")
        if duration is not None and not 6 <= duration <= 12:
            warnings.append(f"{piece_id}/{eid}: OBJECTS duración fuera 6-12")
    elif fam == "PHOTO_OBJECT":
        if len(assets) != 3:
            critical.append(f"{piece_id}/{eid}: PHOTO_OBJECT = 1 foto + 2 objetos")
        if duration is not None and not 8 <= duration <= 12:
            warnings.append(f"{piece_id}/{eid}: PHOTO_OBJECT duración fuera 8-12")

    if fam != "TYPO" and not states:
        missing.append(f"{eid}: states")
    for asset in assets:
        if isinstance(asset, dict):
            missing.extend(_asset_missing(asset, fam))
    return critical, warnings, missing


def _cutter_ready(piece: dict[str, Any]) -> tuple[bool, list[str]]:
    typ = str(piece.get("type") or "")
    if typ not in VIDEO:
        return False, []
    if typ == "full_episode":
        return True, []
    errors: list[str] = []
    ranges = piece.get("sourceRanges") if isinstance(piece.get("sourceRanges"), list) else []
    if not ranges:
        return False, ["sourceRanges faltante"]
    for index, row in enumerate(ranges, 1):
        if not isinstance(row, dict):
            errors.append(f"sourceRange {index} no objeto")
            continue
        start, end = _num(row.get("start")), _num(row.get("end"))
        if start is None or end is None:
            errors.append(f"sourceRange {index} no numérico")
        elif end <= start:
            errors.append(f"sourceRange {index} end<=start")
    return not errors, errors


def _progress_from_content(piece: dict[str, Any], alpha_ready: bool, cutter_ready: bool) -> int:
    # Prefer explicit checklist if the project already uses it.
    if isinstance(piece.get("productionChecklist"), dict):
        return checklist_progress(piece)
    score = 0
    total = 8
    score += bool(piece.get("title"))
    score += bool(piece.get("objective") or piece.get("thesis"))
    score += bool(piece.get("schedule"))
    score += bool(piece.get("parts") or piece.get("staticProduction"))
    score += bool(piece.get("timeline") or piece.get("staticProduction"))
    score += bool(cutter_ready or piece.get("type") in STATIC)
    score += bool(alpha_ready)
    score += bool(piece.get("qa"))
    return round(100 * score / total)


def validate_r6_project(project: dict[str, Any], libraries: dict[str, Any] | None = None) -> dict[str, Any]:
    libraries = libraries or {}
    r6_detected = is_r6_project(project)
    critical: list[str] = []
    warnings: list[str] = []
    piece_reports: list[dict[str, Any]] = []

    if not project.get("projectId"):
        critical.append("projectId faltante")
    pieces = project.get("pieces")
    if not isinstance(pieces, list):
        critical.append("pieces debe ser lista")
        pieces = []

    seen_ids: set[str] = set()
    for index, piece in enumerate(pieces, 1):
        if not isinstance(piece, dict):
            critical.append(f"piece[{index}] no objeto")
            continue
        pid = _pid(piece, index)
        pcritical: list[str] = []
        pwarnings: list[str] = []
        missing: list[str] = []
        typ = str(piece.get("type") or "")
        stage = str(piece.get("stage") or "")
        workflow = str(piece.get("workflowStatus") or "")

        if pid in seen_ids:
            pcritical.append(f"{pid}: canonicalId/id repetido")
        seen_ids.add(pid)
        if typ not in VIDEO | STATIC:
            pcritical.append(f"{pid}: type inválido {typ}")
        if stage not in STAGES:
            pcritical.append(f"{pid}: stage inválido {stage}")
        if workflow not in WORKFLOW:
            pcritical.append(f"{pid}: workflowStatus inválido {workflow}")
        if not isinstance(piece.get("schedule"), dict):
            pwarnings.append(f"{pid}: schedule faltante")

        cutter_ready, cutter_errors = _cutter_ready(piece)
        if typ in VIDEO and stage in {"ALFA", "OMEGA"} and typ != "full_episode" and not cutter_ready:
            missing.extend(cutter_errors)

        if typ in VIDEO:
            timeline = piece.get("timeline") if isinstance(piece.get("timeline"), list) else []
            timeline_ids: list[str] = []
            xrs: list[dict[str, Any]] = []
            captions: list[dict[str, Any]] = []
            for event_index, event in enumerate(timeline, 1):
                if not isinstance(event, dict):
                    pcritical.append(f"{pid}: timeline[{event_index}] no objeto")
                    continue
                eid = str(event.get("id") or f"timeline[{event_index}]")
                if event.get("id"):
                    timeline_ids.append(eid)
                start, end = _num(event.get("start")), _num(event.get("end"))
                if start is None or end is None:
                    pcritical.append(f"{pid}: {eid} start/end no numérico")
                elif end <= start:
                    pcritical.append(f"{pid}: {eid} end<=start")
                if event.get("track") == "xr":
                    xrs.append(event)
                if event.get("track") == "captions":
                    captions.append(event)
                if event.get("track") == "broll" and event.get("type") == "cine":
                    if event.get("cineType") not in CINE_TYPES:
                        pcritical.append(f"{pid}: cineType inválido {event.get('cineType')}")
                    for field in ("function", "visual", "musicAutomation", "captionPolicy"):
                        if event.get(field) in (None, ""):
                            missing.append(f"{eid}: {field}")
                    if "silence" not in event:
                        missing.append(f"{eid}: silence")
                if event.get("track") == "sfx":
                    sfx = event.get("sfx") if isinstance(event.get("sfx"), dict) else {}
                    library_id = sfx.get("libraryId") or event.get("libraryId") or event.get("definitionId")
                    if library_id and libraries.get("sfx"):
                        families = (libraries["sfx"].get("families") or {})
                        if library_id not in families:
                            pwarnings.append(f"{pid}: SFX fuera de librería {library_id}")
                    required = (libraries.get("sfx") or {}).get("eventRequiredFields") or [
                        "libraryId", "variant", "trigger", "purpose", "start", "end", "mix", "status"
                    ]
                    for field in required:
                        if field == "id":
                            value = event.get("id")
                        elif field in {"start", "end"}:
                            value = event.get(field)
                        else:
                            value = sfx.get(field) if field in sfx else event.get(field)
                        if value in (None, ""):
                            missing.append(f"{eid}: SFX {field}")
            if len(timeline_ids) != len(set(timeline_ids)):
                pcritical.append(f"{pid}: timeline ids repetidos")

            profile = piece.get("editProfile") if isinstance(piece.get("editProfile"), dict) else {}
            profile_code = profile.get("code")
            visual_xrs = [event for event in xrs if event.get("xrFamily") != "NO_XR"]
            if r6_detected and profile_code:
                if profile_code not in EDIT_PROFILES:
                    pcritical.append(f"{pid}: editProfile inválido {profile_code}")
                elif profile_code in {"MOTION_SFX", "SFX_ONLY"} and visual_xrs:
                    pwarnings.append(f"{pid}: {profile_code} no autoriza XR visual; hay {len(visual_xrs)} XR")
            if r6_detected and profile_code == "XR_FULL":
                if typ == "intro" and len(visual_xrs) != 6:
                    pwarnings.append(f"{pid}: intro XR_FULL tiene {len(visual_xrs)} XR; canon pide 6")
                if typ == "vertical" and not (2 <= len(visual_xrs) <= 4):
                    pwarnings.append(f"{pid}: vertical XR_FULL tiene {len(visual_xrs)} XR; canon pide 2-4")
                families = [event.get("xrFamily") for event in visual_xrs]
                for left, right in zip(families, families[1:]):
                    if left and left == right:
                        pwarnings.append(f"{pid}: XR consecutivos de misma familia {left}")

            if r6_detected:
                for event in xrs:
                    ecritical, ewarnings, emissing = _family_errors(pid, event)
                    pcritical.extend(ecritical)
                    pwarnings.extend(ewarnings)
                    missing.extend(emissing)
                for event in captions:
                    eid = str(event.get("id") or "caption")
                    source_text = str(event.get("sourceText") or event.get("text") or "").strip()
                    word_count = int(event.get("wordCount") or len(source_text.split()) or 0)
                    mode = event.get("displayMode")
                    if event.get("type") == "caption_group" or event.get("captionPolicyVersion") == "R6":
                        if mode == "hero_word":
                            hero = str(event.get("highlightWord") or event.get("text") or "").split()
                            if len(hero) != 1:
                                pwarnings.append(f"{pid}/{eid}: hero_word debería ser una palabra")
                        elif word_count and not 6 <= word_count <= 17:
                            pwarnings.append(f"{pid}/{eid}: caption group tiene {word_count} palabras; soft range 6-17")
                        if not event.get("partId"):
                            missing.append(f"{eid}: caption partId")
                        if event.get("suppressedBy") and event.get("visibility") != "hidden":
                            pwarnings.append(f"{pid}/{eid}: suppressedBy pero visibility no hidden")
                        if event.get("captionSchema") != "abrxos.caption.v2":
                            missing.append(f"{eid}: captionSchema abrxos.caption.v2")
                        if event.get("captionPolicyVersion") != "R6":
                            missing.append(f"{eid}: captionPolicyVersion R6")
        else:
            static = piece.get("staticProduction")
            if stage in {"ALFA", "OMEGA"} and (not isinstance(static, dict) or not static.get("items")):
                pcritical.append(f"{pid}: estático {stage} sin staticProduction.items")

        # Alpha completeness is stricter than Cutter readiness. R6 video identity
        # requires both editorial fields and production metadata; Cutter readiness
        # remains independent and depends only on source truth.
        if stage == "ALFA":
            if r6_detected and typ in VIDEO:
                if not piece.get("title"):
                    missing.append("title")
                if not piece.get("objective"):
                    missing.append("objective")
                if not piece.get("thesis"):
                    missing.append("thesis")
                if not piece.get("source"):
                    missing.append("source")
                profile_value = piece.get("editProfile")
                if not (isinstance(profile_value, dict) and profile_value.get("code")):
                    missing.append("editProfile")
                if not isinstance(piece.get("schedule"), dict):
                    missing.append("schedule")
            elif not (piece.get("objective") or piece.get("thesis")):
                missing.append("objective/thesis")
            if typ in VIDEO and not piece.get("parts"):
                missing.append("parts")
            if typ in VIDEO and not piece.get("timeline"):
                missing.append("timeline")
        missing = sorted(set(missing))
        alpha_ready = stage != "ALFA" or (not pcritical and not missing)
        progress = _progress_from_content(piece, alpha_ready, cutter_ready)
        critical.extend(pcritical)
        warnings.extend(pwarnings)
        piece_reports.append({
            "id": pid,
            "type": typ,
            "stage": stage,
            "workflowStatus": workflow,
            "alphaReady": bool(alpha_ready),
            "cutterReady": bool(cutter_ready),
            "progressPercent": progress,
            "missing": missing,
            "critical": pcritical,
            "warnings": pwarnings,
        })

    return {
        "schema": VALIDATION_SCHEMA,
        "r6Detected": r6_detected,
        "projectId": project.get("projectId"),
        "critical": critical,
        "warnings": warnings,
        "pieces": piece_reports,
        "summary": {
            "pieceCount": len(piece_reports),
            "criticalCount": len(critical),
            "warningCount": len(warnings),
            "alphaReadyCount": sum(1 for row in piece_reports if row["alphaReady"]),
            "cutterReadyCount": sum(1 for row in piece_reports if row["cutterReady"]),
        },
    }
