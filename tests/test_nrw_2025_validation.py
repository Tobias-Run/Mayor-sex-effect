"""Protect primary-evidence checks and original-call timing in the new cohort."""
import copy
import hashlib
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from nrw_2025_validation import candidate_window, presentation_pairs, sole_same_buyer, original_records, procedure_audit

class ValidationTests(unittest.TestCase):
    def test_publication_in_q1_cannot_move_a_december_issue_into_q1(self):
        self.assertFalse(candidate_window('2026-01-05','2025-12-30+01:00'))
        self.assertTrue(candidate_window('2026-01-05','2026-01-02+01:00'))
        self.assertFalse(candidate_window('2026-01-05','2026-01-06'))
        self.assertFalse(candidate_window('2026-02-30','2026-02-27'))
        self.assertFalse(candidate_window('2026-01-05',''))

    def test_sole_original_buyer_is_required(self):
        one={'xml':{'buyers':[{'name':'Stadt Example','organization_id':'ORG-1'}]}}
        self.assertTrue(sole_same_buyer(one,' Stadt  Example '))
        two=copy.deepcopy(one);two['xml']['buyers'].append({'name':'County Example'})
        self.assertFalse(sole_same_buyer(two,'Stadt Example'))
        self.assertFalse(sole_same_buyer(one,'Gemeinde Example'))

    def setup_evidence(self,root):
        raw=b'<html><body><p>Frau A at the 2025 election. Herr B at the 2025 election.</p></body></html>'
        (root/'source.html').write_bytes(raw)
        source={'s':{'file':'source.html','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}}
        annotations=[{'ags':'05','official_finalist_role':role,'public_presentation':value,'source_id':'s','locator_quote':quote,'tier':'B','context':'contemporaneous_2025_election','disposition':'accepted_first_coder'} for role,value,quote in [('winner','female','Frau A'),('loser','male','Herr B')]]
        events=[{'ags':'05','municipality_source':'Example, Stadt','first_date':'2025-09-14','decisive_date':'2025-09-28','decisive_pair':True,'absolute_margin_pp':1.25}]
        return events,annotations,source

    def test_supported_public_presentation_does_not_certify_administrative_gender_or_study(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);events,a,s=self.setup_evidence(root)
            pair=presentation_pairs(events,a,s,root)[0]
            self.assertEqual(pair['pair_status'],'mixed_public_presentation')
            self.assertEqual(pair['signed_presentation_margin_pp'],1.25)
            for field in ('administrative_gender_verified','independent_second_coding','main_study_eligibility_certified'):
                self.assertFalse(pair[field])

    def test_locators_must_be_in_pinned_original_not_a_derived_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);events,a,s=self.setup_evidence(root)
            (root/'s.txt').write_text('Invented personal pronoun')
            a[0]['locator_quote']='Invented personal pronoun'
            with self.assertRaises(ValueError):presentation_pairs(events,a,s,root)

    def test_current_only_or_predicted_evidence_cannot_assign_presentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);events,a,s=self.setup_evidence(root)
            for field,value in [('tier','E'),('context','current_2026_role')]:
                bad=copy.deepcopy(a);bad[0][field]=value
                with self.assertRaises(ValueError):presentation_pairs(events,bad,s,root)

    def test_changed_source_and_repeated_finalist_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);events,a,s=self.setup_evidence(root)
            with self.assertRaises(ValueError):presentation_pairs(events,a+[a[0]],s,root)
            (root/'source.html').write_bytes(b'<html>changed</html>')
            with self.assertRaises(ValueError):presentation_pairs(events,a,s,root)

    def test_originals_require_exact_notice_identity_and_procedure(self):
        notice='11111111-1111-4111-8111-111111111111'
        wrong='22222222-2222-4222-8222-222222222222'
        guid='33333333-3333-4333-8333-333333333333'
        index=[{'notice-identifier':notice,'notice-version':1,'notice-type':'cn-standard','procedure-identifier':guid,'publication-number':'1-2026'}]
        def xml(identifier,procedure):
            return ('<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">'
                    '<cbc:ID>'+identifier+'</cbc:ID><cbc:VersionID>01</cbc:VersionID><cbc:ContractFolderID>'+procedure+'</cbc:ContractFolderID><cbc:NoticeTypeCode>cn-standard</cbc:NoticeTypeCode></ContractNotice>').encode()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def snapshot(identifier,procedure):
                with zipfile.ZipFile(root/'day.zip','w') as archive:
                    archive.writestr(notice+'-01.xml',xml(identifier,procedure))
                raw=(root/'day.zip').read_bytes()
                return [{'file':'day.zip','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'period':'2026-01-05'}]
            pins=snapshot(notice,guid)
            matched,missing=original_records(index,pins,root)
            self.assertEqual((len(matched),missing),(1,[]))
            for identifier,procedure in ((wrong,guid),(notice,wrong)):
                pins=snapshot(identifier,procedure)
                with self.assertRaises(ValueError):original_records(index,pins,root)

    def test_absent_competition_is_not_inferred_to_be_a_direct_award(self):
        result={'publication-number':'1-2026','procedure-identifier':'g','ags':'05','publication-date':'2026-02-02','buyer-name':{'deu':['Stadt Example']}}
        original={'index':result,'xml':{'buyers':[{'name':'Stadt Example'}],'units':[]}}
        row=procedure_audit([result],[],[original])[0]
        self.assertEqual(row['original_competition_graph_status'],'no_indexed_competition_found')
        self.assertIsNone(row['root_competition_publication_date'])
        self.assertFalse(row['issue_and_publication_in_candidate_q1_window'])
        self.assertFalse(row['main_study_eligibility_certified'])

if __name__=='__main__':unittest.main()
