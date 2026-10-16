"""Verify published report/checkpoint pins without local original-source bundles."""
import json
from pathlib import Path
from build_feasibility_update import verify

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = [
    ('manuscript/report-inputs.json', 'inputs'),
    ('manuscript/report-reproduction-checkpoint.json', 'outputs'),
    ('manuscript/feasibility-2026-10-16/inputs.json', 'inputs'),
    ('manuscript/feasibility-2026-10-16/verification.json', 'outputs'),
    ('docs/feasibility/internal-review-selection-inputs-2026-10-16.json', 'inputs'),
]


def main():
    seen, count = {}, 0
    for name, field in MANIFESTS:
        pins = json.loads((ROOT / name).read_text())[field]
        verify(ROOT, {'inputs': pins})
        for pin in pins:
            if pin['artifact'] in seen and seen[pin['artifact']] != pin['sha256']:
                raise ValueError('Conflicting published evidence pins: ' + pin['artifact'])
            seen[pin['artifact']] = pin['sha256']
        count += len(pins)
    print(json.dumps({'manifest_collections_verified': len(MANIFESTS),
                      'pin_entries_verified': count, 'unique_artifacts_verified': len(seen),
                      'private_original_source_audit_repeated': False}, indent=2))


if __name__ == '__main__':
    main()
