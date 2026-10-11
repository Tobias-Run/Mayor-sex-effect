"""Verify retained NRW 2025 presentation evidence and original procurement XML.

Requires ignored first-coder annotations and source snapshots. No gender inference,
causal estimator, rate calculation or certified treatment assignment is performed.
"""
import csv
import hashlib
import json
import subprocess
from html.parser import HTMLParser
from collections import Counter, defaultdict
from pathlib import Path
from federal_procurement import (identity, parse_competition, parse_eforms,
                                 source_date, verified_archive)
from nrw_phase_linkage import competition_graph
import bavaria_bounded_route as ted

RAW = Path('data/raw/nrw-2025-validation')
OUT = Path('outputs/nrw-2025-validation')
DOC = Path('docs/feasibility')
COHORT_START, COHORT_END = '2025-09-14', '2025-09-28'
CANDIDATE_START, CANDIDATE_END = '2026-01-01', '2026-03-31'


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style'):
            self.skip = max(0,self.skip-1)
    def handle_data(self, value):
        if not self.skip:
            self.parts.append(value)


def original_visible_text(raw, filename):
    if filename.endswith('.pdf'):
        if not raw.startswith(b'%PDF'):
            raise ValueError('Expected original PDF bytes')
        return subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode('utf-8')
    parser = VisibleText()
    parser.feed(raw.decode('utf-8',errors='replace'))
    return ' '.join(parser.parts)


def presentation_pairs(events, annotations, sources, root):
    """Validate source pins and exact reviewed locators; never predict presentation."""
    grouped = defaultdict(dict)
    for r in annotations:
        if r['disposition'] != 'accepted_first_coder':
            continue
        if r['official_finalist_role'] not in ('winner', 'loser'):
            raise ValueError('Unknown finalist role')
        if r['public_presentation'] not in ('female', 'male', 'other_explicit', 'conflicting'):
            raise ValueError('Unsupported explicit presentation value')
        if r['tier'] not in ('B', 'C') or not r['context'].startswith(('contemporaneous_2025', 'retrospective_', 'named_2025', 'final_2025')):
            raise ValueError('No suitable primary historical context')
        source = sources[r['source_id']]
        raw = (root / source['file']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source['sha256'] or len(raw) != source['bytes']:
            raise ValueError('Presentation original source changed')
        if ' '.join(r['locator_quote'].split()) not in ' '.join(original_visible_text(raw,source['file']).split()):
            raise ValueError('Reviewed exact presentation locator is missing')
        if r['official_finalist_role'] in grouped[r['ags']]:
            raise ValueError('Repeated finalist disposition')
        grouped[r['ags']][r['official_finalist_role']] = r
    result = []
    for event in events:
        if event['ags'] not in grouped:
            continue
        if event['first_date'] != COHORT_START or event['decisive_date'] not in (COHORT_START, COHORT_END) or not event['decisive_pair']:
            raise ValueError('Presentation annotation is outside the fixed cohort')
        records = grouped[event['ags']]
        complete = set(records) == {'winner','loser'}
        mixed = complete and {r['public_presentation'] for r in records.values()} == {'female','male'}
        same = complete and len({r['public_presentation'] for r in records.values()}) == 1 and records['winner']['public_presentation'] in ('female','male')
        result.append({'ags':event['ags'],'municipality':event['municipality_source'].removeprefix('Krfr. Stadt ').removesuffix(', Stadt'),
                       'absolute_margin_pp':event['absolute_margin_pp'],
                       'pair_status':'mixed_public_presentation' if mixed else 'same_public_presentation' if same else 'conflicting_or_other' if complete else 'unresolved',
                       'female_presented_winner':records['winner']['public_presentation']=='female' if mixed else None,
                       'signed_presentation_margin_pp':event['absolute_margin_pp']*(1 if records['winner']['public_presentation']=='female' else -1) if mixed else None,
                       'source_ids':';'.join(sorted(r['source_id'] for r in records.values())),
                       'first_coder_review_only':True,'independent_second_coding':False,
                       'administrative_gender_verified':False,'main_study_eligibility_certified':False})
    return result


def original_records(index, exports, root):
    """Match exact UUID/version across retained national dates, never by title."""
    targets = {}
    for n in index:
        if n['notice-type'] not in ('cn-standard','can-standard'):
            continue
        key = identity(n['notice-identifier'], n['notice-version'])
        if key in targets:
            raise ValueError('Duplicate indexed UUID/version')
        targets[key] = n
    found = {}
    for pin in exports:
        with verified_archive(root, pin) as archive:
            for filename in archive.namelist():
                if Path(filename).name != filename or not filename.endswith('.xml'):
                    raise ValueError('Unexpected archive member')
                try:
                    key = identity(*Path(filename).stem.rsplit('-',1))
                except (ValueError,TypeError):
                    continue
                if key not in targets:
                    continue
                target = targets[key]
                raw = archive.read(filename)
                parsed = (parse_competition if target['notice-type']=='cn-standard' else parse_eforms)(raw)
                if identity(parsed['notice_identifier'],parsed['notice_version']) != key or parsed['procedure_identifier'] != target['procedure-identifier']:
                    raise ValueError('Original XML identity or procedure differs from index')
                digest = hashlib.sha256(raw).hexdigest()
                if key in found:
                    if found[key]['xml_sha256'] != digest:
                        raise ValueError('Conflicting originals for one UUID/version')
                    continue
                found[key] = {'index':{k:v for k,v in target.items() if k!='links'},'xml':parsed,
                              'xml_file':filename,'xml_sha256':digest,'xml_bytes':len(raw),
                              'export_file':pin['file'],'national_publication_day':pin['period']}
    missing = [n['publication-number'] for k,n in targets.items() if k not in found]
    return list(found.values()), missing


def sole_same_buyer(original, expected_name):
    buyers = original['xml']['buyers']
    return len(buyers)==1 and buyers[0]['name'] is not None and ted.normal_text(buyers[0]['name'])==ted.normal_text(expected_name)


def candidate_window(publication, issue):
    """Both dates must fit the candidate window; a new publication is not a new call."""
    issue = source_date(issue)
    publication = source_date(publication)
    return bool(publication and issue and CANDIDATE_START <= issue <= publication <= CANDIDATE_END)


def procedure_audit(results, context, originals):
    by_number = {r['index']['publication-number']:r for r in originals}
    indexed_calls = defaultdict(list)
    for n in context:
        if n['notice-type']=='cn-standard':
            indexed_calls[n['procedure-identifier']].append(n)
    rows = []
    for notice in results:
        number, guid = notice['publication-number'],notice['procedure-identifier']
        names = set(notice.get('buyer-name',{}).get('deu',[]))
        if len(names)!=1:
            raise ValueError('Fixed result queue must have a unique indexed buyer')
        expected_name = next(iter(names))
        result = by_number.get(number)
        calls = indexed_calls[guid]
        nodes = []
        complete = True
        for call in calls:
            original = by_number.get(call['publication-number'])
            if original is None or not sole_same_buyer(original,expected_name):
                complete = False
                continue
            nodes.append({**original['xml'],'ags':notice['ags'],
                          'publication_number':call['publication-number'],
                          'competition_publication_date':source_date(call['publication-date'])})
        graph = competition_graph(nodes) if complete and nodes else {'graph_status':'original_competition_missing_or_buyer_pending' if calls else 'no_indexed_competition_found'}
        root_number = graph.get('candidate_competition_publication_number')
        root = by_number.get(root_number)
        call_day = graph.get('candidate_competition_date')
        issue_day = source_date(root['xml']['notice_issue_date_source']) if root else None
        buyer_ok = result is not None and sole_same_buyer(result,expected_name)
        units = result['xml']['units'] if result else []
        good = [u for u in units if u['dated_total_supported'] and not u['analytical_contract_unit_review_required']]
        chronology = sum(bool(call_day and call_day<=u['contract_conclusion_date']<=source_date(notice['publication-date'])) for u in good)
        rows.append({'ags':notice['ags'],'result_publication_number':number,'procedure_identifier':guid,
                     'result_publication_date':source_date(notice['publication-date']),
                     'original_result_xml_matched':result is not None,
                     'sole_original_buyer_name_matches':buyer_ok,
                     'indexed_competition_notices':len(calls),'original_competition_graph_status':graph['graph_status'],
                     'root_competition_publication_number':root_number,
                     'root_competition_publication_date':call_day,'root_competition_issue_date':issue_day,
                     'call_published_before_november_2025':call_day<'2025-11-01' if call_day else None,
                     'issue_and_publication_in_candidate_q1_window':candidate_window(call_day,issue_day),
                     'original_result_lot_count':len(units),
                     'dated_single_contract_total_tender_units':len(good),
                     'chronologically_supported_dated_total_units':chronology if buyer_ok else 0,
                     'buyer_jurisdiction_certified':False,'actual_term_certified':False,
                     'main_study_eligibility_certified':False})
    return rows


def csv_write(path, rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    events=json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text())
    sources=json.loads((RAW/'retrieval.json').read_text())
    annotations=json.loads((RAW/'first-coder-presentation.json').read_text())
    pairs=presentation_pairs(events,annotations,sources,RAW)
    results=json.loads((OUT/'matched-notices.json').read_text())
    context_root=RAW/'ted-procedure-context'
    pin=json.loads((context_root/'retrieval.json').read_text())
    ted.RAW=context_root;ted.FIELDS=pin['fields']
    context,_=ted.snapshot(pin['query'])
    export_root=RAW/'federal-eforms'
    initial=json.loads((export_root/'retrieval.json').read_text())
    alignment=json.loads((export_root/'alignment-retrieval.json').read_text())
    exports=initial['exports']+alignment['exports']
    if len({p['file'] for p in exports})!=len(exports) or sum(p['bytes'] for p in exports)>1024**3:
        raise ValueError('Export duplicates or total acquisition cap exceeded')
    originals,missing=original_records(context,exports,export_root)
    rows=procedure_audit(results,context,originals)
    csv_write(DOC/'nrw-2025-presentation-pairs.csv',pairs)
    csv_write(DOC/'nrw-2025-original-procedure-audit.csv',rows)
    csv_write(DOC/'nrw-2025-validation-source-manifest.csv',[dict(source_id=k,**m) for k,m in sources.items()])
    (DOC/'nrw-2025-validation-export-manifest.json').write_text(json.dumps({'initial':initial,'date_alignment':alignment},indent=2)+'\n')
    (DOC/'nrw-2025-procedure-context-request-manifest.json').write_text(json.dumps(pin,indent=2)+'\n')
    (OUT/'xml-records.json').write_text(json.dumps(originals,indent=2,ensure_ascii=False)+'\n')
    mixed=[p for p in pairs if p['pair_status']=='mixed_public_presentation']
    q1=[r for r in rows if r['issue_and_publication_in_candidate_q1_window'] and r['sole_original_buyer_name_matches']]
    summary={'checked_on':'2026-10-10','review_scope':'Six prediction leads with provisional procurement matches; not all close pairs',
             'reviewed_pairs':len(pairs),'first_coder_supported_mixed_pairs':len(mixed),
             'female_presented_wins':sum(p['female_presented_winner'] for p in mixed),
             'female_presented_losses':sum(not p['female_presented_winner'] for p in mixed),
             'presentation_bands':[{'width_pp':h,'mixed_pairs':sum(p['absolute_margin_pp']<=h for p in mixed),'female_wins':sum(p['absolute_margin_pp']<=h and p['female_presented_winner'] for p in mixed)} for h in (1,2,5)],
             'independent_second_coded_pairs':0,'administrative_gender_verified_pairs':0,
             'result_notices':len(results),'procedure_guids':len({r['procedure-identifier'] for r in results}),
             'context_notices':len(context),'context_types':dict(Counter(r['notice-type'] for r in context)),
             'retained_export_days':len(exports),'retained_export_bytes':sum(p['bytes'] for p in exports),
             'original_target_xml_matches':len(originals),'missing_original_publication_numbers':missing,
             'graph_status_counts':dict(Counter(r['original_competition_graph_status'] for r in rows)),
             'original_result_xml_matches':sum(r['original_result_xml_matched'] for r in rows),
             'sole_original_buyer_name_matches':sum(r['sole_original_buyer_name_matches'] for r in rows),
             'calls_published_before_november_2025':sum(r['call_published_before_november_2025'] is True for r in rows),
             'candidate_q1_issue_and_publication_procedures':len(q1),
             'candidate_q1_municipalities':sorted({r['ags'] for r in q1}),
             'candidate_q1_chronological_dated_total_units':sum(r['chronologically_supported_dated_total_units'] for r in q1),
             'certified_main_study_elections':0,'estimated_causal_effects':0,
             'annotation_sha256':hashlib.sha256((RAW/'first-coder-presentation.json').read_bytes()).hexdigest(),
             'warning':'Original XML and explicit presentation evidence do not establish completed independent coding, buyer jurisdiction, continuous officeholding or a complete procurement outcome population. Candidate-window results are availability counts, not outcome rates.'}
    from nrw_early_feasibility import gaussian_t_mde
    available_ags = {r['ags'] for r in q1}
    available = [p for p in mixed if p['ags'] in available_ags]
    wins = sum(p['female_presented_winner'] for p in available)
    losses = len(available)-wins
    summary['candidate_q1_result_first_election_inventory'] = {'pairs':len(available),'female_wins':wins,'female_losses':losses,'certified':False}
    summary['conditional_q1_precision_benchmark'] = {'treated':wins,'control':losses,'mde_sd':gaussian_t_mde(wins,losses) if wins and losses and len(available)>2 else None,'alpha':0.05,'power':0.8,'assumptions':'Independent equal-variance Gaussian pooled t test; hypothetical standardized outcomes, not observed variance or RDD power. The new call-first roster may add unresolved observations.'}
    (DOC/'nrw-2025-validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
