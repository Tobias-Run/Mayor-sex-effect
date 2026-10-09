"""Protect the report against stale evidence and misleading sample accounting."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/report'))
import build_feasibility_report as report


class ReportTests(unittest.TestCase):
    def setUp(self):
        doc = report.DOC
        self.inputs = [
            report.numeric_map(report.csv_rows(doc/'nrw-election-register-summary.csv'), value='count'),
            report.csv_rows(doc/'nrw-early-linkage-matrix.csv'),
            json.loads((doc/'nrw-early-feasibility-checkpoint.json').read_text()),
            report.numeric_map([r for r in report.csv_rows(doc/'nrw-buyer-and-phase-summary.csv')
                                if r['stage'] == 'buyer_scope']),
            report.numeric_map(report.csv_rows(doc/'nrw-procedure-scope-summary.csv')),
            json.loads((doc/'bavaria-bounded-checkpoint.json').read_text()),
            report.csv_rows(doc/'bavaria-bounded-linkage-matrix.csv'),
            report.csv_rows(doc/'bavaria-bounded-band-summary.csv'),
            report.csv_rows(doc/'nrw-early-selection-audit.csv'),
        ]

    def test_pins_detect_changed_contents_even_at_same_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/'public.csv'
            original = b'count\n380\n'
            path.write_bytes(original)
            manifest = {'inputs': [{'artifact': path.name, 'bytes': len(original),
                                   'sha256': hashlib.sha256(original).hexdigest()}]}
            report.verify_inputs(root, manifest)
            path.write_bytes(b'count\n381\n')
            with self.assertRaisesRegex(ValueError, 'Pinned public report input changed'):
                report.verify_inputs(root, manifest)

    def test_duplicate_or_escaping_pins_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/'one.csv'
            path.write_bytes(b'x')
            entry = {'artifact': path.name, 'bytes': 1, 'sha256': hashlib.sha256(b'x').hexdigest()}
            with self.assertRaisesRegex(ValueError, 'Duplicate report input'):
                report.verify_inputs(root, {'inputs': [entry, entry]})
            with self.assertRaisesRegex(ValueError, 'Input escapes repository'):
                report.verify_inputs(root, {'inputs': [dict(entry, artifact='../one.csv')]})

    def test_report_uses_frozen_public_inputs(self):
        pins = report.verify_inputs()
        self.assertEqual(pins['evidence_cutoff'], '2026-10-05')
        self.assertEqual(pins['report_date'], '2026-10-09')
        self.assertTrue(all(r['artifact'].startswith('docs/feasibility/') for r in pins['inputs']))
        facts = report.collect_facts()
        self.assertEqual((facts['bavaria_general'], facts['bavaria_calendar_2020']), (902, 906))
        self.assertEqual((facts['bavaria_indexed_counts'], facts['bavaria_indexed_municipalities']), (35, 6))
        self.assertEqual((facts['nrw_linked'], facts['nrw_linked_units']), (3, 13))
        self.assertEqual(facts['certified_main_elections'], 0)
        self.assertFalse(facts['causal_effects_estimated'])
        self.assertFalse(facts['independent_review_complete'])

    def test_all_pilot_window_units_cannot_replace_mixed_pair_intersection(self):
        self.inputs[2]['candidate_window_observed_units'] = 25
        with self.assertRaisesRegex(ValueError, 'candidate-window units differ'):
            report.reconcile(*self.inputs)

    def test_more_result_units_do_not_create_independent_elections(self):
        before = report.reconcile(*self.inputs)
        altered = copy.deepcopy(self.inputs)
        row = next(r for r in altered[1] if r['pair_status'] == 'mixed_public_presentation'
                   and int(r['candidate_window_called_dated_count_units']) > 0)
        row['candidate_window_called_dated_count_units'] = str(int(row['candidate_window_called_dated_count_units']) + 100)
        altered[2]['candidate_window_observed_units'] += 100
        after = report.reconcile(*altered)
        self.assertEqual(len(before[2]), len(after[2]))

    def test_repeated_election_rows_are_not_new_assignments(self):
        self.inputs[1].append(dict(self.inputs[1][0]))
        with self.assertRaisesRegex(ValueError, 'close-review election counts differ'):
            report.reconcile(*self.inputs)

    def test_bavaria_counted_units_and_municipalities_remain_distinct(self):
        self.inputs[5]['municipalities_with_indexed_total_tender_counts'] = 7
        with self.assertRaisesRegex(ValueError, 'indexed-count municipalities differ'):
            report.reconcile(*self.inputs)

    def test_procedure_strata_must_partition_observed_units(self):
        codes = json.loads(self.inputs[4]['observed_unit_procedure_code_counts'])
        codes['open'] += 1
        self.inputs[4]['observed_unit_procedure_code_counts'] = json.dumps(codes)
        with self.assertRaisesRegex(ValueError, 'do not partition units'):
            report.reconcile(*self.inputs)

    def test_review_or_eligibility_changes_require_report_revision(self):
        for key, value, expected in [
            ('independent_second_coding_completed', True, 'Independent-review status changed'),
            ('certified_main_study_elections', 1, 'Main eligibility changed'),
            ('causal_effects_estimated', True, 'Effect-status changed'),
        ]:
            with self.subTest(key=key):
                changed = copy.deepcopy(self.inputs)
                changed[2][key] = value
                with self.assertRaisesRegex(ValueError, expected):
                    report.reconcile(*changed)

    def test_template_preserves_nested_math_but_rejects_missing_facts(self):
        template = r'{{count}} pairs; $\frac{V_{Fi}}{V_{Mi}}$'
        rendered, used = report.render_template(template, {'count': 3})
        self.assertEqual(rendered, r'3 pairs; $\frac{V_{Fi}}{V_{Mi}}$')
        self.assertEqual(used, ['count'])
        for bad in ('{{unknown}}', '{{count:bad}}', '{{count'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                report.render_template(bad, {'count': 3})

    def test_pdf_identifier_is_deterministic_without_changing_other_bytes(self):
        prefix, suffix = b'%PDF-1.5\nunchanged objects\n', b'\nstartxref\n123\n%%EOF\n'
        with tempfile.TemporaryDirectory() as tmp:
            files = [Path(tmp)/'first.pdf', Path(tmp)/'second.pdf']
            for path, identifier in zip(files, (b'a'*32, b'b'*32)):
                original = prefix + b'/ID[<' + identifier + b'><' + identifier + b'>]' + suffix
                path.write_bytes(original)
                report.normalize_pdf_identifier(path)
                normalized = path.read_bytes()
                self.assertEqual(len(original), len(normalized))
                self.assertTrue(normalized.startswith(prefix) and normalized.endswith(suffix))
                report.normalize_pdf_identifier(path)
                self.assertEqual(normalized, path.read_bytes())
            self.assertEqual(files[0].read_bytes(), files[1].read_bytes())

    def test_missing_or_duplicated_pdf_identifiers_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bad.pdf'
            for contents in (b'%PDF-no-identifier', (b'/ID[<' + b'a'*32 + b'><' + b'a'*32 + b'>]')*2):
                with self.subTest(contents=contents):
                    path.write_bytes(contents)
                    with self.assertRaisesRegex(ValueError, 'Expected one fixed-length PDF identifier pair'):
                        report.normalize_pdf_identifier(path)
                    self.assertEqual(path.read_bytes(), contents)


if __name__ == '__main__':
    unittest.main()
