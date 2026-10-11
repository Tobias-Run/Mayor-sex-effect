"""Protect expansion selection and primary vote reconciliation."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'pilot'))
from cohort_expansion import screen, validate_official, german_count


def pair():
    base = {'state': '12', 'ags': '12064044', 'ags_name': 'Example',
            'election_type': 'Bürgermeisterwahl', 'office_type': '',
            'flag_superseded': 'FALSE', 'flag_shared_ags': 'FALSE',
            'flag_decisive_round_missing': 'FALSE', 'has_stichwahl': 'TRUE',
            'election_date': '2025-09-28', 'election_date_sw': '2025-10-19',
            'valid_votes': '1000', 'n_candidates_sw': '2',
            'candidate_gender': '', 'candidate_gender_source': ''}
    return [dict(base, candidate_name='Person, One', candidate_votes_sw='51',
                 candidate_rank_sw='1', candidate_voteshare_sw='.51', is_winner='TRUE'),
            dict(base, candidate_name='Person, Two', candidate_votes_sw='49',
                 candidate_rank_sw='2', candidate_voteshare_sw='.49', is_winner='FALSE')]


class ExpansionTests(unittest.TestCase):
    def test_unresolved_and_same_prediction_labels_remain_in_frame(self):
        for label in ('', 'm'):
            rows = pair()
            for row in rows:
                row['candidate_gender'] = label; row['candidate_name'] = ''
            event, reason = screen(rows)
            self.assertIsNone(reason)
            self.assertFalse(event['both_names_available'])
            self.assertEqual(event['absolute_margin_pp'], 2)

    def test_runoff_uses_its_own_vote_sum_not_first_round_valid_votes(self):
        event, _ = screen(pair())
        self.assertEqual(event['valid_votes'], 100)
        rows = pair()
        for r in rows:
            r['has_stichwahl'] = 'FALSE'; r['n_candidates_hw'] = '2'
            for key in ('votes', 'rank', 'voteshare'):
                r['candidate_' + key + '_hw'] = r['candidate_' + key + '_sw']
        self.assertEqual(screen(rows)[1], 'valid_votes_do_not_reconcile')

    def test_winner_and_quality_flags_cannot_be_silently_ignored(self):
        rows = pair(); rows[0]['candidate_votes_sw'] = '49'; rows[1]['candidate_votes_sw'] = '51'
        self.assertEqual(screen(rows)[1], 'winner_votes_disagree')
        rows = pair(); rows[1]['flag_shared_ags'] = 'TRUE'
        self.assertEqual(screen(rows)[1], 'source_quality_flag')

    def test_association_offices_and_ties_are_separate_dispositions(self):
        rows = pair()
        for r in rows: r['election_type'] = 'VG-Bürgermeisterwahl'
        self.assertEqual(screen(rows)[1], 'association_office')
        rows = pair(); rows[0]['candidate_votes_sw'] = '49'
        self.assertEqual(screen(rows)[1], 'invalid_or_tied_votes')

    def test_official_validation_requires_full_pair_and_committee_winner(self):
        event, _ = screen(pair())
        source = ('<html><table><tr><td>Wahltag</td><td>19.10.2025</td></tr>'
                  '<tr><td>Wahlart</td><td>Stichwahl</td></tr><tr><td>Stadt</td><td>Example</td></tr>'
                  '<tr><td>Gültige Stimmen</td><td>100</td><td>99</td></tr></table>'
                  '<table><tr><td>1</td><td>Person, One</td><td>A</td><td>51</td><td>51</td></tr>'
                  '<tr><td>2</td><td>Person, Two</td><td>B</td><td>49</td><td>49</td></tr></table>'
                  '<p>Der Wahlausschuss stellte fest, dass Person, One gewählt worden ist.</p></html>')
        self.assertTrue(validate_official(source.encode(), event))
        self.assertTrue(validate_official(source.replace('Person, One', 'Dr.Person, Dr. One').replace('Person, Two', 'Person, Dr. Two').encode(), event))
        self.assertTrue(validate_official(source.replace('dass Person, One', 'dass Person,  One').encode(), event))
        for changed in (source.replace('Person, Two', 'Other, Two'),
                        source.replace('dass Person, One', 'dass Person, Two'),
                        source.replace('<td>100</td>', '<td>101</td>')):
            with self.assertRaises(ValueError): validate_official(changed.encode(), event)

    def test_german_decimal_percentages_are_not_vote_counts(self):
        self.assertEqual(german_count('2.628'), 2628)
        for invalid in ('2,628', '26.28', '-1', '51,57'):
            with self.assertRaises(ValueError): german_count(invalid)


if __name__ == '__main__': unittest.main()
