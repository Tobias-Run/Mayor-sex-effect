"""Audit exact Brandenburg originals and preserve unresolved election linkage."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from cohort_expansion import ROOT, OUT, DOC, frame, official_sources
from federal_procurement import (identity, safe_xml, source_date, text_at,
                                 verified_archive)
from nrw_2025_validation import csv_write, original_records, original_visible_text
from nrw_phase_linkage import competition_graph
from nrw_2025_q1_eligibility import lot_audit, municipal_scope
import bavaria_bounded_route as ted


def main():
    _, events, _ = frame()
    official_statuses, _ = official_sources(events, download=False)
    official_verified = sum(row['official_pair_verified'] for row in official_statuses.values())
    if official_verified != len(events):
        raise ValueError('Official pair verification incomplete')
    with (DOC / 'nrw-2025-q1-linked-election-inventory.csv').open(newline='') as f:
        nrw_elections = list(csv.DictReader(f))
    if {e['ags'] for e in events} & {e['ags'] for e in nrw_elections}:
        raise ValueError('Expansion repeats an existing municipality')
    nrw_count_elections = sum(e['known_mixed_with_count_inventory'] == 'True' for e in nrw_elections)
    context = json.loads((OUT / 'procedure-context.json').read_text())
    existing = Path('data/raw/nrw-2025-validation/federal-eforms')
    extra = ROOT / 'national-xml'
    cached_pins = [p for name in ('retrieval.json', 'alignment-retrieval.json', 'q1-completion-retrieval.json')
                   for p in json.loads((existing / name).read_text())['exports']]
    extra_manifest = json.loads((extra / 'retrieval.json').read_text())
    extra_pins = extra_manifest['exports']
    csv_pins = json.loads((ROOT / 'national-csv/retrieval.json').read_text())['exports']
    additional_bytes = sum(p['bytes'] for p in extra_pins + csv_pins)
    combined_bytes = additional_bytes + sum(p['bytes'] for p in cached_pins)
    if len(extra_pins) > 64 or additional_bytes > 256 * 1024 ** 2 or combined_bytes > 1024 ** 3:
        raise ValueError('Expansion source budget exceeded')
    originals = {}
    for root, pins in ((existing, cached_pins), (extra, extra_pins)):
        found, _ = original_records(context, pins, root)
        for record in found:
            number = record['index']['publication-number']
            if number in originals:
                if originals[number]['xml_sha256'] != record['xml_sha256']:
                    raise ValueError('Conflicting exact originals')
                continue
            originals[number] = dict(record, export_root=str(root))
    roots, source_rows = {}, []
    for number, record in originals.items():
        root = Path(record['export_root'])
        pins = cached_pins if root == existing else extra_pins
        pin = next(p for p in pins if p['file'] == record['export_file'])
        with verified_archive(root, pin) as archive:
            raw = archive.read(record['xml_file'])
        if len(raw) != record['xml_bytes'] or hashlib.sha256(raw).hexdigest() != record['xml_sha256']:
            raise ValueError('Original XML changed')
        xml = safe_xml(raw); idx = record['index']
        if identity(text_at(xml, 'cbc:ID'), text_at(xml, 'cbc:VersionID')) != identity(idx['notice-identifier'], idx['notice-version']) or text_at(xml, 'cbc:ContractFolderID') != idx['procedure-identifier']:
            raise ValueError('Original identity changed')
        roots[number] = xml
        source_rows.append({'publication_number': number, 'procedure_identifier': idx['procedure-identifier'],
                            'xml_file': record['xml_file'], 'xml_sha256': record['xml_sha256'],
                            'xml_bytes': len(raw), 'export_url': pin['url'],
                            'export_file': pin['file'], 'export_sha256': pin['sha256']})
    by_guid = defaultdict(list)
    for n in context: by_guid[n['procedure-identifier']].append(n)
    calls = json.loads((OUT / 'matched-calls.json').read_text())
    procedures, units = [], []
    for guid, notices in by_guid.items():
        call_rows = [n for n in calls if n['procedure-identifier'] == guid]
        if len({n['ags'] for n in call_rows}) != 1 or len({n['election_year'] for n in call_rows}) != 1:
            raise ValueError('Ambiguous election/procedure assignment')
        ags, year = call_rows[0]['ags'], call_rows[0]['election_year']
        event = next(e for e in events if e['ags'] == ags)
        aliases = ted.aliases([event]); expected = set(aliases)
        if ags == '12065332': expected.add(ted.normal_text('Stadt Velten - Die Bürgermeisterin'))
        missing = [n['publication-number'] for n in notices if n['publication-number'] not in originals]
        nodes = [dict(originals[n['publication-number']]['xml'], ags=ags,
                      publication_number=n['publication-number'], competition_publication_date=source_date(n['publication-date']))
                 for n in notices if n['notice-type'] == 'cn-standard' and n['publication-number'] in originals]
        graph = competition_graph(nodes) if nodes and not missing else {'graph_status': 'original_graph_pending'}
        root_number = graph.get('candidate_competition_publication_number')
        root_record = originals.get(root_number)
        issue = source_date(root_record['xml']['notice_issue_date_source']) if root_record else None
        pub = graph.get('candidate_competition_date')
        start, end, cutoff = str(year + 1) + '-01-01', str(year + 1) + '-03-31', str(year + 1) + '-09-30'
        q1 = bool(issue and pub and start <= issue <= pub <= end)
        scope = not missing and all(municipal_scope(roots[n['publication-number']], expected)['scope_status'] == 'sole_named_municipal_contracting_party_supported' for n in notices)
        codes = {text_at(roots[n['publication-number']], 'cac:TenderingProcess/cbc:ProcedureCode') for n in notices if n['publication-number'] in roots}
        category = next(iter(codes)) if len(codes) == 1 and codes <= {'open', 'restricted', 'neg-w-call'} else 'category_unresolved'
        own_units = []
        for n in notices:
            number = n['publication-number']
            if n['notice-type'] != 'can-standard' or number not in roots: continue
            result_pub = source_date(n['publication-date'])
            result_issue = source_date(originals[number]['xml']['notice_issue_date_source'])
            observed = bool(issue and result_issue and result_pub and issue <= result_issue <= result_pub <= cutoff)
            for u in lot_audit(roots[number]):
                eligible = q1 and scope and category != 'category_unresolved' and observed and u['award_graph_supported'] and u['total_count_supported'] and bool(u['contract_conclusion_date'] and issue <= u['contract_conclusion_date'] <= result_pub)
                own_units.append({'ags': ags, 'election_year': year, 'procedure_identifier': guid,
                                  'publication_number': number, **u,
                                  'dated_supported_count_population': eligible,
                                  'main_study_eligibility_certified': False})
        owners = Counter(lot for u in own_units for lot in u['lot_ids'].split(';'))
        for u in own_units:
            if any(owners[lot] > 1 for lot in u['lot_ids'].split(';')):
                u['dated_supported_count_population'] = False
                u['audit_reasons'] += ';overlapping_result_notices_require_correction_review'
        units.extend(own_units)
        procedures.append({'ags': ags, 'election_year': year, 'procedure_identifier': guid,
                           'original_graph_status': graph['graph_status'], 'root_publication_number': root_number,
                           'root_issue_date': issue, 'root_publication_date': pub,
                           'original_issue_and_publication_in_q1': q1,
                           'municipal_contracting_party_supported': scope,
                           'called_category': category, 'original_xml_notices': len(notices) - len(missing),
                           'missing_original_publication_numbers': ';'.join(missing),
                           'indexed_result_notices_by_cutoff': sum(n['notice-type'] == 'can-standard' for n in notices),
                           'dated_supported_tender_statistics': sum(u['dated_supported_count_population'] for u in own_units),
                           'distinct_contracts_in_supported_lots': len({c for u in own_units if u['dated_supported_count_population'] for c in u['contract_ids'].split(';') if c}),
                           'main_study_eligibility_certified': False})
    presentation_root = ROOT / 'presentation'
    pins = json.loads((presentation_root / 'retrieval.json').read_text())
    annotations = json.loads((presentation_root / 'first-coder-annotations.json').read_text())
    search_deviations = json.loads((presentation_root / 'search-budget-deviations.json').read_text())
    grouped = defaultdict(dict)
    for row in annotations:
        pin = pins[row['source_id']]; raw = (presentation_root / pin['file']).read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256'] or ' '.join(row['locator_quote'].split()) not in ' '.join(original_visible_text(raw, pin['file']).split()):
            raise ValueError('Presentation original or locator changed')
        if row['role'] in grouped[row['ags']]: raise ValueError('Duplicate finalist annotation')
        grouped[row['ags']][row['role']] = row
    with (DOC / 'brandenburg-expansion-national-election-coverage.csv').open(newline='') as f:
        national = {r['ags']: r for r in csv.DictReader(f)}
    elections = []
    for e in events:
        coded = grouped[e['ags']]
        complete = set(coded) == {'winner', 'loser'}
        mixed = complete and {r['presentation'] for r in coded.values()} == {'male', 'female'}
        own_p = [p for p in procedures if p['ags'] == e['ags']]
        own_u = [u for u in units if u['ags'] == e['ags'] and u['dated_supported_count_population']]
        elections.append({'ags': e['ags'], 'municipality': e['municipality'], 'election_year': e['decisive_date'][:4],
                          'decisive_date': e['decisive_date'], 'absolute_margin_pp': e['absolute_margin_pp'],
                          'pair_status': 'mixed_public_presentation' if mixed else 'same_public_presentation' if complete else 'one_finalist_unresolved' if coded else 'not_reviewed_in_this_bounded_batch',
                          'female_presented_winner': coded['winner']['presentation'] == 'female' if mixed else None,
                          'accepted_first_coder_finalists': len(coded),
                          'presentation_source_ids': ';'.join(sorted({r['source_id'] for r in coded.values()})),
                          'provisional_national_call_notices': national[e['ags']]['provisional_national_call_notices'],
                          'original_q1_called_procedures': sum(p['original_issue_and_publication_in_q1'] and p['municipal_contracting_party_supported'] and p['called_category'] != 'category_unresolved' for p in own_p),
                          'dated_supported_tender_statistics': len(own_u),
                          'known_mixed_with_supported_count_inventory': mixed and bool(own_u),
                          'independent_second_coding': False, 'main_study_eligibility_certified': False})
    csv_write(DOC / 'brandenburg-expansion-original-procedure-audit.csv', procedures)
    csv_write(DOC / 'brandenburg-expansion-result-audit.csv', units)
    csv_write(DOC / 'brandenburg-expansion-xml-source-manifest.csv', source_rows)
    csv_write(DOC / 'brandenburg-expansion-presentation-source-manifest.csv', [{'source_id': key, **pin} for key, pin in pins.items()])
    csv_write(DOC / 'brandenburg-expansion-linked-election-inventory.csv', elections)
    combined = [
        {'cohort': 'NRW 2025', 'ags': e['ags'], 'municipality': e['municipality'],
         'pair_status': e['pair_status'], 'female_presented_winner': e['female_presented_winner'],
         'original_q1_called_procedures': e['original_q1_procedures'],
         'candidate_tender_statistics': e['candidate_tender_count_lot_results'],
         'known_mixed_with_supported_count_inventory': e['known_mixed_with_count_inventory'],
         'independent_second_coding': False, 'main_study_eligibility_certified': False}
        for e in nrw_elections]
    combined += [
        {'cohort': 'Brandenburg ' + e['election_year'], 'ags': e['ags'], 'municipality': e['municipality'],
         'pair_status': e['pair_status'], 'female_presented_winner': e['female_presented_winner'],
         'original_q1_called_procedures': e['original_q1_called_procedures'],
         'candidate_tender_statistics': e['dated_supported_tender_statistics'],
         'known_mixed_with_supported_count_inventory': e['known_mixed_with_supported_count_inventory'],
         'independent_second_coding': False, 'main_study_eligibility_certified': False}
        for e in elections]
    csv_write(DOC / 'expanded-election-acquisition-frame.csv', combined)
    (OUT / 'original-records.json').write_text(json.dumps(list(originals.values()), indent=2, ensure_ascii=False) + '\n')
    summary = {'checked_on': '2026-10-11', 'expansion_elections': len(elections),
               'new_official_pairs_verified': official_verified, 'exact_original_notices': len(originals),
               'unmatched_indexed_originals': [n['publication-number'] for n in context if n['publication-number'] not in originals],
               'original_q1_called_procedures': sum(p['original_issue_and_publication_in_q1'] and p['municipal_contracting_party_supported'] and p['called_category'] != 'category_unresolved' for p in procedures),
               'dated_supported_tender_statistics': sum(u['dated_supported_count_population'] for u in units),
               'new_confirmed_first_coder_mixed_pairs': sum(e['pair_status'] == 'mixed_public_presentation' for e in elections),
               'new_mixed_pairs_with_supported_count_inventory': sum(e['known_mixed_with_supported_count_inventory'] for e in elections),
               'new_accepted_first_coder_finalists': len(annotations),
               'search_budget_deviations': [{k: v for k, v in row.items() if k != 'queries'}
                                            for row in search_deviations],
               'new_candidate_role_observation_velten': {'source_id': 'velten-entry', 'first_workday_observed': '2026-01-12', 'legal_acceptance_or_continuous_tenure_certified': False},
               'nrw_plus_brandenburg_acquisition_frame_elections': len(combined),
               'nrw_supported_first_coder_mixed_count_elections_preserved': nrw_count_elections,
               'certified_main_study_elections': 0, 'pooled_effects_estimated': False,
               'all_category_negotiated_denominator_supported': False,
               'additional_compressed_export_bytes': additional_bytes, 'combined_compressed_export_bytes': combined_bytes,
               'additional_daily_xml_exports': len(extra_pins),
               'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [DOC / 'nrw-2025-q1-linked-election-inventory.csv',
                                          presentation_root / 'first-coder-annotations.json',
                                          presentation_root / 'retrieval.json',
                                          presentation_root / 'search-budget-deviations.json',
                                          ROOT / 'official-source-retrieval.json',
                                          OUT / 'procedure-context.json',
                                          extra / 'retrieval.json',
                                          ROOT / 'national-csv/retrieval.json']}}
    (DOC / 'brandenburg-expansion-audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
