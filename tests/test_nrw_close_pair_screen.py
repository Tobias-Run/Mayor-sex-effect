"""Exercise measurement failures that would change the research sample."""
import copy
import hashlib
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src' / 'pilot'))
from nrw_close_pair_screen import (audit_reviews, decisive, reviewed_pair,
                                   select_pairs, validate_evidence, verified_bytes)


class ClosePairAuditTests(unittest.TestCase):
    def event(self, votes=(51,49), runoff=True):
        people=[dict(candidate_name_source='Synthetic, A',votes_first=90,votes_runoff=votes[0]),
                dict(candidate_name_source='Synthetic, B',votes_first=80,votes_runoff=votes[1])]
        if runoff:
            people.append(dict(candidate_name_source='Synthetic, C',votes_first=30,votes_runoff=None))
        else:
            for p,v in zip(people,votes):p.update(votes_first=v,votes_runoff=None)
        return dict(ags='05000001',detail_source_id='synthetic-votes',municipality_source='Synthetic example',has_runoff=runoff,
            decisive_pair=True,candidates=people,first_valid_votes=200 if runoff else sum(votes),
            runoff_valid_votes=sum(votes) if runoff else None,decisive_date='2020-09-27',
            winner_name_source='Synthetic, A' if votes[0]>votes[1] else 'Synthetic, B')

    def evidence(self,label='female'):
        return dict(label=label,tier='B',primary_authorship=True,cue='named_address',
            person_reference_reviewed=True,original_inspected=True,historical_2020_link_reviewed=True,
            event_context_year=2020,event_context_note='Synthetic 2020 election record',
            document_date='2020-09-27',retrospective=False,identity_status='matched',
            identity_note='',identity_source_ids=[],source_id='synthetic',locator='Frau / Herr')

    def review(self,first=None,second=None):
        return dict(ags='05000001',rank=1,reviewed_source_ids=[],search_batch_ids=['synthetic-query'],
            public_evidence_sections='Synthetic fixture',public_remaining_gap='Synthetic gap',
            candidates=[dict(candidate_name_source='Synthetic, '+name,administrative_sex_gender=None,
                            review_disposition='reviewed',reason='Synthetic fixture',accepted_evidence=evs)
                        for name,evs in [('A',first or []),('B',second or [])]])

    def test_runoff_uses_finalist_votes_and_inclusive_two_pp_boundary(self):
        event=self.event()
        self.assertEqual(decisive(event)[2:],(100,Decimal(2)))
        self.assertEqual(len(select_pairs([event],Decimal(2))),1)
        self.assertEqual(len(select_pairs([event],Decimal('1.999'))),0)

    def test_signed_margin_is_candidate_difference_not_distance_from_half(self):
        review=self.review([self.evidence('female')],[self.evidence('male')])
        row=reviewed_pair(self.event(),review,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})
        self.assertEqual(Decimal(row['signed_female_minus_male_margin_pp']),Decimal(2))
        self.assertEqual(row['female_presented_winner'],'true')
        event=self.event((49,51))
        row=reviewed_pair(event,review,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})
        self.assertEqual(Decimal(row['signed_female_minus_male_margin_pp']),Decimal(-2))
        self.assertEqual(row['female_presented_winner'],'false')

    def test_one_unknown_never_becomes_same_or_mixed_even_with_prediction(self):
        event=self.event();event['prediction_followup']=[{'gender_label':'w'},{'gender_label':'m'}]
        row=reviewed_pair(event,self.review([self.evidence('female')]),{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})
        self.assertEqual(row['pair_status'],'unresolved')
        self.assertEqual(row['signed_female_minus_male_margin_pp'],'')
        self.assertEqual(row['female_presented_winner'],'')

    def test_generic_masculine_and_wrong_person_pronouns_are_rejected(self):
        for changed in ({'cue':'generic_masculine_office'},{'person_reference_reviewed':False}):
            evidence=self.evidence('male');evidence.update(changed)
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})

    def test_current_and_unrelated_dates_cannot_be_interpolated(self):
        for changed in ({'historical_2020_link_reviewed':False},{'event_context_year':2024},
                        {'document_date':'2025-11-01','retrospective':False}):
            evidence=self.evidence();evidence.update(changed)
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})

    def test_later_explicit_2020_retrospective_is_distinct_from_current_contact(self):
        evidence=self.evidence();evidence.update(document_date='2025-11-01',retrospective=True)
        self.assertEqual(validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'}),'female')

    def test_primary_host_does_not_make_a_newspaper_reprint_primary(self):
        evidence=self.evidence();evidence['primary_authorship']=False
        with self.assertRaises(ValueError):validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})

    def test_identity_exceptions_require_manual_corroboration(self):
        for status in ('pending','manually_corroborated'):
            evidence=self.evidence();evidence['identity_status']=status
            with self.subTest(status=status),self.assertRaises(ValueError):
                validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})

    def test_conflicting_presentations_stay_out_of_binary_margin(self):
        row=reviewed_pair(self.event(),self.review([self.evidence('female'),self.evidence('male')],
                         [self.evidence('male')]),{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})
        self.assertEqual(row['pair_status'],'conflicting_or_other')
        self.assertEqual(row['signed_female_minus_male_margin_pp'],'')

    def test_changed_original_or_inaccessible_source_cannot_supply_assignment(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory,'source.txt');raw=b'Synthetic original';path.write_bytes(raw)
            source=dict(status='acquired',local_file=str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            self.assertEqual(verified_bytes(source),raw)
            path.write_bytes(b'Synthetic mutation')
            with self.assertRaises(ValueError):verified_bytes(source)
            source['status']='unavailable'
            with self.assertRaises(ValueError):verified_bytes(source)

    def test_declared_legacy_encoding_preserves_the_named_identity_locator(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory,'source.html')
            raw='<p>Herr Synthétique, nomination for the 2020 election.</p>'.encode('iso-8859-1')
            path.write_bytes(raw)
            source=dict(source_id='synthetic',status='acquired',local_file=str(path),
                        bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),text_encoding='iso-8859-1')
            evidence=self.evidence('male');evidence['locator']='Herr Synthétique'
            self.assertEqual(validate_evidence(evidence,{'synthetic':source},{}),'male')
            source['text_encoding']='utf-8'
            with self.assertRaises(ValueError):validate_evidence(evidence,{'synthetic':source},{})

    def test_missing_duplicate_and_swapped_finalist_dispositions_fail(self):
        event=self.event();review=self.review()
        for rows in ([],[review,copy.deepcopy(review)]):
            with self.assertRaises(ValueError):audit_reviews([event],rows,{})
        review['candidates'].reverse()
        with self.assertRaises(ValueError):audit_reviews([event],[review],{})

    def test_first_round_and_invalid_denominators_are_checked(self):
        self.assertEqual(decisive(self.event((54,46),False))[3],Decimal(8))
        event=self.event();event['runoff_valid_votes']=101
        with self.assertRaises(ValueError):decisive(event)
        event=self.event();event['winner_name_source']='Synthetic, B'
        with self.assertRaises(ValueError):decisive(event)

    def test_ocr_without_visual_review_is_rejected(self):
        evidence=self.evidence();evidence.update(ocr_text_file='synthetic.txt',visual_page_verified=False)
        with self.assertRaises(ValueError):validate_evidence(evidence,{'synthetic':{'source_id':'synthetic'}}, {'synthetic':'Frau / Herr'})


if __name__=='__main__':unittest.main()
