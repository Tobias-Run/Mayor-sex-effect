"""Protect NRW election scope, single-candidate ballots and exact identities."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pilot"))
from nrw_election_register import (SUMMARIES, compare_decisive_pair, compare_gerda,
                                   name_key, official_ags, parse_detail, universe)


class NRWUniverseTests(unittest.TestCase):
    def summary(self, rows):
        return ('Election\nEndgültige Ergebnisse\n\n'
                'Verwaltungsbezirks-Nr.;Verwaltungsbezirksname;Datum\n' + rows)

    def test_county_office_is_excluded_and_no_election_is_retained(self):
        text = self.summary('111000;Krfr. Stadt Example;13.09.2020\n'
                            '112000;Krfr. Stadt Other;Es findet keine Wahl statt\n'
                            '154000;Kreis Example;13.09.2020\n')
        entries, excluded = universe([(SUMMARIES[1], text)])
        self.assertEqual(len(entries), 2)
        self.assertEqual(excluded, 1)
        self.assertFalse(entries[1]['election_held'])

    def test_aachen_archive_code_is_not_naively_prefixed(self):
        self.assertEqual(official_ags('313000'), '05334002')
        self.assertEqual(official_ags('962024'), '05962024')

    def test_contradictory_or_duplicate_dates_are_rejected(self):
        for rows in ('154004;Example;13.09.2020\n154004;Example;Es findet keine Wahl statt\n',
                     '154004;Example;27.09.2020\n',
                     '154004;Example;13.09.2020\n154004;Example;13.09.2020\n'):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                universe([(SUMMARIES[0], self.summary(rows))])


class NRWDetailTests(unittest.TestCase):
    def entry(self):
        return {'municipality_source': 'Example', 'source_code': '154004',
                'ags': '05154004', 'election_held': True, 'has_runoff': False}

    def detail(self, rows, valid=100, winner='Person, A (CDU)', single=False):
        return ('Endgültiges Ergebnis für Example\n'
                'Bei der Wahl am 13.09.2020 gewählt:\n' + winner + '\n' +
                ('13.09.2020:80,0 % der Wähler\n' if single else '') +
                'Zum Vergleich:\nBisher im Amt:\nFormer, Person (SPD)\n'
                '13.09.2015: 70,0 % der gültigen Stimmen\n'
                f'Gültige Stimmen;{valid};100,0;\ndavon entfielen auf:\n' + rows)

    def test_single_candidate_residual_is_not_an_invented_opponent(self):
        event = parse_detail(self.detail('Person, A (CDU);80;80,0;\n', single=True), self.entry())
        self.assertEqual(event['candidate_count'], 1)
        self.assertEqual(event['first_valid_votes_not_allocated_to_candidates'], 20)
        self.assertFalse(event['decisive_pair'])
        self.assertIsNone(event['absolute_margin_pp'])

    def test_prior_incumbent_is_not_a_candidate_or_term_start(self):
        event = parse_detail(self.detail('Person, A (CDU);60;60,0;\nPerson, B (SPD);40;40,0;\n'), self.entry())
        self.assertEqual(event['candidate_count'], 2)
        self.assertEqual(event['first_date'], '2020-09-13')
        self.assertFalse(event['actual_terms_verified'])

    def test_competitive_residual_and_missing_majority_are_rejected(self):
        for rows in ('Person, A (CDU);60;60,0;\nPerson, B (SPD);39;39,0;\n',
                     'Person, A (CDU);45;45,0;\nPerson, B (SPD);40;40,0;\nPerson, C (FDP);15;15,0;\n'):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                parse_detail(self.detail(rows), self.entry())

    def test_whitespace_is_normalized_but_name_particles_and_swaps_are_not(self):
        self.assertEqual(name_key('Person , A  '), name_key('Person, A'))
        self.assertNotEqual(name_key('von Helden, Johannes'), name_key('Helden, Johannes'))
        self.assertNotEqual(name_key('Thomas, Dr. Roland'), name_key('Roland, Dr. Thomas'))

    def test_unrelated_name_discrepancy_does_not_merge_names_or_drop_matched_finalists(self):
        event = {'has_runoff': True, 'decisive_pair': True, 'winner_name_source': 'Person, A',
                 'candidates': [{'candidate_name_source': 'Person, A', 'votes_first': 40, 'votes_runoff': 60},
                                {'candidate_name_source': 'Person, B', 'votes_first': 35, 'votes_runoff': 40},
                                {'candidate_name_source': 'von Person, C', 'votes_first': 25, 'votes_runoff': None}]}
        rows = [{'candidate_name': 'Person, ' + name, 'candidate_votes_hw': first,
                 'candidate_votes_sw': second, 'is_winner': winner,
                 'election_date': '2020-09-13', 'election_date_sw': '2020-09-27',
                 'candidate_gender_source': 'predicted'}
                for name, first, second, winner in [('A','40','60','TRUE'),('B','35','40','FALSE'),('C','25','','FALSE')]]
        self.assertFalse(compare_gerda(event, rows)[0])
        self.assertTrue(compare_decisive_pair(event, rows))
        wrong = copy.deepcopy(rows)
        wrong[0]['candidate_votes_sw'] = '61'
        self.assertFalse(compare_decisive_pair(event, wrong))


if __name__ == '__main__':
    unittest.main()
