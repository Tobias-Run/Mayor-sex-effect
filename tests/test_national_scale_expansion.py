"""Guard a broader window, source reconciliation and exact buyer aliases."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'pilot'))
from test_cohort_expansion import pair
from national_scale_expansion import screen, validate_page, niedersachsen_aliases
from cohort_expansion_national import municipal_match


def official_page():
    return '''Vorläufiges Ergebnis der Direktwahl 2021 in Niedersachsen
Bürgermeister/Bürgermeisterin
Schlüssel: 241004
Nach dem vorläufigen Ergebnis der Direktwahl kann als gewählt gelten:
One Person, Example
D   Gültige Stimmen   100
     1       Person, One        Example
                                51    51.0
     2       Person, Two
                      Wrapped occupation continuation
                                49    49.0
'''


def event():
    return {'ags': '03241004', 'valid_votes': 100,
            'candidates': [{'name': 'Person, One', 'votes': 51, 'winner': True},
                           {'name': 'Person, Two', 'votes': 49, 'winner': False}]}


class NationalExpansionTests(unittest.TestCase):
    def test_older_elections_retained_without_names_or_labels(self):
        rows = pair()
        for r in rows:
            r['election_date'] = '2018-09-01'
            r['election_date_sw'] = '2018-09-15'
            r['candidate_gender'] = ''
            r['candidate_name'] = ''
        record, reason = screen(rows)
        self.assertIsNone(reason)
        self.assertFalse(record['both_names_available'])
        for r in rows:
            r['election_date_sw'] = '2026-09-15'
        self.assertEqual(screen(rows)[1], 'outside_2018_2025')

    def test_wrapped_pdf_rows_reconcile_and_reject_vote_changes(self):
        self.assertEqual(validate_page(event(), [official_page()]), 1)
        with self.assertRaisesRegex(ValueError, 'identities or votes'):
            validate_page(event(), [official_page().replace('49    49.0', '48    48.0')])

    def test_wrong_declared_winner_and_duplicate_pages_rejected(self):
        with self.assertRaisesRegex(ValueError, 'declared winner'):
            validate_page(event(), [official_page().replace('One Person', 'Two Person')])
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            validate_page(event(), [official_page(), official_page()])

    def test_suffix_normalization_keeps_strict_buyer_checks(self):
        mapping = niedersachsen_aliases([{'ags': '03241004', 'municipality': 'Burgwedel, Stadt'}])
        buyer = {'organisationName': 'Stadt Burgwedel', 'organisationCountryCode': 'DEU', 'buyerLegalType': 'kommun-beh'}
        self.assertEqual(municipal_match([buyer], mapping)[0], '03241004')
        self.assertIsNone(municipal_match([buyer, buyer], mapping)[0])
        buyer['organisationName'] = 'Stadt Burgwedel Service GmbH'
        self.assertIsNone(municipal_match([buyer], mapping)[0])


if __name__ == '__main__': unittest.main()
