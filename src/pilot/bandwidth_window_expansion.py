"""Execute the authorized 10 pp acquisition band and older-cohort year window.

Run: python src/pilot/bandwidth_window_expansion.py --acquire
Replay without --acquire. Old 5 pp outputs and report inputs are untouched.
"""
import argparse
import calendar
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from national_scale_expansion import load_frame, validate_page, niedersachsen_aliases
from cohort_expansion import official_url, validate_official
from cohort_expansion_national import notice_key, national_day, municipal_match
from nrw_2025_reopening import parse_detail
from nrw_2025_validation import csv_write
from federal_procurement import export_url, verified_archive, csv_rows

RAW = Path('data/raw/bandwidth-window-expansion-2026-10-11')
OUT = Path('outputs/bandwidth-window-expansion-2026-10-11')
DOC = Path('docs/feasibility')
BASE = Path('data/raw/cohort-expansion-2026-10-11')
PRIOR_PROCUREMENT_BYTES = 757474906 + 117362156
NEW_BUDGET = 192 * 1024**2
COMBINED_BUDGET = 1024**3
SOURCE_CUTOFF = date(2026, 9, 30)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def check_pin(pin, path):
    raw = Path(path).read_bytes()
    if digest(raw) != pin['sha256'] or ('bytes' in pin and len(raw) != pin['bytes']):
        raise ValueError('Pinned source changed: ' + str(path))
    return raw


def band(margin):
    if margin < 0:
        raise ValueError('Absolute margin must be nonnegative')
    return 'within_2pp' if margin <= 2 else 'over_2_to_5pp' if margin <= 5 else 'over_5_to_10pp' if margin <= 10 else 'outside_10pp'


def followup_end(call_day):
    when = date.fromisoformat(call_day)
    month = when.year * 12 + when.month - 1 + 9
    year, zero_month = divmod(month, 12)
    return date(year, zero_month + 1, min(when.day, calendar.monthrange(year, zero_month + 1)[1]))


def cohort_window(cohort):
    if cohort in ('Niedersachsen 2021', 'Brandenburg 2024'):
        return '2025-01-01', '2025-12-31', 'complete_calendar_year_separate_cohort'
    if cohort in ('NRW 2025', 'Brandenburg 2025'):
        return '2026-01-01', '2026-03-31', 'Q1_2026_younger_cohort'
    raise ValueError('Unspecified cohort window')


def official_nrw_frame():
    root = Path('data/raw/nrw-2025')
    pins = json.loads((root / 'detail-retrieval.json').read_text())
    previous = json.loads(Path('outputs/nrw-election-register-2025/events.json').read_text())
    events, source_manifest = [], []
    for old in previous:
        pin = pins[old['source_code']]
        raw = check_pin(pin, root / (old['source_code'] + '.txt'))
        parsed = parse_detail(raw.decode('utf-8-sig'), old)
        if parsed['candidates'] != old['candidates'] or parsed['absolute_margin_pp'] != old['absolute_margin_pp']:
            raise ValueError('Official NRW replay differs')
        if not parsed['decisive_pair'] or parsed['absolute_margin_pp'] > 10:
            continue
        field = 'votes_runoff' if parsed['has_runoff'] else 'votes_first'
        candidates = [c for c in parsed['candidates'] if c[field] is not None]
        event = {'state': '05', 'ags': parsed['ags'], 'municipality': re.sub(r'^Krfr\. Stadt ', '', parsed['municipality_source']), 'first_date': parsed['first_date'], 'decisive_date': parsed['decisive_date'], 'round': 'runoff' if parsed['has_runoff'] else 'first', 'valid_votes': sum(c[field] for c in candidates), 'absolute_margin_pp': parsed['absolute_margin_pp'], 'both_names_available': True, 'candidates': [{'name': c['candidate_name_source'], 'votes': c[field], 'winner': c['candidate_name_source'] == parsed['winner_name_source']} for c in candidates], 'cohort': 'NRW 2025', 'official_status': 'official_final_identities_votes_winner_verified'}
        events.append(event)
        source_manifest.append({'ags': event['ags'], 'cohort': event['cohort'], 'url': pin['url'], 'sha256': pin['sha256'], 'source_status': event['official_status'], 'page': ''})
    if len(events) != 65:
        raise ValueError('Official NRW 10 pp frame differs from 65')
    return events, source_manifest


def active_frame(records):
    nrw, manifest = official_nrw_frame()
    other = [dict(r, cohort=('Niedersachsen 2021' if r['state'] == '03' else 'Brandenburg ' + r['decisive_date'][:4])) for r in records if r['absolute_margin_pp'] <= 10 and ((r['state'] == '03' and r['decisive_date'][:4] == '2021') or (r['state'] == '12' and r['decisive_date'][:4] in ('2024', '2025')))]
    return sorted(nrw + other, key=lambda e: (e['cohort'], e['decisive_date'], e['ags'])), manifest


def verify_other(events, acquire):
    ni_root = Path('data/raw/national-scale-expansion-2026-10-11')
    ni_pins = json.loads((ni_root / 'official-retrieval.json').read_text())['sources']
    pages = {}
    for pin in ni_pins:
        path = Path(pin['artifact']); check_pin(pin, path)
        text = subprocess.run(['pdftotext', '-layout', str(path), '-'], check=True, capture_output=True, text=True).stdout
        # Explicit permitted city-chief label; no gender inference from it.
        pages[pin['round']] = text.replace('Oberbürgermeister/Oberbürgermeisterin', 'Bürgermeister/Bürgermeisterin').split('\f')
    bb_old = json.loads((BASE / 'official-source-retrieval.json').read_text())
    cache = RAW / 'bb-official-retrieval.json'
    bb_new = json.loads(cache.read_text()) if cache.exists() else {}
    sources = []
    for event in events:
        if event['state'] == '05':
            continue
        try:
            if event['state'] == '03':
                page = validate_page(event, pages[event['round']])
                pin = next(p for p in ni_pins if p['round'] == event['round'])
                status = 'state_transmitted_provisional_return_numbers_verified'
            else:
                key = event['ags'] + '-' + event['decisive_date'][:4]
                source_key = key + '-linked' if event['ags'] == '12069604' else key
                source_root = BASE if source_key in bb_old else RAW
                pin = bb_old.get(source_key) or bb_new.get(source_key)
                if pin is None and acquire:
                    url = official_url(event)
                    with urlopen(url, timeout=45) as response:
                        raw = response.read(5*1024**2 + 1)
                        if response.status != 200 or len(raw) > 5*1024**2 or b'<html' not in raw.lower():
                            raise ValueError('Invalid bounded official response')
                        pin = {'url': url, 'final_url': response.url, 'file': 'bb-' + key + '.html', 'sha256': digest(raw), 'bytes': len(raw), 'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
                    (RAW / pin['file']).write_bytes(raw)
                    bb_new[source_key] = pin
                    cache.write_text(json.dumps(bb_new, indent=2) + '\n')
                if pin is None:
                    raise ValueError('Official source not acquired')
                validate_official(check_pin(pin, source_root / pin['file']), event)
                page = ''
                status = 'official_committee_identities_votes_day_winner_verified'
            event['official_status'] = status
            sources.append({'ags': event['ags'], 'cohort': event['cohort'], 'url': pin['url'], 'sha256': pin['sha256'], 'source_status': status, 'page': page})
        except (ValueError, OSError) as error:
            event['official_status'] = 'unresolved:' + str(error)
            sources.append({'ags': event['ags'], 'cohort': event['cohort'], 'url': '', 'sha256': '', 'source_status': event['official_status'], 'page': ''})
    return sources


def monthly_sources(acquire):
    root = RAW / 'national-csv'; root.mkdir(parents=True, exist_ok=True)
    path = root / 'retrieval.json'
    pins = json.loads(path.read_text())['exports'] if path.exists() else []
    by_period = {p['period']: p for p in pins}
    used = sum(p['bytes'] for p in pins)
    for month in range(4, 13):
        period = '2025-' + str(month).zfill(2)
        if period in by_period or not acquire:
            continue
        allowance = min(32*1024**2, NEW_BUDGET - used, COMBINED_BUDGET - PRIOR_PROCUREMENT_BYTES - used)
        if allowance <= 0:
            print('Stopped at resource budget before ' + period, flush=True); break
        url = export_url(period, 'csv')
        with urlopen(url, timeout=60) as response:
            raw = response.read(allowance + 1)
            if len(raw) > allowance:
                print('Stopped: source exceeds remaining budget: ' + period, flush=True); break
            if response.status != 200 or response.headers.get('x-amzn-waf-action') == 'challenge':
                raise ValueError('Protected or unsuccessful export')
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                if len(archive.namelist()) != len(set(archive.namelist())) or sum(i.file_size for i in archive.infolist()) > 1024**3 or archive.testzip():
                    raise ValueError('Invalid or oversized ZIP')
            pin = {'period': period, 'url': url, 'final_url': response.url, 'file': period + '-csv.zip', 'bytes': len(raw), 'sha256': digest(raw), 'retrieved_at_utc': datetime.now(timezone.utc).isoformat()}
        (root / pin['file']).write_bytes(raw)
        pins.append(pin); by_period[period] = pin; used += len(raw)
        path.write_text(json.dumps({'exports': pins}, indent=2) + '\n')
        print('Acquired ' + period + ': ' + str(len(raw)) + ' bytes', flush=True)
    if used > NEW_BUDGET or PRIOR_PROCUREMENT_BYTES + used > COMBINED_BUDGET:
        raise ValueError('Resource budget exceeded')
    prior = json.loads((BASE / 'national-csv/retrieval.json').read_text())['exports']
    return [(BASE / 'national-csv', p) for p in prior] + [(root, p) for p in pins]


def first_metadata_occurrence(seen, key, row, buyers):
    payload = {'notice': row, 'buyers': sorted(buyers, key=lambda b: json.dumps(b, sort_keys=True))}
    fingerprint = digest(json.dumps(payload, sort_keys=True).encode())
    if key in seen:
        if seen[key] != fingerprint:
            raise ValueError('Conflicting duplicate notice/version; review before discovery continues')
        return False
    seen[key] = fingerprint
    return True


def discovery(events, sources):
    windows = {e['cohort']: cohort_window(e['cohort']) for e in events}
    calls, outside, seen, coverage = [], [], {}, defaultdict(set)
    duplicates = 0
    types = Counter()
    for root, pin in sorted(sources, key=lambda rp: rp[1]['period']):
        relevant = events
        if not relevant:
            continue
        mapping = niedersachsen_aliases(relevant)
        if any(e['ags'] == '12065332' for e in relevant):
            mapping['stadt velten - die bürgermeisterin'].add('12065332')
        by_ags = {e['ags']: e for e in relevant}
        for cohort in {e['cohort'] for e in relevant}:
            coverage[cohort].add(pin['period'])
        with verified_archive(root, pin) as archive:
            buyers = defaultdict(list)
            for row in csv_rows(archive, 'organisation.csv'):
                if row['organisationRole'] == 'buyer': buyers[notice_key(row)].append(row)
            for row in csv_rows(archive, 'notice.csv'):
                key = notice_key(row)
                if not first_metadata_occurrence(seen, key, row, buyers.get(key, [])):
                    duplicates += 1
                    continue
                ags, reason = municipal_match(buyers.get(key, []), mapping)
                if not ags: continue
                event = by_ags[ags]; start, end, label = windows[event['cohort']]
                day = national_day(row['publicationDate'])
                if not start <= day <= end:
                    outside.append({'cohort':event['cohort'],'ags':ags,'national_notice_identifier':key[0],'version':key[1],'notice_type':row['noticeType'],'publication_day_berlin':day,'export_period':pin['period'],'disposition':'source_publication_day_outside_fixed_window','source_export_sha256':pin['sha256']})
                    continue
                types[(event['cohort'], row['noticeType'])] += 1
                if row['noticeType'] != 'cn-standard': continue
                target_end = followup_end(day)
                calls.append({'cohort': event['cohort'], 'ags': ags, 'municipality': event['municipality'], 'margin_stratum': band(event['absolute_margin_pp']), 'within_5pp': event['absolute_margin_pp'] <= 5, 'national_notice_identifier': key[0], 'version': key[1], 'publication_day_berlin': day, 'procedure_identifier_source': row['procedureIdentifier'], 'buyer_name_source': buyers[key][0]['organisationName'], 'metadata_followup_target_end': target_end.isoformat(), 'metadata_followup_target_mature_at_cutoff': target_end <= SOURCE_CUTOFF, 'original_call_root_verified': False, 'supported_tender_count_outcome': False, 'source_export_file': pin['file'], 'source_export_sha256': pin['sha256']})
        print('Replayed ' + pin['period'], flush=True)
    return calls, outside, coverage, len(seen), duplicates, types


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--acquire', action='store_true'); args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = json.loads((RAW / 'protocol-before-discovery.json').read_text()); check_pin(protocol, protocol['artifact'])
    addendum = json.loads((RAW / 'calendar-addendum-before-replay.json').read_text()); check_pin(addendum, addendum['artifact'])
    records = load_frame()[0]
    national = sorted([r for r in records if r['absolute_margin_pp'] <= 10], key=lambda r: (r['state'], r['decisive_date'], r['ags']))
    repeat_counts = Counter(r['ags'] for r in national)
    national_rows = [{k:r[k] for k in ('state','ags','municipality','decisive_date','round','valid_votes','absolute_margin_pp','both_names_available')} | {'margin_stratum':band(r['absolute_margin_pp']), 'within_2pp':r['absolute_margin_pp']<=2,'within_5pp':r['absolute_margin_pp']<=5,'elections_for_municipality_in_10pp_screen':repeat_counts[r['ags']],'main_study_eligibility_certified':False} for r in national]
    csv_write(DOC / 'national-10pp-election-inventory.csv', national_rows)
    events, official_manifest = active_frame(records)
    official_manifest += verify_other(events, args.acquire)
    (OUT / 'selected-elections.json').write_text(json.dumps(events, indent=2, ensure_ascii=False) + '\n')
    sources = monthly_sources(args.acquire)
    calls, outside, coverage, inspected, duplicates, types = discovery(events, sources)
    by_event = defaultdict(list)
    for call in calls: by_event[(call['cohort'],call['ags'])].append(call)
    prior = list(csv.DictReader((DOC / 'broader-election-acquisition-frame.csv').open()))
    previous_ids = {(r['cohort'],r['ags']) for r in prior}
    inventory = []
    for e in events:
        cs = by_event[(e['cohort'],e['ags'])]; start,end,label=cohort_window(e['cohort'])
        required={start[:4]+'-'+str(m).zfill(2) for m in range(1,13 if label.startswith('complete') else 4)}
        inventory.append({'cohort':e['cohort'],'ags':e['ags'],'municipality':e['municipality'],'decisive_date':e['decisive_date'],'absolute_margin_pp':e['absolute_margin_pp'],'margin_stratum':band(e['absolute_margin_pp']),'within_2pp':e['absolute_margin_pp']<=2,'within_5pp':e['absolute_margin_pp']<=5,'new_vs_previous_58_event_frame':(e['cohort'],e['ags']) not in previous_ids,'official_source_status':e['official_status'],'call_window_start':start,'call_window_end':end,'window_kind':label,'required_monthly_exports':len(required),'verified_monthly_exports':len(required & coverage[e['cohort']]),'monthly_metadata_coverage_complete':required<=coverage[e['cohort']],'national_standard_call_notices':len(cs),'standard_call_notices_in_Q1':sum(c['publication_day_berlin'][5:7] in ('01','02','03') for c in cs),'standard_call_notices_without_procedure_identifier':sum(not c['procedure_identifier_source'] for c in cs),'distinct_nonmissing_procedure_identifiers':len({c['procedure_identifier_source'] for c in cs if c['procedure_identifier_source']}),'any_nine_month_metadata_followup_immature':any(not c['metadata_followup_target_mature_at_cutoff'] for c in cs),'original_call_roots_verified_in_this_phase':False,'presentation_review_complete_in_this_phase':False,'new_supported_mixed_count_outcome':False,'independent_second_coding':False,'main_study_eligibility_certified':False})
    csv_write(DOC / 'relaxed-acquisition-election-inventory.csv',inventory)
    csv_write(DOC / 'relaxed-acquisition-national-call-discovery.csv',calls)
    csv_write(DOC / 'relaxed-acquisition-outside-window-notices.csv',outside)
    csv_write(DOC / 'relaxed-acquisition-official-source-manifest.csv',official_manifest)
    matrix=[]
    for scope,rs in [('National GERDA 2018–2025',national)] + [(cohort,[e for e in events if e['cohort']==cohort]) for cohort in sorted({e['cohort'] for e in events})]:
        for h in (2,5,10):
            es=[e for e in rs if e['absolute_margin_pp']<=h]
            matrix.append({'scope':scope,'cumulative_width_pp':h,'election_events':len(es),'distinct_municipalities':len({e['ags'] for e in es}),'both_finalist_names_available':sum(e['both_names_available'] for e in es),'certified_main_study_elections':0})
    csv_write(DOC / 'bandwidth-expansion-nested-counts.csv',matrix)
    gains=[]
    for cohort in sorted({e['cohort'] for e in events}):
        for h in (2,5,10):
            es=[e for e in events if e['cohort']==cohort and e['absolute_margin_pp']<=h]
            ids={e['ags'] for e in es}
            for window in (('Q1','calendar_year') if cohort in ('Brandenburg 2024','Niedersachsen 2021') else ('Q1',)):
                cs=[c for c in calls if c['cohort']==cohort and c['ags'] in ids and (window=='calendar_year' or c['publication_day_berlin'][5:7] in ('01','02','03'))]
                gains.append({'cohort':cohort,'cumulative_width_pp':h,'metadata_window':window,'election_events':len(es),'events_with_standard_call_metadata':len({c['ags'] for c in cs}),'standard_call_notices':len(cs),'calls_missing_procedure_identifier':sum(not c['procedure_identifier_source'] for c in cs),'distinct_nonmissing_procedure_identifiers':len({c['procedure_identifier_source'] for c in cs if c['procedure_identifier_source']}),'original_call_roots_verified':False,'certified_main_study_elections':0})
    csv_write(DOC / 'parameter-gain-decomposition.csv',gains)
    cohorts=[]
    for cohort in sorted({e['cohort'] for e in events}):
        es=[e for e in inventory if e['cohort']==cohort]; cs=[c for c in calls if c['cohort']==cohort]
        cohorts.append({'cohort':cohort,'elections':len(es),'events_with_standard_call_metadata':sum(bool(e['national_standard_call_notices']) for e in es),'within_5pp_events_with_standard_calls':sum(e['within_5pp'] and bool(e['national_standard_call_notices']) for e in es),'new_5_to_10pp_events_with_standard_calls':sum(not e['within_5pp'] and bool(e['national_standard_call_notices']) for e in es),'events_with_calls_beyond_Q1':sum(e['national_standard_call_notices']>e['standard_call_notices_in_Q1'] for e in es),'events_without_Q1_calls_but_with_annual_calls':sum(e['standard_call_notices_in_Q1']==0 and e['national_standard_call_notices']>0 for e in es),'standard_call_notices':len(cs),'calls_missing_procedure_identifier':sum(not c['procedure_identifier_source'] for c in cs),'monthly_metadata_coverage_complete':all(e['monthly_metadata_coverage_complete'] for e in es),'target_followup_immature_notices':sum(not c['metadata_followup_target_mature_at_cutoff'] for c in cs)})
    summary={'checked_on':'2026-10-11','protocol_sha256':protocol['sha256'],'calendar_addendum_sha256':addendum['sha256'],'matched_notice_records_outside_window':len(outside),'acquisition_ceiling_absolute_gap_pp':10,'causal_rdd_bandwidth_adopted':False,'national_election_events_10pp':len(national),'national_distinct_municipalities_10pp':len(repeat_counts),'national_both_names_available_10pp':sum(e['both_names_available'] for e in national),'national_repeated_municipalities':sum(n>1 for n in repeat_counts.values()),'previous_active_elections':len(prior),'expanded_active_elections':len(events),'expanded_active_distinct_municipalities':len({e['ags'] for e in events}),'added_active_elections':sum(e['new_vs_previous_58_event_frame'] for e in inventory),'official_source_checks_supported':sum(not e['official_source_status'].startswith('unresolved') for e in inventory),'national_notice_rows_inspected':inspected+duplicates,'unique_national_notice_versions':inspected,'identical_duplicate_export_rows_collapsed':duplicates,'standard_call_notices':len(calls),'active_events_with_standard_calls':sum(bool(e['national_standard_call_notices']) for e in inventory),'cohorts':cohorts,'notice_type_counts':[{'cohort':c,'type':t,'count':n} for (c,t),n in sorted(types.items())],'new_procurement_bytes':sum(p['bytes'] for root,p in sources if root==RAW/'national-csv'),'combined_procurement_bytes':PRIOR_PROCUREMENT_BYTES+sum(p['bytes'] for root,p in sources if root==RAW/'national-csv'),'new_supported_mixed_count_elections':0,'previous_supported_mixed_count_elections':4,'certified_main_study_elections':0,'effects_estimated':False,'cohorts_pooled':False,'pages_deployed':False,'warning':'Acquisition events and notice metadata only. Missing coverage is not zero procurement; wider bands are not an RDD justification; nine-month follow-up is prospective and immature young-cohort calls remain censored.'}
    (DOC / 'bandwidth-window-expansion-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (DOC / 'bandwidth-window-export-manifest.json').write_text(json.dumps({'exports':[p for _,p in sources]},indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)


if __name__=='__main__': main()
