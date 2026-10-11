"""Keep domestic notices and publication calendars distinct."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'pilot'))
from cohort_expansion_national import national_day, notice_key, municipal_match


class NationalExpansionTests(unittest.TestCase):
    def test_utc_midnight_is_converted_to_german_publication_day(self):
        self.assertEqual(national_day('2025-01-06T23:00:00Z'), '2025-01-07')
        self.assertEqual(national_day('2026-03-29T22:00:00Z'), '2026-03-30')
        with self.assertRaises(ValueError): national_day('2025-01-07T00:00:00')

    def test_domestic_numeric_identifiers_are_retained_and_versions_normalized(self):
        self.assertEqual(notice_key({'noticeIdentifier': '23280040', 'noticeVersion': '01'}), ('23280040', 1))
        with self.assertRaises(ValueError): notice_key({'noticeIdentifier': '23280040', 'noticeVersion': '0'})

    def test_multiple_buyer_roles_and_corporate_roles_are_not_municipal(self):
        buyer = {'organisationName': 'Stadt Example', 'organisationCountryCode': 'DEU', 'buyerLegalType': 'kommun-beh'}
        aliases = {'stadt example': {'12000001'}}
        self.assertEqual(municipal_match([buyer], aliases)[0], '12000001')
        self.assertIsNone(municipal_match([buyer, buyer], aliases)[0])
        self.assertIsNone(municipal_match([dict(buyer, buyerLegalType='pub-undert')], aliases)[0])
        self.assertIsNone(municipal_match([dict(buyer, organisationName='Stadt Example Housing GmbH')], aliases)[0])


if __name__ == '__main__': unittest.main()
