"""Prepare a local portable reviewer folder, without contacting or uploading.

Public output contains aggregate readiness only. Originals, names, case forms
and the first-coder key remain local. This is preparation, not second coding.
"""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKETS = ROOT/'data/interim/nrw-independent-review'
DEST = ROOT/'outputs/independent-review-handoff-2026-10-10'
TOP = {'case_id', 'measurement_codebook', 'municipality_for_identity', 'target_event_year',
       'candidates', 'original_sources', 'blinding_limit'}
PERSON = {'slot', 'official_candidate_name'}
SOURCE = {'source_id', 'source_url', 'sha256', 'local_file', 'retrieved_at_utc'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_packet(packet, root):
    require(set(packet) == TOP, 'Unexpected packet fields; inspect possible label leakage')
    require(packet['target_event_year'] == 2020, 'Target event changed')
    require(len(packet['candidates']) == 2 and {p['slot'] for p in packet['candidates']} == {'A', 'B'},
            'Candidate slots differ')
    require(all(set(p) == PERSON for p in packet['candidates']), 'Unexpected candidate fields')
    for source in packet['original_sources']:
        require(set(source) == SOURCE, 'Unexpected source fields')
        path = (root/source['local_file']).resolve()
        require(path.is_relative_to((root/'data/raw').resolve()), 'Source outside original-data directory')
        require(not source['source_id'].startswith('nrw-result-'), 'Official vote file in reviewer packet')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'], 'Reviewer original hash differs')


def prepare():
    require(not DEST.exists(), 'Handoff already exists; preserve it rather than overwrite')
    packets = [json.loads(p.read_text()) for p in sorted(PACKETS.glob('R*.json'))]
    require(len(packets) == len({p['case_id'] for p in packets}) == 28, 'Expected 28 distinct packets')
    for packet in packets:
        validate_packet(packet, ROOT)
    with (PACKETS/'second-coder-form.csv').open(newline='') as handle:
        forms = list(csv.DictReader(handle))
    expected = {(p['case_id'], c['slot']) for p in packets for c in p['candidates']}
    require(len(forms) == 56 and {(r['case_id'], r['candidate_slot']) for r in forms} == expected,
            'Forms do not cover every candidate exactly once')
    require(all(not v for row in forms for k, v in row.items() if k not in ('case_id', 'candidate_slot')),
            'Forms contain prior/completed coding; preserve and inspect')
    require(not (PACKETS/'first-coder-key.csv').exists(), 'First-coder key in reviewer directory')
    DEST.mkdir(parents=True)
    (DEST/'cases').mkdir()
    (DEST/'originals').mkdir()
    copied = {}
    for packet in packets:
        portable = dict(packet, measurement_codebook='measurement-codebook.md')
        portable['original_sources'] = []
        for source in packet['original_sources']:
            original = ROOT/source['local_file']
            # Content-addressed filenames omit the first search's naming cues.
            relative = 'originals/'+source['sha256']+original.suffix
            if relative not in copied:
                shutil.copyfile(original, DEST/relative)
                copied[relative] = source['sha256']
            portable['original_sources'].append(dict(source, local_file=relative))
        (DEST/'cases'/f"{packet['case_id']}.json").write_text(json.dumps(portable, indent=2, ensure_ascii=False)+'\n')
    shutil.copyfile(PACKETS/'second-coder-form.csv', DEST/'second-coder-form.csv')
    shutil.copyfile(ROOT/'docs/feasibility/candidate-exposure-codebook.md', DEST/'measurement-codebook.md')
    (DEST/'START-HERE.md').write_text('''# Independent candidate review — local handoff

Use measurement-codebook.md, cases/ and the pinned originals/ to complete both
slots in second-coder-form.csv. Paths in case files are relative to this folder.
Code historical public presentation, identity, authorship and 2020 linkage;
names, photographs and predicted labels do not establish presentation.

Record reviewer identity, UTC date, source ID, exact locator/page and uncertainty.
For missing evidence, allow at most ten minutes of initial search per candidate,
record actual effort/failed routes and retain unresolved cases. Do not silently
relax the evidence rules. Save the initial completed form before reconciliation.

Do not consult the public report, first-coder records, votes or key before coding.
Disclose prior exposure. Original publications and municipal identity can reveal
office or results: full blinding is not guaranteed. Sources reflect an earlier
search and are not a complete documentation census. No agreement rate or review
completion may be reported until a separate reviewer actually completes coding.

The first-coder key is deliberately excluded. Do not upload or forward this
folder automatically. Source rights and personal-data handling still apply.
''')
    files = sorted(p for p in DEST.rglob('*') if p.is_file())
    require(not any('key' in p.name for p in files), 'Key unexpectedly included')
    manifest = [dict(artifact=str(p.relative_to(DEST)), bytes=p.stat().st_size,
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]
    (DEST/'handoff-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    result = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(), evidence_cutoff='2026-10-05',
                  prepared_pairs=len(packets), blank_candidate_forms=len(forms),
                  unique_original_files=len(copied), original_file_hashes_verified=True,
                  portable_source_paths=True, packet_schema_excludes_prior_labels=True,
                  first_coder_key_included=False, independent_reviewer_assigned=False,
                  independent_second_coding_completed=False, handoff_sent=False,
                  original_sources_uploaded=False, source_selection_and_blinding_limits_remain=True,
                  local_manifest_sha256=hashlib.sha256((DEST/'handoff-manifest.json').read_bytes()).hexdigest())
    (ROOT/'docs/feasibility/reviewer-handoff-readiness.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    prepare()
