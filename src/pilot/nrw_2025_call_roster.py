"""Audit a Q1 competitive-call roster independently of result availability.

All 30 official pairs within 5 pp enter the query, regardless of presentation.
Correction roots, exact original identities and missing results remain explicit.
This roster does not cover no-call awards or a complete primary outcome denominator.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
import bavaria_bounded_route as ted
from nrw_2025_procurement_screen import select
from nrw_2025_validation import (RAW, DOC, OUT, candidate_window, csv_write,
                                original_records, sole_same_buyer)
from nrw_phase_linkage import competition_graph
from federal_procurement import source_date


def retained_snapshot(root):
    pin=json.loads((root/'retrieval.json').read_text())
    ted.RAW=root;ted.FIELDS=pin['fields']
    notices,_=ted.snapshot(pin['query'])
    return notices,pin


def main():
    events=select(json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text()))
    calls,call_pin=retained_snapshot(RAW/'q1-call-roster')
    mapping=ted.aliases(events)
    matched=[dict(n,ags=ted.match_buyer(n,mapping)[0]) for n in calls if ted.match_buyer(n,mapping)[0]]
    context,context_pin=retained_snapshot(RAW/'q1-followup-context')
    guids={n['procedure-identifier'] for n in matched}
    if any(n['procedure-identifier'] not in guids for n in context):
        raise ValueError('Context contains an unqueried procedure')
    export_root=RAW/'federal-eforms'
    exports=[]
    for filename in ('retrieval.json','alignment-retrieval.json'):
        exports+=json.loads((export_root/filename).read_text())['exports']
    originals,missing=original_records(context,exports,export_root)
    by_number={n['index']['publication-number']:n for n in originals}
    grouped=defaultdict(list)
    by_guid=defaultdict(list)
    for n in matched:grouped[n['procedure-identifier']].append(n)
    for n in context:by_guid[n['procedure-identifier']].append(n)
    procedures=[]
    for guid,roster in sorted(grouped.items()):
        if len({n['ags'] for n in roster})!=1:
            raise ValueError('Procedure crosses municipality identity')
        ags=roster[0]['ags']
        names={name for n in roster for name in n['buyer-name']['deu']}
        if len(names)!=1:
            raise ValueError('Ambiguous buyer across roster corrections')
        name=next(iter(names))
        cn=[n for n in by_guid[guid] if n['notice-type']=='cn-standard']
        results=[n for n in by_guid[guid] if n['notice-type']=='can-standard']
        nodes=[]
        complete=True
        for n in cn:
            original=by_number.get(n['publication-number'])
            if not original or not sole_same_buyer(original,name):
                complete=False
                continue
            nodes.append({**original['xml'],'ags':ags,'publication_number':n['publication-number'],
                          'competition_publication_date':source_date(n['publication-date'])})
        graph=competition_graph(nodes) if complete and nodes else {'graph_status':'original_graph_pending'}
        root_number=graph.get('candidate_competition_publication_number')
        root=by_number.get(root_number)
        day=graph.get('candidate_competition_date')
        issue=source_date(root['xml']['notice_issue_date_source']) if root else None
        procedures.append({'ags':ags,'procedure_identifier':guid,'q1_roster_notices':len(roster),
                           'all_indexed_competition_notices':len(cn),'original_graph_status':graph['graph_status'],
                           'root_call_publication_number':root_number,'root_call_publication_date':day,
                           'root_call_issue_date':issue,'original_issue_and_publication_in_q1':candidate_window(day,issue),
                           'indexed_standard_result_notices_by_2026_09_30':len(results),
                           'result_followup_status':'indexed_result_present' if results else 'no_indexed_standard_result_by_cutoff',
                           'original_result_xml_matches':sum(n['publication-number'] in by_number for n in results),
                           'certified_outcome_denominator':False,'main_study_eligibility_certified':False})
    municipality=[]
    for event in events:
        rs=[r for r in procedures if r['ags']==event['ags']]
        municipality.append({'ags':event['ags'],'municipality':event['municipality'],'all_q1_call_notice_matches':sum(r['q1_roster_notices'] for r in rs),
                             'provisional_q1_roster_procedures':len(rs),
                             'verified_original_q1_procedures':sum(r['original_issue_and_publication_in_q1'] for r in rs),
                             'procedures_with_no_indexed_standard_result_by_cutoff':sum(r['result_followup_status']=='no_indexed_standard_result_by_cutoff' for r in rs),
                             'certified_outcome_denominator':False})
    csv_write(DOC/'nrw-2025-q1-call-procedures.csv',procedures)
    csv_write(DOC/'nrw-2025-q1-call-municipalities.csv',municipality)
    (DOC/'nrw-2025-q1-call-request-manifests.json').write_text(json.dumps({'calls':call_pin,'followup':context_pin},indent=2)+'\n')
    (OUT/'q1-original-records.json').write_text(json.dumps(originals,indent=2,ensure_ascii=False)+'\n')
    summary={'checked_on':'2026-10-10','selection':'All 30 official NRW 2025 decisive pairs within 5 pp, irrespective of predictions or earlier results',
             'call_publication_window':['2026-01-01','2026-03-31'],'result_followup_cutoff':'2026-09-30',
             'indexed_call_notices':len(calls),'provisional_exact_municipal_calls':len(matched),
             'provisional_roster_procedures':len(procedures),'municipalities_with_call_matches':len({n['ags'] for n in matched}),
             'followup_notices':len(context),'followup_types':dict(Counter(n['notice-type'] for n in context)),
             'roster_procedures_without_indexed_standard_result':sum(not any(n['notice-type']=='can-standard' for n in by_guid[g]) for g in guids),
             'exact_original_xml_matches_in_retained_exports':len(originals),'original_publications_still_missing':missing,
             'original_graph_status_counts':dict(Counter(r['original_graph_status'] for r in procedures)),
             'verified_original_issue_and_publication_q1_procedures':sum(r['original_issue_and_publication_in_q1'] for r in procedures),
             'certified_outcome_denominators':0,'warning':'Quarter publication can be a correction of an earlier call. Missing indexed results are unresolved/censored, not cancelled or zero-tender awards. This competitive-call roster excludes no-call procurement and is not a complete procedure-choice population.'}
    (DOC/'nrw-2025-q1-call-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
