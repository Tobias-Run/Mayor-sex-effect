"""Protect the new cohort, exact runoff denominator and gender-neutral selection."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
import nrw_2025_reopening as election
from nrw_2025_procurement_screen import select

class ReopeningTests(unittest.TestCase):
    def test_cohort_and_directories_are_separate_from_frozen_2020(self):
        self.assertEqual(election.FIRST_DATE,'2025-09-14')
        self.assertEqual(election.RUNOFF_DATE,'2025-09-28')
        self.assertEqual(str(election.OUT),'outputs/nrw-election-register-2025')
        self.assertEqual(str(election.ROOT),'data/raw/nrw-2025')
        text='Election\nEndgültige Ergebnisse\n\nVerwaltungsbezirks-Nr.;Verwaltungsbezirksname;Datum\n111000;Krfr. Stadt Example;14.09.2025\n154000;Kreis Example;14.09.2025\n'
        events,counties=election.universe([(election.SUMMARIES[1],text)])
        self.assertEqual((len(events),counties),(1,1))
        with self.assertRaises(ValueError):
            election.universe([(election.SUMMARIES[1],text.replace('14.09.2025','13.09.2020'))])

    def test_runoff_margin_uses_runoff_votes_and_declared_winner(self):
        text='Endgültiges Ergebnis für Example\nBei der Stichwahl am 28.09.2025 gewählt:\nPerson, A (CDU)\nGültige Stimmen;200;100,0;100;100,0\ndavon entfielen auf:\nPerson, A (CDU);90;45,0;51;51,0\nPerson, B (SPD);80;40,0;49;49,0\nPerson, C (FDP);30;15,0;;\n'
        entry={'municipality_source':'Example','has_runoff':True,'election_held':True}
        event=election.parse_detail(text,entry)
        self.assertEqual(event['absolute_margin_pp'],2)
        self.assertFalse(event['gender_measurement_verified'])
        with self.assertRaises(ValueError):
            election.parse_detail(text.replace('49;49,0','48;48,0'),entry)

    def test_selection_includes_unknown_and_same_prediction_labels(self):
        events=[{'ags':str(i),'municipality_source':name,'decisive_pair':True,'absolute_margin_pp':margin,'prediction':label}
                for i,name,margin,label in [(1,'Goch, Stadt',5,'same'),(2,'Krfr. Stadt Bielefeld',2,'unknown'),(3,'Other',5.01,'mixed')]]
        result=select(events)
        self.assertEqual([e['ags'] for e in result],['1','2'])
        self.assertEqual([e['municipality'] for e in result],['Goch','Bielefeld'])

if __name__=='__main__':
    unittest.main()
