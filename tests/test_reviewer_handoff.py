"""Guard against stale originals and first-coder labels in a reviewer handoff."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src/report'))
import prepare_reviewer_handoff as handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.original = self.root/'data/raw/original.html'
        self.original.parent.mkdir(parents=True)
        self.original.write_bytes(b'original publication')
        self.packet = dict(case_id='R001', measurement_codebook='codebook.md',
                           municipality_for_identity='Example', target_event_year=2020,
                           candidates=[dict(slot=s, official_candidate_name=s) for s in ('A','B')],
                           original_sources=[dict(source_id='primary-example', source_url='https://example.org',
                             sha256=hashlib.sha256(self.original.read_bytes()).hexdigest(),
                             local_file='data/raw/original.html', retrieved_at_utc='2026-10-05T00:00:00Z')],
                           blinding_limit='Original text can reveal results')

    def test_stale_original_is_rejected(self):
        handoff.validate_packet(self.packet, self.root)
        self.original.write_bytes(b'changed publication')
        with self.assertRaisesRegex(ValueError, 'hash differs'):
            handoff.validate_packet(self.packet, self.root)

    def test_prior_labels_or_votes_are_rejected(self):
        for level, key in [('top','first_coder_pair_status'), ('candidate','winner'), ('source','accepted_quote')]:
            changed = copy.deepcopy(self.packet)
            target = changed if level == 'top' else changed['candidates' if level == 'candidate' else 'original_sources'][0]
            target[key] = 'leaked'
            with self.subTest(level=level), self.assertRaises(ValueError):
                handoff.validate_packet(changed, self.root)

    def test_official_votes_and_paths_outside_originals_are_rejected(self):
        for key, value in [('source_id','nrw-result-123'), ('local_file','../secret')]:
            changed = copy.deepcopy(self.packet)
            changed['original_sources'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                handoff.validate_packet(changed, self.root)


if __name__ == '__main__':
    unittest.main()
