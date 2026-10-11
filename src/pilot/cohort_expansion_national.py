"""Call-first national discovery for the fixed ten-election expansion frame.

Includes numeric domestic IDs rather than discarding them as invalid UUIDs.
These records remain metadata discoveries, not deduplicated procedures or
successful competition outcomes. No national publication date is a TED date.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from uuid import UUID
from federal_procurement import csv_rows, verified_archive
from nrw_2025_validation import csv_write
from cohort_expansion import ROOT, OUT, DOC, frame
import bavaria_bounded_route as ted


def national_day(timestamp):
    value = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('National timestamp lacks timezone')
    return value.astimezone(ZoneInfo('Europe/Berlin')).date().isoformat()


def notice_key(row):
    name, version = row['noticeIdentifier'], row['noticeVersion']
    try:
        name = str(UUID(name))
    except ValueError:
        if not name.isdigit():
            raise ValueError('Unknown national notice identifier format')
    if not version.isdigit() or int(version) < 1:
        raise ValueError('Invalid national version')
    return name, int(version)


def municipal_match(buyers, aliases):
    if len(buyers) != 1:
        return None, 'missing_or_multiple_buyer_roles'
    buyer = buyers[0]
    candidates = aliases.get(ted.normal_text(buyer['organisationName']), set())
    if len(candidates) != 1:
        return None, 'unmatched_or_ambiguous_exact_name'
    if buyer['organisationCountryCode'] not in ('', 'DEU'):
        return None, 'country_conflict'
    if buyer['buyerLegalType'] not in ('', 'kommun-beh'):
        return None, 'nonmunicipal_legal_type'
    return next(iter(candidates)), 'provisional_exact_buyer_role_name'


def main():
    addendum = json.loads((ROOT / 'national-discovery-before-acquisition.json').read_text())
    if hashlib.sha256(Path(addendum['artifact']).read_bytes()).hexdigest() != addendum['sha256']:
        raise ValueError('Pre-acquisition discovery addendum changed')
    _, selected, _ = frame()
    export_root = ROOT / 'national-csv'
    pins = json.loads((export_root / 'retrieval.json').read_text())['exports']
    if {p['period'] for p in pins} != {'2025-01', '2025-02', '2025-03', '2026-01', '2026-02', '2026-03'}:
        raise ValueError('Incomplete fixed six-month metadata coverage')
    if sum(p['bytes'] for p in pins) > 256 * 1024 ** 2:
        raise ValueError('National discovery budget exceeded')
    calls, retained, by_ags, seen = [], [], defaultdict(list), set()
    dispositions, types = Counter(), Counter()
    for pin in pins:
        year = int(pin['period'][:4]) - 1
        events = [e for e in selected if e['decisive_date'][:4] == str(year)]
        aliases = ted.aliases(events)
        if year == 2025:
            aliases[ted.normal_text('Stadt Velten - Die Bürgermeisterin')].add('12065332')
        with verified_archive(export_root, pin) as archive:
            buyers = defaultdict(list)
            for row in csv_rows(archive, 'organisation.csv'):
                if row['organisationRole'] == 'buyer':
                    buyers[notice_key(row)].append(row)
            for row in csv_rows(archive, 'notice.csv'):
                key = notice_key(row)
                if key in seen:
                    raise ValueError('Duplicate notice/version across monthly discovery exports')
                seen.add(key)
                ags, reason = municipal_match(buyers.get(key, []), aliases)
                dispositions[reason] += 1
                if not ags:
                    continue
                day = national_day(row['publicationDate'])
                if not str(year + 1) + '-01-01' <= day <= str(year + 1) + '-03-31':
                    raise ValueError('Monthly export contains out-of-quarter municipal record')
                types[row['noticeType']] += 1
                unit = {'ags': ags, 'election_year': year, 'national_notice_identifier': key[0],
                        'national_notice_version': key[1], 'national_notice_type': row['noticeType'],
                        'national_publication_timestamp_source': row['publicationDate'],
                        'national_publication_day_berlin': day,
                        'procedure_identifier_source': row['procedureIdentifier'],
                        'procedure_identifier_available': bool(row['procedureIdentifier']),
                        'buyer_name_source': buyers[key][0]['organisationName'],
                        'buyer_legal_type_source': buyers[key][0]['buyerLegalType'],
                        'metadata_scope_status': reason,
                        'original_xml_verified': False, 'original_call_root_verified': False,
                        'main_study_eligibility_certified': False,
                        'source_export_file': pin['file'], 'source_export_sha256': pin['sha256']}
                retained.append(unit)
                if row['noticeType'] == 'cn-standard':
                    calls.append(unit); by_ags[ags].append(unit)
    csv_write(DOC / 'brandenburg-expansion-national-call-discovery.csv', calls)
    inventory = []
    for event in selected:
        cs = by_ags[event['ags']]
        inventory.append({'ags': event['ags'], 'municipality': event['municipality'],
                          'election_year': event['decisive_date'][:4], 'national_monthly_metadata_coverage_complete': True,
                          'provisional_national_call_notices': len(cs),
                          'call_notices_with_procedure_identifier': sum(c['procedure_identifier_available'] for c in cs),
                          'distinct_nonmissing_procedure_identifiers': len({c['procedure_identifier_source'] for c in cs if c['procedure_identifier_source']}),
                          'original_call_roots_verified': False, 'main_study_eligibility_certified': False})
    csv_write(DOC / 'brandenburg-expansion-national-election-coverage.csv', inventory)
    (OUT / 'national-matched-notices.json').write_text(json.dumps(retained, indent=2, ensure_ascii=False) + '\n')
    (DOC / 'brandenburg-expansion-national-export-manifest.json').write_text(json.dumps({'exports': pins, 'total_bytes': sum(p['bytes'] for p in pins)}, indent=2) + '\n')
    summary = {'checked_on': '2026-10-11', 'selected_elections': len(selected),
               'national_monthly_exports': len(pins), 'additional_compressed_csv_bytes': sum(p['bytes'] for p in pins),
               'national_notice_rows_inspected': len(seen), 'exact_municipal_notice_type_counts': dict(types),
               'provisional_national_call_notices': len(calls),
               'elections_with_provisional_national_calls': sum(bool(by_ags[e['ags']]) for e in selected),
               'calls_missing_procedure_identifier': sum(not c['procedure_identifier_available'] for c in calls),
               'distinct_nonmissing_procedure_identifiers': len({c['procedure_identifier_source'] for c in calls if c['procedure_identifier_source']}),
               'match_dispositions_all_national_notices': dict(dispositions),
               'xml_call_roots_verified': 0, 'certified_main_study_elections': 0,
               'primary_outcome_rates_estimated': False, 'pooled_with_nrw': False,
               'discovery_addendum_sha256': addendum['sha256'],
               'warning': 'Metadata discoveries. Numeric domestic IDs without procedure IDs remain visible; counts are notices, not independent procurements. Zero exact matches is unknown coverage.'}
    (DOC / 'brandenburg-expansion-national-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()
