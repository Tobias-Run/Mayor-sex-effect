"""Verify original publication chronology and prospective result censoring."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'/'pilot'))
from expanded_original_audit import chronological_statistic,context_query

class ExpandedOriginalTests(unittest.TestCase):
    def unit(self,day):
        return {'award_graph_supported':True,'total_count_supported':True,'contract_conclusion_date':day}
    def test_contract_before_original_publication_is_not_supported(self):
        self.assertFalse(chronological_statistic(self.unit('2025-01-02'),'2025-01-01','2025-01-03','2025-02-01','2025-02-02','2025-10-03'))
        self.assertTrue(chronological_statistic(self.unit('2025-01-03'),'2025-01-01','2025-01-03','2025-02-01','2025-02-02','2025-10-03'))
    def test_result_must_fit_target_and_source_cutoff(self):
        args=(self.unit('2025-04-01'),'2025-01-01','2025-01-02','2025-11-01','2025-11-02','2025-10-02')
        self.assertFalse(chronological_statistic(*args))
        self.assertFalse(chronological_statistic(self.unit('2026-09-01'),'2026-01-01','2026-01-02','2026-10-01','2026-10-02','2026-10-02'))
    def test_unsupported_award_or_missing_date_is_not_supported(self):
        u=self.unit('2025-04-01');u['award_graph_supported']=False
        self.assertFalse(chronological_statistic(u,'2025-01-01','2025-01-02','2025-05-01','2025-05-02','2025-10-02'))
        with self.assertRaises(ValueError):context_query(set())
        self.assertEqual(context_query({'b','a'}),context_query({'a','b'}))

if __name__=='__main__':unittest.main()
