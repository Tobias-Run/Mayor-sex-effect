import copy
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update', ROOT / 'src/report/build_feasibility_update.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FeasibilityUpdateTests(unittest.TestCase):
    def test_changed_and_duplicate_pins_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'evidence').write_text('changed')
            pin = {'artifact': 'evidence', 'bytes': 7, 'sha256': 'not-the-hash'}
            with self.assertRaisesRegex(ValueError, 'Changed public evidence'):
                module.verify(root, {'inputs': [pin]})
            import hashlib
            pin['sha256'] = hashlib.sha256(b'changed').hexdigest()
            with self.assertRaisesRegex(ValueError, 'Duplicate or unsafe'):
                module.verify(root, {'inputs': [pin, pin]})

    def test_denominators_and_window_alignment_are_checked(self):
        base = ROOT / 'docs/feasibility'
        def rows(n):
            with (base / n).open(newline='') as f:
                return list(csv.DictReader(f))
        events = rows('eligibility-scoreboard-events.csv')
        exposure = rows('readiness-exposure-audit.csv')
        summary = json.loads((base / 'readiness-p4-p5-summary.json').read_text())
        self.assertEqual(module.reconcile(events, exposure, summary)['provisional_elections'], 6)
        changed = copy.deepcopy(exposure)
        changed[0]['supported_tender_statistics'] = '0'
        with self.assertRaisesRegex(ValueError, 'denominator mismatch'):
            module.reconcile(events, changed, summary)
        changed = copy.deepcopy(exposure)
        changed[0]['existing_window_matches_reference'] = 'False'
        with self.assertRaisesRegex(ValueError, 'Window alignment'):
            module.reconcile(events, changed, summary)

    def test_public_only_rebuild_is_identical(self):
        source = ROOT / 'manuscript/feasibility-2026-10-16'
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            destination = root / 'manuscript/feasibility-2026-10-16'
            destination.mkdir(parents=True)
            for n in ['inputs.json', 'manuscript.template.md']:
                (destination / n).write_bytes((source / n).read_bytes())
            manifest = json.loads((source / 'inputs.json').read_text())
            for pin in manifest['inputs']:
                path = root / pin['artifact']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / pin['artifact']).read_bytes())
            module.build(root, destination)
            for n in ['manuscript.md', 'facts.json']:
                self.assertEqual((destination / n).read_bytes(), (source / n).read_bytes())
