"""Failure-mode checks for provisional procurement matches and sample bounds."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/pilot'))
AVAILABLE = bool(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'))
if AVAILABLE:
    import bavaria_bounded_route as route


@unittest.skipUnless(AVAILABLE, 'Optional early-feasibility numerical dependencies unavailable')
class BoundedRouteTests(unittest.TestCase):
    def test_joint_or_ambiguous_buyers_are_not_elections(self):
        mapping = {'gemeinde test': {'09111111'}}
        self.assertIsNone(route.match_buyer({'buyer-name': {'deu': ['Gemeinde Test', 'Stadt Other']},
                                             'buyer-legal-type': ['la']}, mapping)[0])
        self.assertIsNone(route.match_buyer({'buyer-name': {'deu': ['Gemeinde Test']},
                                             'buyer-legal-type': ['la']},
                                            {'gemeinde test': {'09111111', '09222222'}})[0])

    def test_substrings_and_public_enterprises_are_not_municipal_matches(self):
        mapping = {'gemeinde test': {'09111111'}}
        for name,kind in [('Gemeinde Test Bau GmbH', 'la'), ('Gemeinde Test', 'pub-undert')]:
            self.assertIsNone(route.match_buyer({'buyer-name': {'deu': [name]},
                                                'buyer-legal-type': [kind]}, mapping)[0])

    def test_multilingual_translation_is_not_another_buyer(self):
        notice = {'buyer-name': {'deu': ['Gemeinde Test'], 'eng': ['Municipality of Test']},
                  'buyer-legal-type': ['la']}
        ags,status = route.match_buyer(notice, {'gemeinde test': {'09111111'}})
        self.assertEqual(ags, '09111111')
        self.assertTrue(status.startswith('provisional_'))

    def test_upper_bounds_respect_observed_winner_and_loser_presentations(self):
        pair = [{'winner': True, 'official_title_presentation': 'female'},
                {'winner': False, 'official_title_presentation': 'missing'}]
        before = json.dumps(pair)
        self.assertEqual(route.options(pair), [1])
        self.assertEqual(json.dumps(pair), before)
        pair[0]['official_title_presentation'] = 'male'
        self.assertEqual(route.options(pair), [0])
        pair[1]['official_title_presentation'] = 'male'
        self.assertEqual(route.options(pair), [])
        pair[1]['official_title_presentation'] = 'conflict'
        with self.assertRaises(ValueError):
            route.options(pair)

    def test_exact_margin_boundary_and_incomplete_votes(self):
        event = {'candidate_identity': {'candidates': [{'votes': 51}, {'votes': 49}], 'valid_votes': 100}}
        self.assertEqual(route.margin(event), 2)
        event['candidate_identity']['valid_votes'] = 101
        with self.assertRaises(ValueError):
            route.margin(event)

    def test_source_semantic_comparison_ignores_order_but_detects_changes(self):
        rows = [{'state': '09', 'candidate_gender': ''}, {'state': '09', 'candidate_gender': 'w'}]
        self.assertEqual(route.semantic_digest(rows), route.semantic_digest(rows[::-1]))
        altered = [{'state': '09', 'candidate_gender': 'm'}, rows[1]]
        self.assertNotEqual(route.semantic_digest(rows), route.semantic_digest(altered))

    def test_incomplete_duplicate_or_changed_snapshot_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def save(payload, total=2):
                raw = json.dumps(payload).encode()
                (root/'page-1.json').write_bytes(raw)
                meta = {'query': 'q', 'fields': route.FIELDS, 'total_notice_count': total,
                        'pages': [{'file': 'page-1.json', 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}]}
                (root/'retrieval.json').write_text(json.dumps(meta))
            with patch.object(route, 'RAW', root):
                save({'totalNoticeCount': 2, 'notices': [{'publication-number': 'A'}, {'publication-number': 'A'}]})
                with self.assertRaises(ValueError): route.snapshot('q')
                save({'totalNoticeCount': 2, 'notices': [{'publication-number': 'A'}]})
                with self.assertRaises(ValueError): route.snapshot('q')
                save({'totalNoticeCount': 1, 'notices': [{'publication-number': 'A'}]}, 1)
                (root/'page-1.json').write_text('{}')
                with self.assertRaises(ValueError): route.snapshot('q')


if __name__ == '__main__':
    unittest.main()
