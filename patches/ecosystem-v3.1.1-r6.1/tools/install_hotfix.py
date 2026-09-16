from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .apply_hotfix import apply_hotfix
from .verify_hotfix import verify_hotfix
from .revert_hotfix import revert_hotfix


def install_hotfix(root: Path, *, home: Path | None = None, targets: dict[str, Path] | None = None) -> dict[str, Any]:
    root = Path(root).resolve()
    applied = apply_hotfix(root, home=home, targets=targets)
    report = verify_hotfix(root, home=home, targets=targets)
    if report['ok']:
        return {
            'status': 'applied_and_verified',
            'hotfixId': applied['hotfixId'],
            'backupId': applied['backupId'],
            'components': applied['components'],
            'verify': report,
        }
    reverted = revert_hotfix(home=home, backup_id=applied['backupId'])
    return {
        'status': 'rolled_back_after_verify_failure',
        'hotfixId': applied['hotfixId'],
        'backupId': applied['backupId'],
        'components': applied['components'],
        'verify': report,
        'revert': reverted,
    }


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--home')
    args = ap.parse_args()
    result = install_hotfix(Path(args.root), home=Path(args.home).expanduser() if args.home else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'applied_and_verified' else 2)
