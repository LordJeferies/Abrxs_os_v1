from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENGINE_VERSION = "1.0.1"
CANON_VERSION = "R6"
CANON_FAMILY = "R6"
CANON_REVISION = "R6.1"


def safe_slug(value: str, fallback: str = "item") -> str:
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.")
    return value or fallback


def deep_merge(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        out = copy.deepcopy(base)
        for key, value in patch.items():
            out[key] = deep_merge(out[key], value) if key in out else copy.deepcopy(value)
        return out
    return copy.deepcopy(patch)


def _json_write(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class BrandStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.brands_dir = self.root / "brands"
        self.references_dir = self.root / "references"
        self.brands_dir.mkdir(parents=True, exist_ok=True)
        self.references_dir.mkdir(parents=True, exist_ok=True)

    def save(self, project: dict) -> dict:
        project = copy.deepcopy(project)
        brand_id = project.get("brandId") or project.get("brandName") or "brand"
        slug = project.get("slug") or safe_slug(brand_id, "brand")
        project["slug"] = slug
        project.setdefault("brandId", brand_id)
        project.setdefault("createdAt", datetime.now(timezone.utc).isoformat())
        project["updatedAt"] = datetime.now(timezone.utc).isoformat()
        _json_write(self.brands_dir / f"{slug}.json", project)
        return {"slug": slug, "path": str(self.brands_dir / f"{slug}.json"), "project": project}

    def load(self, slug: str) -> dict:
        path = self.brands_dir / f"{safe_slug(slug)}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self) -> list[dict]:
        out = []
        for path in sorted(self.brands_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            out.append({
                "slug": obj.get("slug", path.stem),
                "brandId": obj.get("brandId", ""),
                "brandName": obj.get("brandName", ""),
                "updatedAt": obj.get("updatedAt", ""),
                "completion": calculate_completion(obj),
            })
        return out

    def delete(self, slug: str) -> bool:
        path = self.brands_dir / f"{safe_slug(slug)}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def save_reference(self, slug: str, filename: str, data: bytes) -> dict:
        brand_dir = self.references_dir / safe_slug(slug)
        brand_dir.mkdir(parents=True, exist_ok=True)
        clean = Path(filename).name.replace("\x00", "")
        clean = re.sub(r"[^A-Za-z0-9._() -]+", "_", clean).strip() or "reference.bin"
        target = brand_dir / clean
        target.write_bytes(data)
        return {"filename": clean, "path": str(target), "bytes": len(data), "sha256": _sha256(target)}


def calculate_completion(project: dict) -> dict:
    blocks = {
        "raw": bool(str(project.get("rawContext", "")).strip()),
        "form": bool(project.get("brandForm")),
        "method": bool(((project.get("method") or {}).get("summary") or {})),
        "adapter": bool(project.get("brandAdapterDraft")),
    }
    completed = sum(1 for v in blocks.values() if v)
    return {"blocks": blocks, "percent": round(completed / len(blocks) * 100)}


def _default_prompt(project: dict) -> str:
    brand = project.get("brandName") or project.get("brandId") or "la marca"
    return f"""ACTÚA COMO ESTRATEGA DE MARCA Y ARQUITECTO DE BRAND ADAPTER ABRXOS R6.\n\nOBJETIVO\nAnaliza el paquete de {brand} y produce dos entregables coherentes pero separados:\n1. estrategia de marca estructurada usando los cinco drivers del Branding Method aportado por el usuario;\n2. Brand Adapter ABRXOS R6 operativo para contenido, edición y producción.\n\nREGLAS\n- Preserva literalmente RAW_BRAND_CONTEXT como fuente.\n- Distingue USER_CONFIRMED, SOURCE_DERIVED, AI_INFERENCE y NEEDS_REVIEW.\n- No inventes tipografías, colores oficiales, logos, claims, clientes, competidores ni datos no presentes.\n- El Branding Method describe estrategia; el Brand Adapter describe ejecución. No los mezcles.\n- Si el PDF original del método se adjunta, úsalo como referencia metodológica proporcionada por el usuario; no lo reproduzcas.\n- Conserva campos desconocidos del Brand Adapter.\n\nSALIDA\nDevuelve dos archivos:\nBRAND_STRATEGY_R6.json + BRAND_STRATEGY_R6.txt\nBRAND_ADAPTER_R6.json + BRAND_ADAPTER_R6.txt\nEl JSON debe ser válido y el TXT legible.\n"""


def _ecosystem_contract(adapter_template: dict) -> dict:
    return {
        "schemaVersion": "abrxos.ecosystem-contract.v1",
        "canonFamily": CANON_FAMILY,
        "canonRevision": CANON_REVISION,
        "brandSchema": str(adapter_template.get("schemaVersion") or "abrxos.brand-adapter.r6"),
        "brandAdapterVersion": str(adapter_template.get("adapterVersion") or CANON_REVISION),
        "features": ["brandMethodSeparated", "brandAdapterR6", "contentBuilderHandoffR61"],
        "contentBuilderMinimum": "1.0.1-r6.1",
        "geometraMinimum": "3.1.1-r6.1",
        "builder": "ABRXOS X Brand Builder",
        "builderVersion": ENGINE_VERSION,
    }


def build_brand_ai_package(project: dict, export_root: Path, resources_dir: Path) -> dict:
    export_root = Path(export_root)
    resources_dir = Path(resources_dir)
    slug = safe_slug(project.get("brandId") or project.get("brandName") or "brand")
    package_name = f"{slug.upper()}_BRAND_AI_PACKAGE_R6"
    folder = export_root / package_name
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)

    adapter_template_path = resources_dir / "brand_adapter_template.json"
    if not adapter_template_path.exists():
        raise FileNotFoundError(f"Missing resource: {adapter_template_path}")
    adapter_template = json.loads(adapter_template_path.read_text(encoding="utf-8"))

    start_here = f"""ABRXOS X · BRAND BUILDER V1\n\nMarca: {project.get('brandName') or project.get('brandId') or 'Sin nombre'}\nBrand ID: {project.get('brandId','')}\nCanon: {project.get('canonVersion', CANON_VERSION)} / R6.1\n\nEste paquete NO ejecuta IA. Adjunta los archivos indicados en 01_QUE_SUBIR_A_CHATGPT.txt a ChatGPT u otra IA y conserva los JSON de salida para reimportarlos.\n\nCapas separadas:\n- Branding Method: estrategia/ADN.\n- Brand Adapter R6: contrato operativo de comunicación y producción.\n"""
    upload = """ORDEN RECOMENDADO DE ARCHIVOS\n\n1. 02_PROMPT_FINAL.txt\n2. 03_RAW_BRAND_CONTEXT.txt\n3. 04_BRAND_FORM.json\n4. 05_BRANDING_METHOD_INPUT.json\n5. 06_BRAND_ADAPTER_TEMPLATE_R6.json\n6. 08_SOURCE_REFERENCES.json\n7. 09_BRAND_DRAFT.json\n8. 10_BRANDING_METHOD_REGISTRY.json\n9. 11_BRANDING_METHOD_SOURCE_NOTE.txt\n10. Si existe la carpeta REFERENCES/, adjunta los archivos relevantes.\n11. Para análisis profundo, adjunta también el PDF original de Branding Method proporcionado por el usuario.\n\nDespués escribe: \"Ejecuta el paquete. Devuelve estrategia JSON+TXT y Brand Adapter R6 JSON+TXT.\"\n"""

    files: dict[str, str] = {
        "00_START_HERE.txt": start_here,
        "01_QUE_SUBIR_A_CHATGPT.txt": upload,
        "02_PROMPT_FINAL.txt": project.get("compiledPrompt") or _default_prompt(project),
        "03_RAW_BRAND_CONTEXT.txt": str(project.get("rawContext", "")),
    }
    for name, obj in {
        "04_BRAND_FORM.json": project.get("brandForm", {}),
        "05_BRANDING_METHOD_INPUT.json": project.get("method", {}),
        "06_BRAND_ADAPTER_TEMPLATE_R6.json": adapter_template,
        "07_EXPECTED_OUTPUT_SCHEMA.json": {
            "strategy": {"schemaVersion": "abrxos.brand-strategy.r6", "brandId": project.get("brandId", ""), "drivers": {}},
            "brandAdapter": adapter_template,
        },
        "08_SOURCE_REFERENCES.json": project.get("references", []),
        "09_BRAND_DRAFT.json": project,
    }.items():
        files[name] = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"

    for name, content in files.items():
        (folder / name).write_text(content, encoding="utf-8")

    method_registry = resources_dir / "branding_method_registry.json"
    if method_registry.exists():
        shutil.copy2(method_registry, folder / "10_BRANDING_METHOD_REGISTRY.json")
    source_note = resources_dir / "BRANDING_METHOD_SOURCE_NOTE.txt"
    if source_note.exists():
        shutil.copy2(source_note, folder / "11_BRANDING_METHOD_SOURCE_NOTE.txt")

    refs_dir = folder / "REFERENCES"
    for ref in project.get("references", []) or []:
        src = Path(str(ref.get("path", ""))).expanduser()
        if src.exists() and src.is_file():
            refs_dir.mkdir(exist_ok=True)
            target = refs_dir / Path(ref.get("filename") or src.name).name
            shutil.copy2(src, target)

    contract = _ecosystem_contract(adapter_template)
    _json_write(folder / "contract_manifest.json", contract)

    manifest_files = []
    for path in sorted(folder.rglob("*")):
        if path.name == "package_manifest.json" or not path.is_file():
            continue
        manifest_files.append({"path": str(path.relative_to(folder)), "bytes": path.stat().st_size, "sha256": _sha256(path)})
    manifest = {
        "schemaVersion": "abrxos.ai-package.brand.v1",
        "builder": "ABRXOS X Brand Builder",
        "builderVersion": ENGINE_VERSION,
        "canonVersion": project.get("canonVersion", CANON_VERSION),
        "canonFamily": CANON_FAMILY,
        "canonRevision": CANON_REVISION,
        "contractFile": "contract_manifest.json",
        "brandId": project.get("brandId", ""),
        "brandName": project.get("brandName", ""),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "files": manifest_files,
    }
    _json_write(folder / "package_manifest.json", manifest)

    zip_path = export_root / f"{package_name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(folder)))

    return {"folder": str(folder), "zip": str(zip_path), "manifest": manifest}
