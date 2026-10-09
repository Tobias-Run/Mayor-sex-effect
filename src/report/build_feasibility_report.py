"""Build the English feasibility report using pinned public artifacts only.

No network, raw person data, original-source acquisition or effect estimation.
Default: reconciled facts, Markdown and standalone SVG/PDF/PNG figures.
--pdf additionally requires pandoc and xelatex. --facts-only skips figures/PDF.
"""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/feasibility'
MAN = ROOT / 'manuscript'
FIG = MAN / 'figures'
OUT = ROOT / 'outputs/feasibility-report'
PIN_FILE = MAN / 'report-inputs.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def csv_rows(path):
    with Path(path).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def verify_inputs(root=ROOT, manifest=None):
    manifest = manifest or json.loads(PIN_FILE.read_text())
    seen = set()
    for entry in manifest['inputs']:
        name = entry['artifact']
        require(name not in seen, 'Duplicate report input')
        seen.add(name)
        path = (root / name).resolve()
        require(path.is_relative_to(root.resolve()), 'Input escapes repository')
        data = path.read_bytes()
        require(len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256'],
                'Pinned public report input changed: ' + name)
    return manifest


def numeric_map(rows, key='metric', value='value'):
    result = {}
    for row in rows:
        name = row[key]
        require(name not in result, 'Ambiguous aggregate metric: ' + name)
        result[name] = row[value]
    return result


def table(rows, headers):
    """Render authored/generated cells; fail on accidental table delimiters."""
    all_rows = [headers] + rows
    require(all(len(r) == len(headers) for r in rows), 'Ragged report table')
    require(all('|' not in str(v) and '\n' not in str(v) for row in all_rows for v in row),
            'Invalid report table cell')
    lines = ['| ' + ' | '.join(map(str, headers)) + ' |',
             '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines.extend('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)
    return '\n'.join(lines)


def find_one(rows, **criteria):
    matches = [r for r in rows if all(str(r[k]) == str(v) for k,v in criteria.items())]
    require(len(matches) == 1, 'Missing or duplicated benchmark row: ' + str(criteria))
    return matches[0]


def reconcile(nrw, close, early, buyer, scope, bav, bavrows, bands, selection):
    """Cross-artifact accounting checks; no hard-coded desired sample yield."""
    n = {k:int(v) for k,v in nrw.items() if str(v).isdigit()}
    require(n['official_elections_held'] + n['official_no_election_entries'] == n['municipal_universe_entries'],
            'NRW universe/held/no-election accounting differs')
    require(n['details_validated'] == n['official_elections_held'], 'NRW details incomplete')
    require(n['two_candidate_decisive_pairs'] <= n['official_elections_held'], 'Too many decisive pairs')
    require(len(close) == len({r['ags'] for r in close}) == n['all_pair_margin_counts_10'],
            'NRW close-review election counts differ')
    require(Counter(r['pair_status'] for r in close) == early['all_55_pair_counts'], 'NRW pair dispositions disagree')
    mixed = [r for r in close if r['pair_status'] == 'mixed_public_presentation']
    linked = [r for r in mixed if int(r['candidate_window_called_dated_count_units']) > 0]
    require(len(mixed) == early['confirmed_mixed_pairs'], 'NRW mixed-pair total differs')
    require(len(linked) == early['candidate_window_linked_mixed_pairs'], 'NRW candidate-window intersection differs')
    require(sum(int(r['candidate_window_called_dated_count_units']) for r in linked) == early['candidate_window_observed_units'],
            'NRW candidate-window units differ')
    require(sum(r['female_presented_winner'] == 'true' for r in linked) == early['candidate_window_female_wins'],
            'NRW cutoff-side accounting differs')
    require(sum(int(r['pilot_dated_count_units']) for r in close) == int(scope['observed_dated_total_units']),
            'NRW pilot result-unit totals differ')
    units = int(scope['observed_dated_total_units'])
    codes = json.loads(scope['observed_unit_procedure_code_counts'])
    timing = json.loads(scope['observed_unit_timing_dispositions'])
    require(sum(codes.values()) == sum(timing.values()) == units, 'Procedure/timing strata do not partition units')
    require(sum(int(r['retained_pilot_result_notices']) for r in close) == int(buyer['combined_retained_result_notices']),
            'NRW retained-notice totals differ')
    require(len(bavrows) == len({r['ags'] for r in bavrows}) == bav['queried_pairs'], 'Bavaria queried elections differ')
    total = sum(int(r['provisional_municipal_result_notices']) for r in bavrows)
    require(total == bav['provisional_municipal_notices'], 'Bavaria notice intersection differs')
    require(total + sum(bav['exclusions'].values()) == bav['query_notice_count'], 'Bavaria query attrition differs')
    require(sum(int(r['provisional_municipal_result_notices']) > 0 for r in bavrows) == bav['municipalities_with_provisional_results'],
            'Bavaria result-presence municipalities differ')
    require(sum(int(r['indexed_single_lot_total_tender_counts']) for r in bavrows) == bav['indexed_single_lot_total_tender_counts'],
            'Bavaria indexed total counts differ')
    require(sum(int(r['indexed_single_lot_total_tender_counts']) > 0 for r in bavrows) == bav['municipalities_with_indexed_total_tender_counts'],
            'Bavaria indexed-count municipalities differ')
    for row in bands:
        subset = [r for r in bavrows if Decimal(r['absolute_margin_pp']) <= Decimal(row['cutoff_pp'])]
        require(len(subset) == int(row['named_general_2020_pairs']), 'Bavaria margin-band accounting differs')
        require(sum(int(r['provisional_municipal_result_notices']) > 0 for r in subset) == int(row['pairs_with_provisional_result_notices']),
                'Bavaria margin-band result presence differs')
    for row in selection:
        require(int(row['supported_candidates']) + int(row['unresolved_candidates']) == int(row['candidate_records']),
                'Candidate evidence support denominator differs')
    require(early['certified_main_study_elections'] == bav['main_study_elections_certified'] == 0,
            'Main eligibility changed; reconsider report claims')
    require(not early['independent_second_coding_completed'] and not bav['independent_coding_completed'],
            'Independent-review status changed; revise report')
    require(not early['causal_effects_estimated'] and not bav['causal_effects_estimated'], 'Effect-status changed')
    return n, mixed, linked, units, codes, timing


def collect_facts():
    nrw = numeric_map(csv_rows(DOC/'nrw-election-register-summary.csv'), value='count')
    close = csv_rows(DOC/'nrw-early-linkage-matrix.csv')
    closecp = json.loads((DOC/'nrw-close-election-checkpoint.json').read_text())
    early = json.loads((DOC/'nrw-early-feasibility-checkpoint.json').read_text())
    buyer_rows = [r for r in csv_rows(DOC/'nrw-buyer-and-phase-summary.csv') if r['stage']=='buyer_scope']
    buyer = numeric_map(buyer_rows)
    scope = numeric_map(csv_rows(DOC/'nrw-procedure-scope-summary.csv'))
    bav = json.loads((DOC/'bavaria-bounded-checkpoint.json').read_text())
    bavrows = csv_rows(DOC/'bavaria-bounded-linkage-matrix.csv')
    bands = csv_rows(DOC/'bavaria-bounded-band-summary.csv')
    selection = csv_rows(DOC/'nrw-early-selection-audit.csv')
    n,mixed,linked,units,codes,timing = reconcile(nrw,close,early,buyer,scope,bav,bavrows,bands,selection)
    for cutoff in (1,2,5,10):
        rows = [r for r in close if Decimal(r['absolute_margin_pp']) <= cutoff]
        require(len(rows) == closecp['inclusive_margin_counts'][str(cutoff)]['pairs'], 'Close checkpoint band differs')
        require(dict(Counter(r['pair_status'] for r in rows)) == closecp['inclusive_margin_counts'][str(cutoff)]['pair_statuses'],
                'Close checkpoint band status differs')
    benchmarks = csv_rows(DOC/'nrw-early-precision-benchmarks.csv')
    pooled = csv_rows(DOC/'bavaria-nrw-conditional-precision.csv')
    fact = dict(nrw_elections=n['official_elections_held'],nrw_candidates=n['official_candidate_records'],
                nrw_universe=n['municipal_universe_entries'],nrw_no_election=n['official_no_election_entries'],
                nrw_county_exclusions=n['excluded_county_office_entries'],nrw_structural=n['two_candidate_decisive_pairs'],
                nrw_reviewed=len(close),nrw_mixed=len(mixed),nrw_same=early['all_55_pair_counts']['same_public_presentation'],
                nrw_unknown=early['all_55_pair_counts']['unresolved'],nrw_priority_pairs=closecp['first_15']['pairs'],
                nrw_priority_mixed=closecp['first_15']['pair_statuses']['mixed_public_presentation'],
                nrw_priority_same=closecp['first_15']['pair_statuses']['same_public_presentation'],
                nrw_priority_unknown=closecp['first_15']['pair_statuses']['unresolved'],
                nrw_priority_wins=closecp['first_15']['female_presented_wins'],nrw_priority_losses=closecp['first_15']['female_presented_losses'],
                nrw_mixed_wins=closecp['all_55']['female_presented_wins'],nrw_mixed_losses=closecp['all_55']['female_presented_losses'],
                nrw_linked=len(linked),nrw_linked_units=early['candidate_window_observed_units'],
                nrw_linked_wins=early['candidate_window_female_wins'],nrw_linked_losses=early['candidate_window_female_losses'],
                nrw_any_linked=early['confirmed_mixed_pairs_with_any_pilot_dated_count'],
                nrw_pilot_units=units,nrw_pilot_elections=sum(int(r['pilot_dated_count_units'])>0 for r in close),
                nrw_retained_notices=int(buyer['combined_retained_result_notices']),nrw_scope_pending=int(buyer['remaining_scope_cases']),
                nrw_called_chronology=timing['documented_competition_chronology_supported'],
                nrw_timing_pending=timing['competition_identity_or_date_review_pending'],
                nrw_no_call=timing['no_prior_call_procedure_requires_separate_timing_rule'],
                nrw_open=codes['open'],nrw_restricted=codes['restricted'],nrw_neg_called=codes['neg-w-call'],nrw_neg_no_call=codes['neg-wo-call'],
                reviewer_packets=early['independent_review_packet']['prepared_pairs'],
                reviewer_candidates=early['independent_review_packet']['prepared_candidates'],
                bavaria_general=bav['general_2020_structural_pairs'],bavaria_calendar_2020=bav['calendar_2020_structural_pairs'],
                bavaria_named=bav['named_pairs'],bavaria_queried=bav['queried_pairs'],bavaria_query_notices=bav['query_notice_count'],
                bavaria_notices=bav['provisional_municipal_notices'],bavaria_result_municipalities=bav['municipalities_with_provisional_results'],
                bavaria_indexed_counts=bav['indexed_single_lot_total_tender_counts'],
                bavaria_indexed_municipalities=bav['municipalities_with_indexed_total_tender_counts'],
                bavaria_mixed=sum(r['pair_status']=='mixed_official_titles' for r in bavrows),
                bavaria_mixed_wins=sum(r['pair_status']=='mixed_official_titles' and r['female_presented_winner']=='true' for r in bavrows),
                bavaria_mixed_losses=sum(r['pair_status']=='mixed_official_titles' and r['female_presented_winner']=='false' for r in bavrows),
                certified_main_elections=0,causal_effects_estimated=False,independent_review_complete=False,
                current_register=bav['register_source_check'])
    fact['bavaria_extended'] = int(next(r['value'] for r in csv_rows(DOC/'bavaria-register-summary.csv')
                                        if r['window']=='GERDA_2020_2024' and r['metric']=='screened_events'))
    fact['frozen_artifact_count'] = len(csv_rows(DOC/'baseline-source-hashes.csv'))
    fact['federal_monthly_archives'] = len(json.loads((DOC/'federal-procurement-export-manifest.json').read_text()))
    registry=bav['register_source_check']
    fact.update(gerda_bavaria_rows=registry['current_bavaria_rows'],
                gerda_historical_rows=registry['historical_2020_2024_rows'],
                gerda_2026_labels=registry['gender_label_year_counts']['2026'],
                current_officeholder_rows=registry['current_municipal_officeholders'],
                current_2026_officeholder_rows=registry['officeholder_election_years']['2026'],
                bavaria_mixed_notices=sum(int(r['provisional_municipal_result_notices']) for r in bavrows
                                         if r['pair_status']=='mixed_official_titles'),
                bavaria_query_exclusions=sum(bav['exclusions'].values()),
                bavaria_2pp_named=int(find_one(bands,cutoff_pp=2)['named_general_2020_pairs']),
                bavaria_2pp_structural=int(find_one(bands,cutoff_pp=2)['statewide_general_2020_structural_pairs']),
                review_classified=early['independent_review_packet']['classified_pairs'],
                review_unknown=early['independent_review_packet']['unresolved_audit_pairs'])
    for group in ('winner','loser'):
        row=find_one(selection,dimension='candidate_election_result',group=group)
        fact[f'{group}_support_count']=int(row['supported_candidates'])
        fact[f'{group}_support_rate_pct']=100*float(row['support_rate'])
    for alpha in (.05,.025):
        suffix = '05' if alpha==.05 else '025'
        for short,scenario in [('confirmed4','confirmed_within_2pp'),('optimistic6','optimistic_all_unknowns_mixed_within_2pp')]:
            fact[f'mde_{short}_{suffix}'] = float(find_one(benchmarks,scenario=scenario,per_test_alpha=alpha)['gaussian_pooled_t_mde_sd'])
        row = find_one(pooled,cutoff_pp=2,bavaria_scope='all_named',alpha=alpha)
        fact[f'mde_optimistic12_{suffix}'] = float(row['gaussian_pooled_t_mde_sd'])
        fact['pooled_close_ceiling'] = int(row['pooled_conditional_max'])
    fact['pooled_wide_ceiling']=int(find_one(pooled,cutoff_pp=10,bavaria_scope='all_named',alpha=.05)['pooled_conditional_max'])
    fact['nrw_band_table'] = table([[c,closecp['inclusive_margin_counts'][str(c)]['pairs'],
        closecp['inclusive_margin_counts'][str(c)]['pair_statuses'].get('mixed_public_presentation',0),
        closecp['inclusive_margin_counts'][str(c)]['female_presented_wins'],
        closecp['inclusive_margin_counts'][str(c)]['female_presented_losses']] for c in (1,2,5,10)],
        ['Margin at most (pp)','Reviewed pairs','Supported mixed pairs','Female-presented wins','Female-presented losses'])
    fact['bavaria_band_table'] = table([[r['cutoff_pp'],r['statewide_general_2020_structural_pairs'],r['named_general_2020_pairs'],
        r['pairs_with_provisional_result_notices'],r['confirmed_female_wins'],r['confirmed_female_losses']] for r in bands],
        ['Margin at most (pp)','General-2020 structural','Named','Provisional result presence','Supported female wins','Supported female losses'])
    fact['linked_table'] = table([[r['municipality'],int(r['pilot_dated_count_units']),
        int(r['candidate_window_called_dated_count_units']),r['female_presented_winner']] for r in mixed],
        ['Supported mixed-pair municipality','Any pilot dated/count units','Called units in candidate window','Female-presented win'])
    selected = [r for r in selection if r['dimension'] in ('candidate_election_result','absolute_margin_band')]
    fact['selection_table'] = table([[r['dimension'].replace('_',' '),r['group'].replace('_',' '),r['supported_candidates'],
        r['candidate_records'],f"{100*float(r['support_rate']):.1f}%"] for r in selected],
        ['Dimension','Group','Supported candidate records','Candidate denominator','Support rate'])
    scenarios = [('Confirmed NRW ≤2 pp',1,3,fact['mde_confirmed4_05'],fact['mde_confirmed4_025']),
                 ('Conditional NRW maximum ≤2 pp',3,3,fact['mde_optimistic6_05'],fact['mde_optimistic6_025']),
                 ('Conditional NRW + named Bavaria maximum ≤2 pp',6,6,fact['mde_optimistic12_05'],fact['mde_optimistic12_025'])]
    fact['precision_table'] = table([[label,n1,n0,f'{a:.2f}',f'{b:.2f}'] for label,n1,n0,a,b in scenarios],
        ['Scenario','Female wins','Female losses','MDE / SD, alpha .05','MDE / SD, alpha .025'])
    fact['precision_plot_data'] = [dict(scenario=label,female_wins=n1,female_losses=n0,alpha=alpha,
        assumed_municipal_sd_pp=sd,gaussian_t_mde_sd=mde,gaussian_t_mde_pp=mde*sd,
        within_0_to_100pp_range=mde*sd<=100,interpretation='assumed_Gaussian_benchmark_not_RDD_or_effect_estimate')
        for label,n1,n0,a,b in scenarios for alpha,mde in ((.05,a),(.025,b)) for sd in (5,10,20)]
    return fact


def render_template(template, facts):
    used = set()
    def replace(match):
        key, digits = match.groups()
        require(key in facts, 'Unknown report fact: ' + key)
        used.add(key)
        value = facts[key]
        require(isinstance(value,(str,int,float)), 'Non-scalar template fact: ' + key)
        return f'{value:.{digits}f}' if digits else str(value)
    result = re.sub(r'\{\{([a-zA-Z0-9_]+)(?::(\d+))?\}\}',replace,template)
    # Nested LaTeX groups legitimately end in }}; only an opening {{ is
    # reserved for report fields.
    require('{{' not in result, 'Unresolved template field')
    return result, sorted(used)


def save_figure(fig, stem):
    for extension in ('svg','pdf','png'):
        metadata = {'Date': '2026-10-09'} if extension=='svg' else (
            {'CreationDate': datetime(2026,10,9,tzinfo=timezone.utc), 'ModDate': datetime(2026,10,9,tzinfo=timezone.utc)}
            if extension=='pdf' else {})
        fig.savefig(FIG/f'{stem}.{extension}',dpi=180,metadata=metadata)


def figures(f):
    # Writable caches for managed/read-only-home environments; honor overrides.
    for variable, directory in [('MPLCONFIGDIR', OUT/'matplotlib-cache'),
                                ('XDG_CACHE_HOME', OUT/'font-cache')]:
        directory.mkdir(parents=True,exist_ok=True)
        os.environ.setdefault(variable,str(directory))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    matplotlib.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'mayor-feasibility-v0.1','pdf.fonttype':42})
    FIG.mkdir(parents=True,exist_ok=True)
    fig,ax = plt.subplots(figsize=(11.6,8.8));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    fig.subplots_adjust(left=.035,right=.965,top=.96,bottom=.03)
    ax.text(.02,.985,'Available evidence narrows before a main-study sample',fontsize=16,fontweight='bold',va='top')
    ax.text(.02,.938,'Independent elections at each step · source scopes differ between states',color='#46505b',fontsize=10)
    left = [(f['nrw_elections'],'Official scheduled-2020 elections','396 municipal entries; 16 without an election'),
            (f['nrw_structural'],'Decisive two-person pairs','Exact official vote vectors'),
            (f['nrw_reviewed'],'Pairs reviewed within 10 pp','Acquisition band; no bandwidth selected'),
            (f['nrw_mixed'],'Supported mixed-presentation pairs',f"{f['nrw_mixed_wins']} female wins / {f['nrw_mixed_losses']} losses; {f['nrw_any_linked']} with any pilot units"),
            (f['nrw_linked'],'Provisional called-window intersections',f"{f['nrw_linked_wins']} female win / {f['nrw_linked_losses']} losses; {f['nrw_linked_units']} result units"),
            (0,'Certified main-study elections','Reporting, exposure and follow-up gates pending')]
    right = [(f['bavaria_general'],'General-2020 structural decisions',f"{f['bavaria_calendar_2020']} in calendar 2020; {f['bavaria_extended']} in 2020–2024"),
             (f['bavaria_named'],'Named, vote-audited decisions','Larger-municipality report coverage'),
             (f['bavaria_queried'],'Named decisions within 10 pp','All entered the capped TED query'),
             (f['bavaria_result_municipalities'],'Provisional municipal result presence',f"{f['bavaria_notices']} result notices; original calls unverified"),
             (f['bavaria_mixed'],'Supported mixed-title pairs with results',f"{f['bavaria_mixed_wins']} female wins / {f['bavaria_mixed_losses']} losses"),
             (0,'Certified main-study elections','Common-window and measurement gates pending')]
    for x,title,rows in [(.02,'NRW',left),(.515,'Bavaria',right)]:
        ax.text(x,.89,title,fontweight='bold',fontsize=13,color='#183c64')
        for index,(number,label,note) in enumerate(rows):
            y=.765-index*.119
            color = '#fcecea' if index==5 else '#edf3f8'
            box=FancyBboxPatch((x,y),.465,.097,boxstyle='round,pad=0.006,rounding_size=0.006',
                              linewidth=.8,edgecolor='#a44940' if index==5 else '#b9c8d7',facecolor=color)
            ax.add_patch(box)
            ax.text(x+.014,y+.053,str(number),fontsize=22,fontweight='bold',color='#9a3b32' if index==5 else '#183c64',va='center')
            ax.text(x+.105,y+.06,label,fontsize=9.8,fontweight='bold',va='center')
            ax.text(x+.105,y+.025,note,fontsize=8.1,color='#46505b',va='center')
            if index<5:
                ax.annotate('',xy=(x+.232,y-.018),xytext=(x+.232,y-.006),
                            arrowprops={'arrowstyle':'->','color':'#798b9d','lw':1.1})
    ax.text(.02,.07,'NRW candidate competition window: 1 Nov 2023–31 Dec 2024. Bavaria query filters result publication,',fontsize=9,color='#46505b')
    ax.text(.02,.044,'1 Nov 2023–30 Sep 2026. The two intersections are not equivalent eligible outcome samples.',fontsize=9,color='#46505b')
    save_figure(fig,'sample-flow');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11.6,6.8),sharey=True)
    fig.subplots_adjust(left=.09,right=.97,top=.78,bottom=.19,wspace=.16)
    palette=['#183c64','#16817b','#c47824']
    names=list(dict.fromkeys(r['scenario'] for r in f['precision_plot_data']))
    for ax,alpha in zip(axes,(.05,.025)):
        ax.axhspan(100,195,color='#f3e4e2',zorder=0)
        ax.axhline(100,color='#a66b65',ls=':',lw=1)
        for i,name in enumerate(names):
            rows=[r for r in f['precision_plot_data'] if r['scenario']==name and r['alpha']==alpha]
            ax.plot([r['assumed_municipal_sd_pp'] for r in rows],[r['gaussian_t_mde_pp'] for r in rows],
                    marker=['o','s','D'][i],lw=2.2,color=palette[i],
                    label=f"{name} ({rows[0]['female_wins']} win{'s' if rows[0]['female_wins']!=1 else ''} / {rows[0]['female_losses']} losses)")
        ax.set_title('Per-test alpha '+str(alpha),fontsize=11)
        ax.set_xlim(4,21);ax.set_ylim(0,195);ax.set_xticks([5,10,20]);ax.set_xlabel('Assumed municipality SD (pp)')
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dbe1e6',linewidth=.6)
        ax.text(5,185,'MDE above the 0–100 pp share range',fontsize=8,color='#7d4d47')
    axes[0].set_ylabel('Minimum detectable change (pp)')
    fig.suptitle('Precision requires assumptions as well as independent elections',x=.09,ha='left',y=.985,fontsize=15,fontweight='bold')
    fig.text(.09,.932,'80% power · Gaussian equal-variance two-group t benchmark · no RDD power or effect estimate',fontsize=10,color='#46505b')
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.08,.906),fontsize=9,frameon=False,ncol=1)
    fig.text(.09,.08,'All scenarios assume usable outcomes; conditional maxima also require favorable unknown resolution and balance.',fontsize=8.5,color='#46505b')
    fig.text(.09,.047,'The SD grid is hypothetical; a bounded-share outcome does not exactly follow the Gaussian model.',fontsize=9,color='#46505b')
    save_figure(fig,'precision-benchmark');plt.close(fig)


def normalize_pdf_identifier(path):
    """Replace XeTeX's temporary-path-derived ID with a content-derived ID.

    Only two fixed-length identifier strings change. PDF offsets, objects,
    text, graphics and all other metadata remain byte-for-byte unchanged.
    """
    data=Path(path).read_bytes()
    matches=list(re.finditer(rb'/ID\s*\[\s*<([a-fA-F0-9]{32})>\s*<([a-fA-F0-9]{32})>\s*\]',data))
    require(len(matches)==1,'Expected one fixed-length PDF identifier pair')
    match=matches[0]
    parts=[];position=0
    for group in (1,2):
        parts.extend([data[position:match.start(group)], b'0'*32])
        position=match.end(group)
    parts.append(data[position:])
    masked=b''.join(parts)
    identifier=hashlib.sha256(masked).hexdigest()[:32].encode('ascii')
    parts=[];position=0
    for group in (1,2):
        parts.extend([data[position:match.start(group)], identifier])
        position=match.end(group)
    parts.append(data[position:])
    normalized=b''.join(parts)
    require(len(normalized)==len(data),'PDF identifier normalization changed offsets')
    Path(path).write_bytes(normalized)


def pdf_export(markdown):
    require(shutil.which('pandoc') and shutil.which('xelatex'), 'PDF export requires pandoc and xelatex')
    OUT.mkdir(parents=True,exist_ok=True)
    text=markdown.replace('(figures/sample-flow.svg)','(figures/sample-flow.pdf)').replace(
        '(figures/precision-benchmark.svg)','(figures/precision-benchmark.pdf)')
    text=re.sub(r'^# [^\n]+\n','',text,count=1,flags=re.MULTILINE)
    text=text.replace('*A Bounded Feasibility Audit in NRW and Bavaria*\n','',1)
    # Repository links in a standalone PDF must remain useful outside checkout.
    def absolute_link(match):
        label,target=match.groups()
        if re.match(r'\w+://',target) or target.startswith('#') or target.startswith('figures/'):
            return match[0]
        path=(MAN/target.split('#')[0]).resolve()
        if not path.is_relative_to(ROOT):return match[0]
        fragment=('#'+target.split('#',1)[1]) if '#' in target else ''
        return '['+label+'](https://github.com/Tobias-Run/Mayor-sex-effect/blob/main/'+str(path.relative_to(ROOT))+fragment+')'
    text=re.sub(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)',absolute_link,text)
    path=OUT/'pandoc-input.md';path.write_text(text)
    environment=dict(os.environ)
    environment['SOURCE_DATE_EPOCH']=str(int(datetime(2026,10,9,tzinfo=timezone.utc).timestamp()))
    subprocess.run(['pandoc',str(path),'--from=gfm+tex_math_dollars+yaml_metadata_block','--pdf-engine=xelatex',
                    '--lua-filter='+str(ROOT/'src/report/pdf-tables.lua'),
                    '--include-in-header='+str(ROOT/'src/report/pdf-layout.tex'),
                    '--pdf-engine-opt=-no-shell-escape','--resource-path='+str(MAN),
                    '-V','papersize:a4','-V','geometry:margin=22mm','-V','fontsize:10pt','-V','mainfont:DejaVu Serif',
                    '-V','sansfont:DejaVu Sans','-V','monofont:DejaVu Sans Mono',
                    '-V','colorlinks:true','-V','urlcolor:blue','--toc','--toc-depth=2',
                    '-o',str(MAN/'feasibility-report.pdf')],cwd=ROOT,env=environment,check=True)
    normalize_pdf_identifier(MAN/'feasibility-report.pdf')


def run(facts_only=False,pdf=False):
    manifest=verify_inputs();facts=collect_facts()
    template=(MAN/'feasibility-report.template.md').read_text()
    markdown,used=render_template(template,facts)
    (MAN/'report-facts.json').write_text(json.dumps(facts,indent=2,ensure_ascii=False)+'\n')
    (MAN/'feasibility-report.md').write_text(markdown)
    if not facts_only:
        figures(facts)
        with (FIG/'precision-data.csv').open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(facts['precision_plot_data'][0]));writer.writeheader();writer.writerows(facts['precision_plot_data'])
        if pdf:pdf_export(markdown)
    verify_inputs()
    outputs=[MAN/'report-facts.json',MAN/'feasibility-report.md']
    if not facts_only:
        outputs += [FIG/f'{stem}.{ext}' for stem in ('sample-flow','precision-benchmark') for ext in ('svg','pdf','png')]
        outputs += [FIG/'precision-data.csv']
        if pdf:outputs += [MAN/'feasibility-report.pdf']
    software={'python':sys.version.split()[0]}
    if not facts_only:
        software.update({name:importlib.metadata.version(name) for name in ('matplotlib','numpy')})
    if pdf:
        for name in ('pandoc','xelatex'):
            software[name]=subprocess.run([name,'--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    checkpoint=dict(report_version=manifest['report_version'],report_date=manifest['report_date'],
        evidence_cutoff=manifest['evidence_cutoff'],evidence_commit=manifest['evidence_commit'],
        checked_at_utc=datetime.now(timezone.utc).isoformat(),pinned_public_inputs_verified=len(manifest['inputs']),
        raw_source_reacquisition=False,software=software,template_fields_resolved=used,
        independent_second_coding_completed=False,report_status='draft_for_review',
        main_study_elections_certified=0,causal_effects_estimated=False,github_pages='deferred',
        outputs=[dict(artifact=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in outputs])
    (MAN/'report-reproduction-checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
    print(json.dumps({k:v for k,v in checkpoint.items() if k not in ('outputs','template_fields_resolved')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--facts-only',action='store_true');parser.add_argument('--pdf',action='store_true')
    args=parser.parse_args()
    require(not(args.facts_only and args.pdf),'--facts-only cannot export a PDF')
    run(args.facts_only,args.pdf)
