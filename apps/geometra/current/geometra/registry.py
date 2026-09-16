from __future__ import annotations
import copy, json
from pathlib import Path
from typing import Any


class RendererRegistry:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._items: dict[str, dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        self._items.clear()
        if not self.root.exists():
            return
        for path in sorted(self.root.glob('*/manifest.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            rid = data['rendererId']
            data['_path'] = str(path.parent)
            self._items[rid] = data

    def list(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(self._items[k]) for k in sorted(self._items)]

    def get(self, renderer_id: str) -> dict[str, Any]:
        if renderer_id not in self._items:
            raise KeyError(f'Unknown renderer: {renderer_id}')
        return copy.deepcopy(self._items[renderer_id])


class CatalogRegistry:
    FILES = {'xr': 'xr_catalog.json', 'sfx': 'sfx_catalog.json', 'motion': 'motion_catalog.json', 'captions': 'caption_styles.json'}

    def __init__(self, root: Path):
        self.root = Path(root)
        self._data: dict[str, list[dict[str, Any]]] = {}
        self.reload()

    def reload(self) -> None:
        self._data = {}
        for kind, filename in self.FILES.items():
            path = self.root / filename
            if path.exists():
                obj = json.loads(path.read_text(encoding='utf-8'))
                rows = obj.get('items', obj if isinstance(obj, list) else [])
                self._data[kind] = rows if isinstance(rows, list) else []
            else:
                self._data[kind] = []

    def list(self, kind: str) -> list[dict[str, Any]]:
        return copy.deepcopy(self._data.get(kind, []))

    def get(self, kind: str, item_id: str) -> dict[str, Any]:
        for row in self._data.get(kind, []):
            if str(row.get('id')) == str(item_id):
                return copy.deepcopy(row)
        return {'id': item_id, 'name': f'Custom {item_id}', 'kind': 'custom', 'fallback': True, 'description': 'Unknown/custom definition preserved by canonical document.'}
